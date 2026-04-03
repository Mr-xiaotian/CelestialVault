from pathlib import Path
from wcwidth import wcswidth

from ...constants import FILE_ICONS
from ...instances.inst_units import HumanBytes, HumanTimestamp
from ...tools.FileOperations import (
    get_file_size,
    get_dir_size,
    get_file_mtime,
    get_dir_mtime,
)
from .file_node import FileNode
from .file_diff import FileDiff


class FileTree:
    def __init__(self, root: FileNode, path: Path):
        self.root = root
        self.path = path

    @classmethod
    def build_from_path(
        cls, root_path: Path, exclude_dirs=None, exclude_exts=None, max_depth=3
    ):
        root_path = Path(root_path)
        exclude_dirs = set(exclude_dirs or [])
        exclude_exts = set(ext.lower() for ext in (exclude_exts or []))

        def _scan(node_path: Path, level: int) -> FileNode:
            if not node_path.exists():
                return FileNode(
                    "(空目录)", node_path, True, 0, HumanTimestamp(0), "📁", level
                )

            mtime = (
                get_dir_mtime(node_path)
                if node_path.is_dir()
                else get_file_mtime(node_path)
            )
            if node_path.is_file():
                size = get_file_size(node_path)
                icon = FILE_ICONS.get(node_path.suffix.lower(), FILE_ICONS["default"])
                return FileNode(
                    node_path.name, node_path, False, size, mtime, icon, level
                )
            elif level >= max_depth:
                size = get_dir_size(node_path)
                return FileNode(
                    node_path.name + "[已折叠]",
                    node_path,
                    True,
                    size,
                    mtime,
                    "📁",
                    level,
                )

            try:
                entries = list(node_path.iterdir())
            except (PermissionError, FileNotFoundError) as e:
                return FileNode(
                    f"[无法访问{node_path.name}]",
                    node_path,
                    True,
                    0,
                    mtime,
                    "🚫",
                    level,
                )

            dirs = [e for e in entries if e.is_dir()]
            files = [e for e in entries if e.is_file()]

            max_dir_name_len = max(
                (wcswidth(str(item.name)) for item in dirs), default=0
            )
            max_file_name_len = max(
                (wcswidth(str(item.name)) for item in files), default=0
            )

            children = []
            total_size = HumanBytes(0)

            exclude_dirs_size = HumanBytes(0)
            exclude_file_size = HumanBytes(0)

            exclude_dirs_num = 0
            exclude_file_num = 0
            for child in entries:
                if child.is_dir():
                    if child.name in exclude_dirs:
                        subdir_size = get_dir_size(child)
                        total_size += subdir_size
                        exclude_dirs_size += subdir_size
                        exclude_dirs_num += 1
                        continue
                    cnode = _scan(child, level + 1)
                    cnode.max_name_len = max_dir_name_len
                    children.append(cnode)
                    total_size += cnode.size
                else:
                    if child.suffix.lower() in exclude_exts:
                        file_size = get_file_size(child)
                        total_size += file_size
                        exclude_file_size += file_size
                        exclude_file_num += 1
                        continue
                    cnode = _scan(child, level + 1)
                    cnode.max_name_len = max_file_name_len
                    children.append(cnode)
                    total_size += cnode.size

            if exclude_dirs_size > 0:
                exclude_name = f"[{exclude_dirs_num}项排除的目录]"
                children.append(
                    FileNode(
                        exclude_name,
                        node_path / exclude_name,
                        True,
                        exclude_dirs_size,
                        HumanTimestamp(0),
                        "📁",
                        level + 1,
                    )
                )
            if exclude_file_size > 0:
                exclude_name = f"[{exclude_file_num}项排除的文件]"
                children.append(
                    FileNode(
                        exclude_name,
                        node_path / exclude_name,
                        False,
                        exclude_file_size,
                        HumanTimestamp(0),
                        "📄",
                        level + 1,
                    )
                )
            return FileNode(
                node_path.name,
                node_path,
                True,
                total_size,
                mtime,
                "📁",
                level,
                children,
            )

        return cls(_scan(root_path, 0), root_path)

    # 打印树
    def print_tree(self):
        def _print(node: FileNode):
            print(node)
            dirs = [c for c in node.children if c.is_dir]
            files = [c for c in node.children if not c.is_dir]
            for d in dirs:
                _print(d)
            for f in files:
                _print(f)

        _print(self.root)

    # 对比两棵树
    def compare_with(self, other: "FileTree", compare_hash: bool = False) -> "FileDiff":
        diff = FileDiff(
            left_path=self.path,
            right_path=other.path,
            only_in_left=[],
            only_in_right=[],
            different_files=[],
            compare_hash=compare_hash,
            diff_size_left=HumanBytes(0),
            diff_size_right=HumanBytes(0),
        )

        def _compare(n1: FileNode, n2: FileNode) -> FileNode:
            n1_map = {c.name: c for c in n1.children}
            n2_map = {c.name: c for c in n2.children}
            common = n1_map.keys() & n2_map.keys()

            diff_children = []
            diff_size = HumanBytes(0)
            mtime = HumanTimestamp(0)

            # 左独有
            for name in n1_map.keys() - n2_map.keys():
                node = n1_map[name]
                diff.only_in_left.append(node.node_path.relative_to(self.path))
                diff.diff_size_left += node.size
                diff_size += node.size
                diff_children.append(node)

            # 右独有
            for name in n2_map.keys() - n1_map.keys():
                node = n2_map[name]
                diff.only_in_right.append(node.node_path.relative_to(other.path))
                diff.diff_size_right += node.size
                diff_size += node.size
                diff_children.append(node)

            # 公共项
            for name in common:
                c1, c2 = n1_map[name], n2_map[name]
                if c1.is_dir and c2.is_dir:
                    is_equal_size = c1.size == c2.size
                    if is_equal_size:
                        if not compare_hash or c1.hash == c2.hash:
                            continue

                    sub_dir = _compare(c1, c2)
                    diff_size += sub_dir.size
                    diff_children.append(sub_dir)
                elif not c1.is_dir and not c2.is_dir:
                    is_equal_size = c1.size == c2.size
                    if is_equal_size:
                        if not compare_hash or c1.hash == c2.hash:
                            continue

                    diff.different_files.append(c1.node_path.relative_to(self.path))
                    diff.diff_size_left += c1.size
                    diff.diff_size_right += c2.size
                    diff_size += c1.size + c2.size
                    diff_children.append(c1)
                    diff_children.append(c2)
                else:
                    # 一方文件一方文件夹
                    diff.only_in_left.append(c1.node_path.relative_to(self.path))
                    diff.only_in_right.append(c2.node_path.relative_to(other.path))
                    diff.diff_size_left += c1.size
                    diff.diff_size_right += c2.size
                    diff_size += c1.size + c2.size
                    diff_children.append(c1)
                    diff_children.append(c2)

            return FileNode(
                f"{n1.name}",
                None,
                True,
                diff_size,
                mtime,
                "📁",
                n1.level,
                diff_children,
            )

        diff.diff_tree = FileTree(_compare(self.root, other.root), self.path)
        return diff
