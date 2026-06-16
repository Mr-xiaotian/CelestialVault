import hashlib
from dataclasses import dataclass
from pathlib import Path

from ...instances.inst_units import HumanBytes, HumanTimestamp
from ...tools.FileOperations import (
    get_dir_mtime,
    get_file_hash,
    get_file_mtime,
)
from .file_util import to_string


class BaseNode:
    name: str
    node_path: Path
    size: HumanBytes
    mtime: HumanTimestamp
    icon: str
    level: int

    def __init__(
        self,
        name: str,
        node_path: Path,
        size: HumanBytes,
        mtime: HumanTimestamp,
        icon: str,
        level: int,
    ):
        """
        初始化文件树节点基类。

        :param name: 节点名称。
        :param node_path: 节点的文件系统路径。
        :param size: 节点大小。
        :param mtime: 节点修改时间。
        :param icon: 节点显示图标。
        :param level: 节点在文件树中的深度。
        """
        self.name = name
        self.node_path = node_path
        self.size = size
        self.mtime = mtime
        self.icon = icon
        self.level = level

        self._hash: str | None = None

    @property
    def hash(self) -> str:
        """返回节点哈希值。子类应覆盖此属性。"""
        return self._hash or ""

    def is_dir(self) -> bool:
        """返回节点是否为目录。子类应覆盖此方法。"""
        return False

    @property
    def children(self) -> list["BaseNode"]:
        """返回子节点列表。叶子节点返回空列表。"""
        return []

    def print(
        self,
        level: int | None = None,
        prefix: str | None = None,
        name: str | None = None,
        suffix: str | None = None,
        max_name_len: int | None = None,
    ) -> None:
        """
        打印节点信息。

        :param level: 缩进级别，默认使用节点自身层级。
        :param prefix: 前缀字符串。
        :param name: 显示名称，默认使用节点名称。
        :param suffix: 后缀字符串，默认显示大小。
        :param max_name_len: 名称对齐的最大长度。
        """
        print(
            to_string(
                indent="    " * level if level is not None else "    " * self.level,
                icon=self.icon,
                prefix=prefix or "",  # f"[{self.node_path.parent.as_posix()}]"
                name=name or self.name,
                suffix=suffix
                or f"({self.size})",  # f"({self.size})" / f"[{self.mtime}]",
                max_name_len=max_name_len or 0,
            )
        )


@dataclass
class FileNode(BaseNode):
    def __init__(
        self,
        name: str,
        suffix: str,
        node_path: Path,
        size: HumanBytes,
        mtime: HumanTimestamp,
        icon: str,
        level: int,
    ):
        """
        初始化文件节点。

        :param name: 文件名。
        :param suffix: 文件后缀。
        :param node_path: 文件路径。
        :param size: 文件大小。
        :param mtime: 文件修改时间。
        :param icon: 显示图标。
        :param level: 节点深度。
        """
        super().__init__(name, node_path, size, mtime, icon, level)
        self.suffix = suffix

    @property
    def hash(self) -> str:
        """惰性计算文件哈希"""
        if not self.node_path.exists():
            self._hash = ""
            return self._hash

        # 检查是否需要重新计算
        new_mtime = get_file_mtime(self.node_path)
        if self._hash is not None and self.mtime == new_mtime:
            return self._hash

        # 更新状态并重新计算
        self.mtime = new_mtime
        self._hash = get_file_hash(self.node_path)

        return self._hash

    def is_dir(self) -> bool:
        """返回 False，文件节点不是目录。"""
        return False


@dataclass
class DirNode(BaseNode):
    def __init__(
        self,
        name: str,
        node_path: Path,
        size: HumanBytes,
        mtime: HumanTimestamp,
        level: int,
        children: list["BaseNode"],
    ):
        """
        初始化目录节点。

        :param name: 目录名。
        :param node_path: 目录路径。
        :param size: 目录总大小。
        :param mtime: 目录修改时间。
        :param level: 节点深度。
        :param children: 子节点列表。
        """
        super().__init__(name, node_path, size, mtime, "📁", level)
        self.children: list[BaseNode] = children

    @property
    def hash(self) -> str:
        """惰性计算文件哈希"""
        if not self.node_path.exists():
            self._hash = ""
            return self._hash

        # 检查是否需要重新计算
        new_mtime = get_dir_mtime(self.node_path)
        if self._hash is not None and self.mtime == new_mtime:
            return self._hash

        # 更新状态并重新计算
        self.mtime = new_mtime
        self._hash = self._compute_dir_hash()

        return self._hash

    def _compute_dir_hash(self, algo: str = "sha256") -> str:
        """根据子节点组合目录哈希"""

        def _hash_bytes(data: bytes) -> str:
            return hashlib.new(algo, data).hexdigest()

        child_hashes: list[bytes] = []
        for child in sorted(self.children, key=lambda c: (not c.is_dir(), c.name)):
            h = child.hash
            if not h:
                continue
            tag = "D" if child.is_dir() else "F"
            entry = f"{tag}:{child.name}:{h}".encode()
            child_hashes.append(entry)

        combined = b"[EMPTY]" if not child_hashes else b"".join(child_hashes)

        return _hash_bytes(combined)

    def is_dir(self) -> bool:
        """返回 True，目录节点是目录。"""
        return True


class ExcludedFilesNode(BaseNode):
    """被排除的文件汇总节点，记录被排除文件的数量和总大小。"""

    def __init__(
        self,
        count: int,
        node_path: Path,
        size: HumanBytes,
        mtime: HumanTimestamp,
        level: int,
    ):
        """
        初始化被排除的文件汇总节点。

        :param count: 被排除的文件数量。
        :param node_path: 所属目录路径。
        :param size: 被排除文件的总大小。
        :param mtime: 被排除文件中最晚的修改时间。
        :param level: 节点深度。
        """
        super().__init__(f"[{count}项排除的文件]", node_path, size, mtime, "📄", level)
        self.count = count

    @property
    def hash(self) -> str:
        """排除节点不计算哈希。"""
        return ""

    def is_dir(self) -> bool:
        """返回 False，文件汇总节点不是目录。"""
        return False


class ExcludedDirsNode(BaseNode):
    """被排除的目录汇总节点，记录被排除目录的数量和总大小。"""

    def __init__(
        self,
        count: int,
        node_path: Path,
        size: HumanBytes,
        mtime: HumanTimestamp,
        level: int,
    ):
        """
        初始化被排除的目录汇总节点。

        :param count: 被排除的目录数量。
        :param node_path: 所属目录路径。
        :param size: 被排除目录的总大小。
        :param mtime: 被排除目录中最晚的修改时间。
        :param level: 节点深度。
        """
        super().__init__(f"[{count}项排除的目录]", node_path, size, mtime, "📁", level)
        self.count = count
        self.children: list[BaseNode] = []

    @property
    def hash(self) -> str:
        """排除节点不计算哈希。"""
        return ""

    def is_dir(self) -> bool:
        """返回 True，目录汇总节点是目录。"""
        return True
