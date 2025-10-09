from pathlib import Path
from wcwidth import wcswidth
from dataclasses import dataclass, field

from ..constants import FILE_ICONS
from ..tools.FileOperations import get_file_size, get_folder_size, align_width
from ..tools.TextTools import format_table
from ..tools.Utilities import bytes_to_human_readable

@dataclass
class FileNode:
    name: str
    path: Path
    is_dir: bool
    size: int
    icon: str
    children: list["FileNode"] = field(default_factory=list)
    max_name_len: int = 0

    def __repr__(self):
        return f"{self.icon} {align_width(self.name, self.max_name_len)}\t({bytes_to_human_readable(self.size)})"


class FileTree:
    def __init__(self, root: FileNode):
        self.root = root

    @classmethod
    def build_from_path(cls, path: Path, exclude_dirs=None, exclude_exts=None, max_depth=3):
        exclude_dirs = set(exclude_dirs or [])
        exclude_exts = set(ext.lower() for ext in (exclude_exts or []))
        def _scan(node_path: Path, depth: int) -> FileNode:
            if not node_path.exists():
                return FileNode(node_path.name, node_path, True, 0, "📁")
            elif node_path.is_file():
                size = get_file_size(node_path)
                icon = FILE_ICONS.get(node_path.suffix, FILE_ICONS["default"])
                return FileNode(node_path.name, node_path, False, size, icon)
            elif depth <= 0:
                folder_size = get_folder_size(node_path)
                return FileNode(node_path.name, node_path, True, folder_size, "📁")
            

            folders = [item for item in node_path.iterdir() if item.is_dir()]
            max_folder_name_len = max((wcswidth(str(item.name)) for item in folders), default=0)
            
            files = [item for item in node_path.iterdir() if item.is_file()]
            max_file_name_len = max((wcswidth(str(item.name)) for item in files), default=0)

            children = []
            total_size = 0

            exclude_dirs_size = 0
            exclude_file_size = 0

            exclude_dirs_num = 0
            exclude_file_num = 0
            for child in node_path.iterdir():
                if child.is_dir():
                    if child.name in exclude_dirs:
                        subfolder_size = get_folder_size(child)
                        total_size += subfolder_size
                        exclude_dirs_size += subfolder_size
                        exclude_dirs_num += 1
                        continue
                    cnode = _scan(child, depth-1)
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
                    cnode = _scan(child, depth-1)
                    cnode.max_name_len = max_file_name_len
                    children.append(cnode)
                    total_size += cnode.size
            
            if exclude_dirs_size > 0:
                children.append(FileNode(f"[{exclude_dirs_num}项排除的目录]", node_path, True, exclude_dirs_size, "📁"))
            if exclude_file_size > 0:
                children.append(FileNode(f"[{exclude_file_num}项排除的文件]", node_path, False, exclude_file_size, "📄"))
            return FileNode(node_path.name, node_path, True, total_size, "📁", children)
        return cls(_scan(Path(path), max_depth))

    def print_tree(self, indent=""):
        def _print(node: FileNode, level_indent: str):
            print(f"{level_indent}{node}")

            # 先打印子文件夹
            dirs = [child for child in node.children if child.is_dir]
            files = [child for child in node.children if not child.is_dir]

            for d in dirs:
                _print(d, level_indent + "    ")
            for f in files:
                _print(f, level_indent + "    ")

        _print(self.root, indent)

    def compare_with(self, other: "FileTree"):
        """递归比较两棵文件树"""
        def _compare(node1: FileNode, node2: FileNode, path=""):
            diffs = []
            n1_children = {c.name: c for c in node1.children}
            n2_children = {c.name: c for c in node2.children}
            for name in n1_children.keys() - n2_children.keys():
                diffs.append(f"📁 only in {node1.path}: {name}")
            for name in n2_children.keys() - n1_children.keys():
                diffs.append(f"📁 only in {node2.path}: {name}")
            for name in n1_children.keys() & n2_children.keys():
                c1, c2 = n1_children[name], n2_children[name]
                if c1.is_dir and c2.is_dir:
                    diffs.extend(_compare(c1, c2, path + "/" + name))
                elif c1.size != c2.size:
                    diffs.append(f"⚠️ size mismatch: {path}/{name}")
            return diffs
        return _compare(self.root, other.root)
