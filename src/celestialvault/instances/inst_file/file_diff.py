from pathlib import Path
from dataclasses import dataclass
from celestialflow import TaskExecutor
from typing import TYPE_CHECKING

from ...instances.inst_units import HumanBytes
from ...tools.FileOperations import (
    delete_file_or_dir,
    copy_file_or_dir,
    append_hash_to_filename,
)
from ...tools.TextTools import format_table
from .file_node import FileNode

if TYPE_CHECKING:
    from .file_tree import FileTree


class DeleteExecutor(TaskExecutor):
    """删除执行器，根据相对路径批量删除指定目录下的文件或文件夹。"""

    def __init__(self, func, parent_dir: Path):
        super().__init__(func, progress_desc="Deleting", show_progress=True)
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
        super().__init__(func, progress_desc=f"Copying({copy_mode})", show_progress=True)
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
        def _print(node: FileNode):
            if node == self.diff_tree.root:
                pass
            else:
                print(
                    node.to_string(
                        indent="    " * (node.level - 1),
                        prefix=(
                            f"[{node.node_path.parent.as_posix()}]"
                            if node.node_path
                            else ""
                        ),
                        suffix=(
                            f"({node.size}) ({node.hash})"
                            if self.compare_hash and node._hash
                            else f"({node.size})"
                        ),
                    )
                )
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
