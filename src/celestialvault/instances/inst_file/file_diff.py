from dataclasses import dataclass
from pathlib import Path

from celestialflow import TaskExecutor, TaskProgress
from wcwidth import wcswidth

from ...instances.inst_units import HumanBytes, HumanTimestamp
from ...tools.FileOperations import (
    append_hash_to_filename,
    copy_file_or_dir,
    delete_file_or_dir,
)
from ...tools.TextTools import format_table
from .file_node import BaseNode, DirNode, ExcludedDirsNode, ExcludedFilesNode
from .file_tree import FileTree


class DeleteExecutor(TaskExecutor):
    """删除执行器，根据相对路径批量删除指定目录下的文件或文件夹。"""

    def __init__(self, func, parent_dir: Path):
        """
        初始化删除执行器。

        :param func: 执行删除操作的函数。
        :param parent_dir: 被删除文件所在的父目录路径。
        """
        super().__init__("Deleting", func)
        self.add_observer(TaskProgress())
        self.parent_dir = parent_dir

    def get_args(self, rel_path: Path):
        """
        根据相对路径计算要删除的目标绝对路径。

        :param rel_path: 文件的相对路径。
        :return: 包含目标绝对路径的元组。
        """
        target = self.parent_dir / rel_path
        return (target,)


class CopyExecutor(TaskExecutor):
    """复制执行器，根据相对路径将文件从主目录批量复制到次目录。"""

    def __init__(self, func, main_dir: Path, minor_dir: Path, copy_mode: str):
        """
        初始化复制执行器。

        :param func: 执行复制操作的函数。
        :param main_dir: 主目录（源）路径。
        :param minor_dir: 次目录（目标）路径。
        :param copy_mode: 同步模式，如 '->'、'<-'。
        """
        super().__init__(
            f"Copying({copy_mode})", func
        )
        self.add_observer(TaskProgress())
        self.main_dir = main_dir
        self.minor_dir = minor_dir

    def get_args(self, rel_path: Path):
        """
        根据相对路径计算源文件和目标文件的绝对路径，并确保目标目录存在。

        :param rel_path: 文件的相对路径。
        :return: (源文件路径, 目标文件路径) 的元组。
        """
        source = self.main_dir / rel_path
        target = self.minor_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        return (source, target)


