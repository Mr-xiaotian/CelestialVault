from pathlib import Path

from wcwidth import wcswidth

from ...constants import FILE_ICONS
from ...instances.inst_units import HumanBytes, HumanTimestamp
from ...tools.FileOperations import (
    get_file_size,
    get_file_mtime,
)
from .file_node import FileNode, DirNode
from .file_util import to_string


class FileTree:
    def __init__(self, root: FileNode|DirNode, path: Path):
        self.root = root
        self.path = path

    @classmethod
    def build_from_path(
        cls, root_path: Path
    ):
        root_path = Path(root_path)

        def _scan(node_path: Path, level: int) -> FileNode|DirNode:
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
            mtime = HumanTimestamp(0)

            for child in entries:
                if child.is_dir():
                    cnode = _scan(child, level+1)
                else:
                    cnode = _scan(child, level+1)
                children.append(cnode)
                total_size += cnode.size
                mtime = max(mtime, cnode.mtime)

            return DirNode(
                node_path.name,
                node_path,
                total_size,
                mtime,
                "📁",
                level,
                children,
            )

        return cls(_scan(root_path, 0), root_path)

    # 打印树
    def print_tree(self, exclude_names=None, exclude_exts=None, max_depth=3):
        """
        递归打印整棵文件树，目录在前、文件在后。
        """
        exclude_names = set(exclude_names or [])
        exclude_exts = set(exclude_exts or [])

        def _get_display_name(node: FileNode|DirNode, depth: int) -> str:
            if isinstance(node, DirNode) and node.children and depth >= max_depth:
                return node.name + "[已折叠]"
            return node.name

        def _print(node: FileNode|DirNode, depth: int, max_name_len: int = 0):
            display_name = _get_display_name(node, depth)
            if isinstance(node, DirNode) and node.children and depth >= max_depth:
                node.print(name=display_name, max_name_len=max_name_len)
                return

            node.print(name=display_name, max_name_len=max_name_len)
            if isinstance(node, DirNode):
                dirs = [c for c in node.children if isinstance(c, DirNode)]
                files = [c for c in node.children if isinstance(c, FileNode)]
                exclude_dirs = []
                exclude_files = []
                child_names = []

                for d in dirs:
                    if d.name in exclude_names:
                        exclude_dirs.append(d)
                        continue
                    child_names.append(_get_display_name(d, depth + 1))
                if exclude_dirs:
                    child_names.append(f"[{len(exclude_dirs)}项排除的目录]")

                for f in files:
                    if f.suffix in exclude_exts:
                        exclude_files.append(f)
                        continue
                    child_names.append(_get_display_name(f, depth + 1))
                if exclude_files:
                    child_names.append(f"[{len(exclude_files)}项排除的文件]")

                child_max_name_len = max((wcswidth(name) for name in child_names), default=0)

                for d in dirs:
                    if d.name in exclude_names:
                        continue
                    _print(d, depth + 1, child_max_name_len)
                if exclude_dirs:
                    print(to_string(
                        indent="    " * (depth+1),
                        icon="📁",
                        prefix="", 
                        name=f"[{len(exclude_dirs)}项排除的目录]",
                        suffix=f"({HumanBytes(sum(d.size for d in exclude_dirs))})",
                        max_name_len=child_max_name_len,
                    ))
                for f in files:
                    if f.suffix in exclude_exts:
                        continue
                    _print(f, depth + 1, child_max_name_len)
                if exclude_files:
                    print(to_string(
                        indent="    " * (depth+1),
                        icon="📄",
                        prefix="", 
                        name=f"[{len(exclude_files)}项排除的文件]",
                        suffix=f"({HumanBytes(sum(f.size for f in exclude_files))})",
                        max_name_len=child_max_name_len,
                    ))

        _print(self.root, 0)
