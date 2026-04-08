import hashlib
from pathlib import Path
from dataclasses import dataclass
from ...instances.inst_units import HumanBytes, HumanTimestamp
from ...tools.FileOperations import (
    get_file_hash,
    get_file_mtime,
    get_dir_mtime,
)
from .file_util import to_string


class BaseNode:
    def __init__(self, name: str, node_path: Path, size: HumanBytes, mtime: HumanTimestamp, icon: str, level: int):
        self.name = name
        self.node_path = node_path
        self.size = size
        self.mtime = mtime
        self.icon = icon
        self.level = level

        self._hash: str | None = None

    def print(self, level: int = None, prefix: str = None, name: str = None, suffix: str = None, max_name_len: int = None):
        print(to_string(
            indent="    " * level if level is not None else "    " * self.level,
            icon=self.icon,
            prefix=prefix or "", # f"[{self.node_path.parent.as_posix()}]"
            name=name or self.name,
            suffix=suffix or f"({self.size})", # f"({self.size})" / f"[{self.mtime}]",
            max_name_len=max_name_len or 0,
        ))


@dataclass
class FileNode(BaseNode):
    def __init__(self, name: str, suffix: str, node_path: Path, size: HumanBytes, mtime: HumanTimestamp, icon: str, level: int):
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
        return False


@dataclass
class DirNode(BaseNode):
    def __init__(self, name: str, node_path: Path, size: HumanBytes, mtime: HumanTimestamp, level: int, children: list["BaseNode"]):
        super().__init__(name, node_path, size, mtime, "📁", level)
        self.children: list["BaseNode"] = children

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

        child_hashes = []
        for child in sorted(self.children, key=lambda c: (not c.is_dir(), c.name)):
            h = child.hash
            if not h:
                continue
            tag = "D" if child.is_dir() else "F"
            entry = f"{tag}:{child.name}:{h}".encode("utf-8")
            child_hashes.append(entry)

        if not child_hashes:
            combined = b"[EMPTY]"
        else:
            combined = b"".join(child_hashes)

        return _hash_bytes(combined)

    def is_dir(self) -> bool:
        return True