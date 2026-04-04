from pathlib import Path

from wcwidth import wcswidth

from ...constants import FILE_ICONS
from ...instances.inst_units import HumanBytes, HumanTimestamp
from ...tools.FileOperations import (
    get_file_size,
    get_file_mtime,
)
from .file_node import BaseNode, FileNode, DirNode
from .file_util import to_string


class FileTree:
    def __init__(self, root: DirNode, path: Path):
        self.root = root
        self.path = path

    @classmethod
    def build_from_path(
        cls, root_path: Path
    ):
        """
        从路径构建文件树。

        :param root_path: 根目录路径
        :return: 文件树
        :raises ValueError: 如果路径不是目录
        """
        root_path = Path(root_path)
        if not root_path.is_dir():
            raise ValueError(f"Path {root_path} is not a directory")

        def _scan(node_path: Path, level: int) -> BaseNode:
            if node_path.is_file():
                size = get_file_size(node_path)
                mtime = get_file_mtime(node_path)
                icon = FILE_ICONS.get(node_path.suffix.lower(), FILE_ICONS["default"])
                return FileNode(
                    node_path.name, node_path.suffix, node_path, size, mtime, icon, level
                ) 

            entries = list(node_path.iterdir())
            children = []

            total_size = HumanBytes(0)
            dir_mtime = HumanTimestamp(0)

            for child in entries:
                cnode = _scan(child, level+1)
                children.append(cnode)
                total_size += cnode.size
                dir_mtime = max(dir_mtime, cnode.mtime)

            return DirNode(
                node_path.name,
                node_path,
                total_size,
                dir_mtime,
                level,
                children,
            )

        return cls(_scan(root_path, 0), root_path)

    # 打印树
    def print_tree(self, exclude_names=None, exclude_exts=None, max_depth=3):
        """
        递归打印整棵文件树，目录在前、文件在后。

        :param exclude_names: 要排除的目录名称集合。
        :param max_depth: 最大打印深度。
        :return: None
        :raises ValueError: 如果最大深度小于等于0
        """
        exclude_names = set(exclude_names or [])
        exclude_exts = set(exclude_exts or [])

        def _get_display_name(node: BaseNode, depth: int) -> str:
            if node.is_dir and node.children and depth >= max_depth:
                return node.name + "[已折叠]"
            return node.name

        def _print(node: BaseNode, depth: int, max_name_len: int = 0):
            display_name = _get_display_name(node, depth)
            node.print(name=display_name, max_name_len=max_name_len)

            if node.is_dir and node.children and depth >= max_depth:
                return
            if not node.is_dir or not node.children:
                return

            dirs = []
            files = []
            exclude_dirs = []
            exclude_files = []
            child_names = []

            for child in node.children:
                if child.is_dir and child.name in exclude_names:
                    exclude_dirs.append(child)
                elif child.is_dir:
                    dirs.append(child)
                    child_names.append(_get_display_name(child, depth + 1))
                elif not child.is_dir and child.suffix in exclude_exts:
                    exclude_files.append(child)
                else:
                    files.append(child)
                    child_names.append(_get_display_name(child, depth + 1))
            
            if exclude_dirs:
                child_names.append(f"[{len(exclude_dirs)}项排除的目录]")
            if exclude_files:
                child_names.append(f"[{len(exclude_files)}项排除的文件]")

            child_max_name_len = max((wcswidth(name) for name in child_names), default=0)
            exclude_dirs_node = DirNode(
                f"[{len(exclude_dirs)}项排除的目录]",
                node.node_path,
                HumanBytes(sum(d.size for d in exclude_dirs)),
                HumanTimestamp(max(d.mtime for d in exclude_dirs)),
                depth + 1,
                [],
            ) if exclude_dirs else None
            exclude_files_node = FileNode(
                f"[{len(exclude_files)}项排除的文件]",
                node.node_path,
                HumanBytes(sum(f.size for f in exclude_files)),
                HumanTimestamp(max(f.mtime for f in exclude_files)),
                "📄",
                depth + 1,
            ) if exclude_files else None

            for d in dirs:
                _print(d, depth + 1, child_max_name_len)
            if exclude_dirs_node:
                exclude_dirs_node.print(max_name_len=child_max_name_len)
            for f in files:
                _print(f, depth + 1, child_max_name_len)
            if exclude_files:
                exclude_files_node.print(max_name_len=max_name_len)

        _print(self.root, 0)
