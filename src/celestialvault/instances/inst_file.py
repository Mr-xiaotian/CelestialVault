import hashlib
from pathlib import Path
from wcwidth import wcswidth
from dataclasses import dataclass, field
from celestialflow import TaskManager

from ..constants import FILE_ICONS
from ..instances.inst_units import HumanBytes, HumanTimestamp
from ..tools.FileOperations import (
    get_file_size, get_dir_size, get_file_hash, get_file_mtime, get_dir_mtime,
    align_width, delete_file_or_dir, copy_file_or_dir, 
    append_hash_to_filename
)
from ..tools.TextTools import format_table


class DeleteManager(TaskManager):
    def __init__(self, func, parent_dir: Path):
        super().__init__(
            func, progress_desc="Delete files/dirs"
        )
        self.parent_dir = parent_dir

    def get_args(self, rel_path: Path):
        target = self.parent_dir / rel_path
        return (target,)


class CopyManager(TaskManager):
    def __init__(self, func, main_dir: Path, minor_dir: Path, copy_mode: str):
        super().__init__(
            func, progress_desc=f"Copy files/dirs[{copy_mode}]"
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
    mtime: HumanTimestamp
    icon: str
    level: int
    children: list["FileNode"] = field(default_factory=list)
    max_name_len: int = 0

    _hash: str | None = field(default=None, repr=False)

    def to_string(self, indent: str = "", prefix: str = "", suffix: str = "") -> str:
        return f"{indent}{self.icon}{prefix} {align_width(self.name, self.max_name_len)}\t{suffix}"

    def __repr__(self):
        return self.to_string(
            indent = "    "*self.level,
            # prefix = f"[{self.node_path.parent.as_posix()}]",
            # prefix = f"[{self.mtime}]",
            suffix = f"({self.size})"
        )
    
    @property
    def hash(self) -> str:
        """惰性计算文件哈希"""
        # 排除统计节点
        if self.name.startswith("[") and (self.name.endswith("排除的目录]") or self.name.endswith("排除的文件]")):
            self._hash = ""
            return self._hash
        
        if not self.node_path.exists():
            self._hash = ""
            return self._hash
        
        # 检查是否需要重新计算
        new_mtime = get_dir_mtime(self.node_path) if self.is_dir else get_file_mtime(self.node_path)
        if self._hash is not None and self.mtime == new_mtime:
            return self._hash
        
        # 更新状态并重新计算
        self.mtime = new_mtime
        if self.is_dir:
            self._hash = self._compute_dir_hash()
        else:
            self._hash = get_file_hash(self.node_path)

        return self._hash
    
    def _compute_dir_hash(self, algo: str = "sha256") -> str:
        """根据子节点组合目录哈希"""
        def _hash_bytes(data: bytes) -> str:
            return hashlib.new(algo, data).hexdigest()
        
        child_hashes = []
        for child in sorted(self.children, key=lambda c: (not c.is_dir, c.name)):
            h = child.hash
            if not h:
                continue
            # 将类型标记 + 名称 + hash 拼起来（防止哈希碰撞）
            tag = "D" if child.is_dir else "F"
            entry = f"{tag}:{child.name}:{h}".encode("utf-8")
            child_hashes.append(entry)

        if not child_hashes:
            combined = b"[EMPTY]"
        else:
            combined = b"".join(child_hashes)

        return _hash_bytes(combined)


@dataclass
class FileDiff:
    left_path: Path
    right_path: Path
    only_in_left: list[Path]
    only_in_right: list[Path]
    different_files: list[Path]
    compare_hash: bool
    diff_size_left: HumanBytes = HumanBytes(0)
    diff_size_right: HumanBytes = HumanBytes(0)
    diff_tree: "FileTree" = None

    def is_identical(self) -> bool:
        return not (self.only_in_left or self.only_in_right or self.different_files)
    
    # 打印树
    def print_diff_tree(self):
        def _print(node: FileNode):
            if node == self.diff_tree.root:
                pass
            else:
                print(node.to_string(
                    indent = "    "*(node.level-1),
                    prefix = f"[{node.node_path.parent.as_posix()}]" if node.node_path else "",
                    suffix = f"({node.size}) ({node.hash})" if self.compare_hash and node._hash else f"({node.size})"
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

    def sync_dirs(self, mode: str = "->"):
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

            delete_manager = DeleteManager(delete_file_or_dir, minor_dir)
            copy_manager = CopyManager(
                copy_file_or_dir, main_dir, minor_dir, copy_mode=mode
            )

            delete_manager.start(minor_dir_diff)
            copy_manager.start(main_dir_diff)

        elif mode == "<->":
            copy_a_to_b_manager = CopyManager(
                copy_file_or_dir, self.left_path, self.right_path, copy_mode="->"
            )
            copy_b_to_a_manager = CopyManager(
                copy_file_or_dir, self.right_path, self.left_path, copy_mode="<-"
            )

            diff_file_in_dir1 = []
            diff_file_in_dir2 = []
            for rel_path in self.different_files:
                file1 = self.left_path / rel_path
                file2 = self.right_path / rel_path

                new_file1 = append_hash_to_filename(file1)
                new_file2 = append_hash_to_filename(file2)

                diff_file_in_dir1.append(new_file1.relative_to(self.left_path))
                diff_file_in_dir2.append(new_file2.relative_to(self.right_path))

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
                return FileNode("(空目录)", node_path, True, 0, HumanTimestamp(0), "📁", level)
            
            mtime = get_dir_mtime(node_path) if node_path.is_dir() else get_file_mtime(node_path)
            if node_path.is_file():
                size = get_file_size(node_path)
                icon = FILE_ICONS.get(node_path.suffix, FILE_ICONS["default"])
                return FileNode(node_path.name, node_path, False, size, mtime, icon, level)
            elif level >= max_depth:
                size = get_dir_size(node_path)
                return FileNode(node_path.name + "[已折叠]", node_path, True, size, mtime, "📁", level)
            
            try:
                entries = list(node_path.iterdir())
            except (PermissionError, FileNotFoundError) as e:
                return FileNode(f"[无法访问{node_path.name}]", node_path, True, 0, mtime, "🚫", level)

            dirs = [e for e in entries if e.is_dir()]
            files = [e for e in entries if e.is_file()]
            
            max_dir_name_len = max((wcswidth(str(item.name)) for item in dirs), default=0)
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
                        subdir_size = get_dir_size(child)
                        total_size += subdir_size
                        exclude_dirs_size += subdir_size
                        exclude_dirs_num += 1
                        continue
                    cnode = _scan(child, level+1)
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
                    cnode = _scan(child, level+1)
                    cnode.max_name_len = max_file_name_len
                    children.append(cnode)
                    total_size += cnode.size
            
            if exclude_dirs_size > 0:
                exclude_name = f"[{exclude_dirs_num}项排除的目录]"
                children.append(FileNode(exclude_name, node_path/exclude_name, True, exclude_dirs_size, HumanTimestamp(0), "📁", level+1))
            if exclude_file_size > 0:
                exclude_name = f"[{exclude_file_num}项排除的文件]"
                children.append(FileNode(exclude_name, node_path/exclude_name, False, exclude_file_size, HumanTimestamp(0), "📄", level+1))
            return FileNode(node_path.name, node_path, True, total_size, mtime, "📁", level, children)
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
    def compare_with(self, other: "FileTree", compare_hash: bool=False) -> "FileDiff":
        diff = FileDiff(
            left_path=self.path,
            right_path=other.path,
            only_in_left=[],
            only_in_right=[],
            different_files=[],
            compare_hash = compare_hash,
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

            return FileNode(f"{n1.name}", None, True, diff_size, mtime, "📁", n1.level, diff_children)

        diff.diff_tree = FileTree(_compare(self.root, other.root), self.path)
        return diff
    
