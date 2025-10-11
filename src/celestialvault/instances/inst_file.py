from pathlib import Path
from wcwidth import wcswidth
from dataclasses import dataclass, field
from celestialflow import TaskManager

from ..constants import FILE_ICONS
from ..instances.inst_units import HumanBytes
from ..tools.FileOperations import (
    get_file_size, get_folder_size, get_file_hash, 
    align_width, delete_file_or_folder, copy_file_or_folder, 
    append_hash_to_filename
)
from ..tools.TextTools import format_table


class DeleteManager(TaskManager):
    def __init__(self, func, parent_dir: Path):
        super().__init__(func, progress_desc="Delete files/folders", show_progress=True)
        self.parent_dir = parent_dir

    def get_args(self, rel_path):
        target = self.parent_dir / rel_path
        return (target,)


class CopyManager(TaskManager):
    def __init__(self, func, main_dir: Path, minor_dir: Path, copy_mode: str):
        super().__init__(
            func, progress_desc=f"Copy files/folders[{copy_mode}]", show_progress=True
        )
        self.main_dir = main_dir
        self.minor_dir = minor_dir

    def get_args(self, rel_path: Path):
        source = self.main_dir / rel_path
        target = self.minor_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        return (source, target)


@dataclass
class FileNode:
    name: str
    node_path: Path
    is_dir: bool
    size: HumanBytes
    icon: str
    level: int
    children: list["FileNode"] = field(default_factory=list)
    max_name_len: int = 0

    def to_string(self, indent: str = "", prefix: str = "", suffix: str = "") -> str:
        return f"{indent}{self.icon}{prefix} {align_width(self.name, self.max_name_len)}\t{suffix}"

    def __repr__(self):
        return self.to_string(
            indent = "    "*self.level,
            # prefix = f"[{self.node_path.parent.as_posix()}]",
            suffix = f"({self.size})"
        )