@dataclass
class FileDiff:
    """两个目录的差异比较结果，包含仅存在于单侧的文件和内容不同的文件列表。"""

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
        """
        判断两个目录是否完全相同（无差异文件）。

        :return: 如果两个目录完全一致返回 True，否则返回 False。
        """
        return not (self.only_in_left or self.only_in_right or self.different_files)

    # 打印树
    def print_diff_tree(self):
        """
        以树形结构打印差异文件，并显示两侧目录的差异大小汇总表。
        """

        def _print(node: BaseNode, max_name_len: int = 0):
            node.print(
                level=node.level - 1,
                prefix=(
                    f"[{node.node_path.parent.as_posix()}]" if node.node_path else ""
                ),
                suffix=(
                    f"({node.size}) ({node.hash})"
                    if self.compare_hash and node._hash
                    else f"({node.size})"
                ),
                max_name_len=max_name_len,
            )
            if node.is_dir():
                dirs = []
                files = []
                child_names = []

                for c in node.children:
                    if c.is_dir():
                        dirs.append(c)
                    else:
                        files.append(c)
                    child_names.append(c.name)
                child_max_name_len = max(
                    (wcswidth(name) for name in child_names), default=0
                )

                for d in dirs:
                    _print(d, child_max_name_len)
                for f in files:
                    _print(f, child_max_name_len)

        if self.is_identical():
            print("No different files found.")
            return

        dirs = [c for c in self.diff_tree.root.children if c.is_dir()]
        files = [c for c in self.diff_tree.root.children if not c.is_dir()]
        for d in dirs:
            _print(d)
        for f in files:
            _print(f)
        print()
        print(
            format_table(
                [
                    [self.left_path, self.diff_size_left],
                    [self.right_path, self.diff_size_right],
                ],
                column_names=["Directory", "Diff Size"],
            )
        )

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
            main_dir, minor_dir = (
                (self.left_path, self.right_path)
                if is_mode_a
                else (self.right_path, self.left_path)
            )

            # 差异分配
            main_dir_diff, minor_dir_diff = (
                (self.only_in_left, self.only_in_right)
                if is_mode_a
                else (self.only_in_right, self.only_in_left)
            )
            main_dir_diff = main_dir_diff + self.different_files

            delete_executor = DeleteExecutor(delete_file_or_dir, minor_dir)
            copy_executor = CopyExecutor(
                copy_file_or_dir, main_dir, minor_dir, copy_mode=mode
            )

            delete_executor.start(minor_dir_diff)
            copy_executor.start(main_dir_diff)

        elif mode == "<->":
            copy_a_to_b_executor = CopyExecutor(
                copy_file_or_dir, self.left_path, self.right_path, copy_mode="->"
            )
            copy_b_to_a_executor = CopyExecutor(
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

            copy_a_to_b_executor.start(self.only_in_left + diff_file_in_dir1)
            copy_b_to_a_executor.start(self.only_in_right + diff_file_in_dir2)

        else:
            raise ValueError("无效的模式，必须为 '->', '<-' 或 '<->'")

    def to_dict(self):
        """
        将差异结果转换为可序列化的字典。

        :return: 包含差异路径和大小信息的字典。
        """
        return {
            "left_path": str(self.left_path),
            "right_path": str(self.right_path),
            "only_in_left": [p.as_posix() for p in self.only_in_left],
            "only_in_right": [p.as_posix() for p in self.only_in_right],
            "different_files": [p.as_posix() for p in self.different_files],
            "diff_size_left": self.diff_size_left,
            "diff_size_right": self.diff_size_right,
        }


# 对比两棵树
def compare_trees(
    tree1: FileTree, tree2: FileTree, compare_hash: bool = False
) -> "FileDiff":
    """
    将当前文件树与另一棵文件树对比，返回包含差异信息的 FileDiff 对象。

    :param tree1: 第一棵文件树。
    :param tree2: 要对比的第二棵文件树。
    :param compare_hash: 是否通过哈希值比较文件内容。
    :return: 包含两棵树差异信息的 FileDiff 对象。
    """
    diff = FileDiff(
        left_path=tree1.path,
        right_path=tree2.path,
        only_in_left=[],
        only_in_right=[],
        different_files=[],
        compare_hash=compare_hash,
        diff_size_left=HumanBytes(0),
        diff_size_right=HumanBytes(0),
    )

    def _compare(n1: DirNode, n2: DirNode) -> DirNode:
        n1_map = {c.name: c for c in n1.children if not isinstance(c, (ExcludedFilesNode, ExcludedDirsNode))}
        n2_map = {c.name: c for c in n2.children if not isinstance(c, (ExcludedFilesNode, ExcludedDirsNode))}
        common = n1_map.keys() & n2_map.keys()

        diff_children = []
        diff_size = HumanBytes(0)
        mtime = HumanTimestamp(0)

        # 左独有
        for name in n1_map.keys() - n2_map.keys():
            node = n1_map[name]
            diff.only_in_left.append(node.node_path.relative_to(tree1.path))
            diff.diff_size_left += node.size
            diff_size += node.size
            diff_children.append(node)

        # 右独有
        for name in n2_map.keys() - n1_map.keys():
            node = n2_map[name]
            diff.only_in_right.append(node.node_path.relative_to(tree2.path))
            diff.diff_size_right += node.size
            diff_size += node.size
            diff_children.append(node)

        # 公共项
        for name in common:
            c1, c2 = n1_map[name], n2_map[name]
            if c1.is_dir() and c2.is_dir():
                # 双方都是文件夹
                is_equal_size = c1.size == c2.size
                if is_equal_size:
                    if not compare_hash or c1.hash == c2.hash:
                        continue

                sub_dir = _compare(c1, c2)
                diff_size += sub_dir.size
                mtime = max(mtime, sub_dir.mtime)
                diff_children.append(sub_dir)
            elif not c1.is_dir() and not c2.is_dir():
                # 双方都是文件
                is_equal_size = c1.size == c2.size
                if is_equal_size:
                    if not compare_hash or c1.hash == c2.hash:
                        continue

                diff.different_files.append(c1.node_path.relative_to(tree1.path))
                diff.diff_size_left += c1.size
                diff.diff_size_right += c2.size
                diff_size += c1.size + c2.size
                mtime = max(mtime, c1.mtime, c2.mtime)
                diff_children.append(c1)
                diff_children.append(c2)
            else:
                # 一方文件一方文件夹
                diff.only_in_left.append(c1.node_path.relative_to(tree1.path))
                diff.only_in_right.append(c2.node_path.relative_to(tree2.path))
                diff.diff_size_left += c1.size
                diff.diff_size_right += c2.size
                diff_size += c1.size + c2.size
                mtime = max(mtime, c1.mtime, c2.mtime)
                diff_children.append(c1)
                diff_children.append(c2)

        return DirNode(
            "DiffTree",
            n1.node_path,
            diff_size,
            mtime,
            n1.level,
            diff_children,
        )

    diff.diff_tree = FileTree(_compare(tree1.root, tree2.root), tree1.path)
    return diff
