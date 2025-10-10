from pathlib import Path
from wcwidth import wcswidth
from typing import Tuple
from dataclasses import dataclass, field

from ..constants import FILE_ICONS
from ..tools.FileOperations import get_file_size, get_folder_size, get_file_hash, align_width
from ..tools.TextTools import format_table
from ..tools.Utilities import bytes_to_human_readable


@dataclass
class FileNode:
    name: str
    relative_path: Path
    is_dir: bool
    size: int
    icon: str
    level: int
    children: list["FileNode"] = field(default_factory=list)
    max_name_len: int = 0

    def to_string(self, indent: str = "", prefix: str = "", suffix: str = "") -> str:
        return f"{indent}{self.icon}{prefix} {align_width(self.name, self.max_name_len)}\t{suffix}"

    def __repr__(self):
        return self.to_string(
            indent = "    "*self.level,
            # prefix = f"[{self.relative_path.parent.as_posix()}]",
            suffix = f"({bytes_to_human_readable(self.size)})"
        )


@dataclass
class FileDiff:
    left_path: Path
    right_path: Path
    only_in_left: list[FileNode]
    only_in_right: list[FileNode]
    size_mismatch: list[Tuple[FileNode, FileNode]]
    diff_size_left: int = 0
    diff_size_right: int = 0
    diff_tree: "FileTree" = None

    def is_identical(self) -> bool:
        return not (self.only_in_left or self.only_in_right or self.size_mismatch)
    
    # 打印树
    def print_diff_tree(self):
        def _print(node: FileNode):
            if node == self.diff_tree.root:
                pass
            elif node.is_dir and node.children:
                print(node.to_string(
                    indent = "    "*(node.level-1),
                    suffix = f"({bytes_to_human_readable(node.size)})"
                ))
            else:
                print(node.to_string(
                    indent = "    "*(node.level-1),
                    prefix = f"[{node.relative_path.parent.as_posix()}]",
                    suffix = f"({bytes_to_human_readable(node.size)})"
                ))
            dirs = [c for c in node.children if c.is_dir]
            files = [c for c in node.children if not c.is_dir]
            for d in dirs:
                _print(d)
            for f in files:
                _print(f)

        _print(self.diff_tree.root)
        print()
        print(format_table([
            [self.left_path, bytes_to_human_readable(self.diff_size_left)],
            [self.right_path, bytes_to_human_readable(self.diff_size_right)]],
            column_names=["Directory", "Diff Size"]
        ))
    

class FileTree:
    def __init__(self, root: FileNode, path: Path):
        self.root = root
        self.path = path

    @classmethod
    def build_from_path(cls, root_path: Path, exclude_dirs=None, exclude_exts=None, max_depth=3):
        root_path = Path(root_path)
        exclude_dirs = set(exclude_dirs or [])
        exclude_exts = set(ext.lower() for ext in (exclude_exts or []))
        def _scan(node_path: Path, level: int) -> FileNode:
            relative_path = node_path.relative_to(root_path.parent)

            if not node_path.exists():
                return FileNode("(空目录)", relative_path, True, 0, "📁", level)
            elif node_path.is_file():
                size = get_file_size(node_path)
                icon = FILE_ICONS.get(node_path.suffix, FILE_ICONS["default"])
                return FileNode(node_path.name, relative_path, False, size, icon, level)
            elif level >= max_depth:
                folder_size = get_folder_size(node_path)
                return FileNode(node_path.name, relative_path, True, folder_size, "📁", level)
            
            entries = list(node_path.iterdir())
            folders = [e for e in entries if e.is_dir()]
            files = [e for e in entries if e.is_file()]
            
            max_folder_name_len = max((wcswidth(str(item.name)) for item in folders), default=0)
            max_file_name_len = max((wcswidth(str(item.name)) for item in files), default=0)

            children = []
            total_size = 0

            exclude_dirs_size = 0
            exclude_file_size = 0

            exclude_dirs_num = 0
            exclude_file_num = 0
            for child in entries:
                if child.is_dir():
                    if child.name in exclude_dirs:
                        subfolder_size = get_folder_size(child)
                        total_size += subfolder_size
                        exclude_dirs_size += subfolder_size
                        exclude_dirs_num += 1
                        continue
                    cnode = _scan(child, level+1)
                    cnode.max_name_len = max_folder_name_len
                    children.append(cnode)
                    total_size += cnode.size
                else:
                    if child.suffix.lower() in exclude_exts:
                        file_size = get_file_size(child)
                        total_size += file_size
                        exclude_file_size += file_size
                        exclude_file_num += 1
                        continue
                    cnode = _scan(child, level+1)
                    cnode.max_name_len = max_file_name_len
                    children.append(cnode)
                    total_size += cnode.size
            
            if exclude_dirs_size > 0:
                exclude_name = f"[{exclude_dirs_num}项排除的目录]"
                children.append(FileNode(exclude_name, relative_path/exclude_name, True, exclude_dirs_size, "📁", level+1))
            if exclude_file_size > 0:
                exclude_name = f"[{exclude_file_num}项排除的文件]"
                children.append(FileNode(exclude_name, relative_path/exclude_name, False, exclude_file_size, "📄", level+1))
            return FileNode(node_path.name, relative_path, True, total_size, "📁", level, children)
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
    def compare_with(self, other: "FileTree") -> "FileDiff":
        diff = FileDiff(
            left_path=self.path,
            right_path=other.path,
            only_in_left=[],
            only_in_right=[],
            size_mismatch=[],
            diff_size_left=0,
            diff_size_right=0,
        )

        def _compare(n1: FileNode, n2: FileNode) -> FileNode:
            n1_map = {c.name: c for c in n1.children}
            n2_map = {c.name: c for c in n2.children}
            common = n1_map.keys() & n2_map.keys()

            diff_children = []

            # 左独有
            for name in n1_map.keys() - n2_map.keys():
                node = n1_map[name]
                diff.only_in_left.append(node)
                diff.diff_size_left += node.size
                diff_children.append(node)

            # 右独有
            for name in n2_map.keys() - n1_map.keys():
                node = n2_map[name]
                diff.only_in_right.append(node)
                diff.diff_size_right += node.size
                diff_children.append(node)

            # 公共项
            for name in common:
                c1, c2 = n1_map[name], n2_map[name]
                if c1.is_dir and c2.is_dir:
                    diff_children.append(_compare(c1, c2))
                elif not c1.is_dir and not c2.is_dir:
                    if c1.size != c2.size:
                        diff.size_mismatch.append((c1, c2))
                        diff.diff_size_left += c1.size
                        diff.diff_size_right += c2.size
                        diff_children.append(c1)
                        diff_children.append(c2)
                else:
                    # 一方文件一方文件夹
                    diff.only_in_left.append(c1)
                    diff.only_in_right.append(c2)
                    diff.diff_size_left += c1.size
                    diff.diff_size_right += c2.size
                    diff_children.append(c1)
                    diff_children.append(c2)

            return FileNode(f"{n1.name}", Path(), True, n1.size, "📁", n1.level, diff_children)

        diff.diff_tree = FileTree(_compare(self.root, other.root), self.path)
        return diff