@dataclass
class FileDiff:
    left_path: Path
    right_path: Path
    only_in_left: list[Path]
    only_in_right: list[Path]
    different_files: list[Path]
    diff_size_left: int = 0
    diff_size_right: int = 0
    diff_tree: "FileTree" = None

    def is_identical(self) -> bool:
        return not (self.only_in_left or self.only_in_right or self.different_files)
    
    # 打印树
    def print_diff_tree(self):
        def _print(node: FileNode):
            if node == self.diff_tree.root:
                pass
            elif node.is_dir and node.children:
                print(node.to_string(
                    indent = "    "*(node.level-1),
                    suffix = node.size
                ))
            else:
                print(node.to_string(
                    indent = "    "*(node.level-1),
                    prefix = f"[{node.node_path.parent.as_posix()}]",
                    suffix = node.size
                ))
            dirs = [c for c in node.children if c.is_dir]
            files = [c for c in node.children if not c.is_dir]
            for d in dirs:
                _print(d)
            for f in files:
                _print(f)

        if self.is_identical():
            print("No different files found.")
            return

        _print(self.diff_tree.root)
        print()
        print(format_table([
            [self.left_path, self.diff_size_left],
            [self.right_path, self.diff_size_right]],
            column_names=["Directory", "Diff Size"]
        ))

    def sync_folders(self, mode: str = "->"):
        """
        根据差异字典同步两个文件夹。

        :param mode: 同步模式，
                    '->' 表示以第一个文件夹为主，
                    '<-' 表示以第二个文件夹为主，
                    '<->' 表示双向同步
        """

        if mode in ["->", "<-"]:
            # 确定主目录和次目录
            is_mode_a = mode == "->"
            main_dir, minor_dir = (self.left_path, self.right_path) if is_mode_a else (self.right_path, self.left_path)

            # 差异分配
            main_dir_diff, minor_dir_diff = (self.only_in_left, self.only_in_right) if is_mode_a else (self.only_in_right, self.only_in_left)
            main_dir_diff = main_dir_diff + self.different_files

            delete_manager = DeleteManager(delete_file_or_folder, minor_dir)
            copy_manager = CopyManager(
                copy_file_or_folder, main_dir, minor_dir, copy_mode=mode
            )

            delete_manager.start(minor_dir_diff)
            copy_manager.start(main_dir_diff)

        elif mode == "<->":
            copy_a_to_b_manager = CopyManager(
                copy_file_or_folder, self.left_path, self.right_path, copy_mode="->"
            )
            copy_b_to_a_manager = CopyManager(
                copy_file_or_folder, self.right_path, self.left_path, copy_mode="<-"
            )

            diff_file_in_dir1 = []
            diff_file_in_dir2 = []
            for rel_path in self.different_files:
                file1 = self.left_path / rel_path
                file2 = self.right_path / rel_path

                new_file1_name = append_hash_to_filename(file1)
                new_file2_name = append_hash_to_filename(file2)

                diff_file_in_dir1.append(new_file1_name)
                diff_file_in_dir2.append(new_file2_name)

            copy_a_to_b_manager.start(self.only_in_left + diff_file_in_dir1)
            copy_b_to_a_manager.start(self.only_in_right + diff_file_in_dir2)

        else:
            raise ValueError("无效的模式，必须为 '->', '<-' 或 '<->'")
        
    def to_dict(self):
        return {
            "left_path": str(self.left_path),
            "right_path": str(self.right_path),
            "only_in_left": [p.as_posix() for p in self.only_in_left],
            "only_in_right": [p.as_posix() for p in self.only_in_right],
            "different_files": [p.as_posix() for p in self.different_files],
            "diff_size_left": self.diff_size_left,
            "diff_size_right": self.diff_size_right,
        }



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
            if not node_path.exists():
                return FileNode("(空目录)", node_path, True, 0, "📁", level)
            elif node_path.is_file():
                size = get_file_size(node_path)
                icon = FILE_ICONS.get(node_path.suffix, FILE_ICONS["default"])
                return FileNode(node_path.name, node_path, False, size, icon, level)
            elif level >= max_depth:
                folder_size = get_folder_size(node_path)
                return FileNode(node_path.name, node_path, True, folder_size, "📁", level)
            
            try:
                entries = list(node_path.iterdir())
            except (PermissionError, FileNotFoundError) as e:
                return FileNode(f"[无法访问{node_path.name}]", node_path, True, 0, "🚫", level)

            folders = [e for e in entries if e.is_dir()]
            files = [e for e in entries if e.is_file()]
            
            max_folder_name_len = max((wcswidth(str(item.name)) for item in folders), default=0)
            max_file_name_len = max((wcswidth(str(item.name)) for item in files), default=0)

            children = []
            total_size = HumanBytes(0)

            exclude_dirs_size = HumanBytes(0)
            exclude_file_size = HumanBytes(0)

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
                children.append(FileNode(exclude_name, node_path/exclude_name, True, exclude_dirs_size, "📁", level+1))
            if exclude_file_size > 0:
                exclude_name = f"[{exclude_file_num}项排除的文件]"
                children.append(FileNode(exclude_name, node_path/exclude_name, False, exclude_file_size, "📄", level+1))
            return FileNode(node_path.name, node_path, True, total_size, "📁", level, children)
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
            different_files=[],
            diff_size_left=0,
            diff_size_right=0,
        )

        def _compare(n1: FileNode, n2: FileNode) -> FileNode:
            n1_map = {c.name: c for c in n1.children}
            n2_map = {c.name: c for c in n2.children}
            common = n1_map.keys() & n2_map.keys()

            diff_children = []
            diff_size = 0

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
                    sub_folder = _compare(c1, c2)
                    diff_size += sub_folder.size
                    diff_children.append(sub_folder)
                elif not c1.is_dir and not c2.is_dir:
                    if c1.size != c2.size:
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

            return FileNode(f"{n1.name}", Path(), True, diff_size, "📁", n1.level, diff_children)

        diff.diff_tree = FileTree(_compare(self.root, other.root), self.path)
        return diff
