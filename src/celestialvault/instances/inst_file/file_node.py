import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from ...instances.inst_units import HumanBytes, HumanTimestamp
from ...tools.FileOperations import (
    get_file_hash,
    get_file_mtime,
    get_dir_mtime,
    align_width,
)


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
        """
        将节点格式化为带缩进、前缀和后缀的字符串表示。

        :param indent: 缩进字符串。
        :param prefix: 节点名称前的前缀。
        :param suffix: 节点名称后的后缀。
        :return: 格式化后的节点字符串。
        """
        return f"{indent}{self.icon}{prefix} {align_width(self.name, self.max_name_len)}\t{suffix}"

    def __repr__(self):
        return self.to_string(
            indent="    " * self.level,
            # prefix = f"[{self.node_path.parent.as_posix()}]",
            # prefix = f"[{self.mtime}]",
            suffix=f"({self.size})",
        )

    @property
    def hash(self) -> str:
        """惰性计算文件哈希"""
        # 排除统计节点
        if self.name.startswith("[") and (
            self.name.endswith("排除的目录]") or self.name.endswith("排除的文件]")
        ):
            self._hash = ""
            return self._hash

        if not self.node_path.exists():
            self._hash = ""
            return self._hash

        # 检查是否需要重新计算
        new_mtime = (
            get_dir_mtime(self.node_path)
            if self.is_dir
            else get_file_mtime(self.node_path)
        )
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

