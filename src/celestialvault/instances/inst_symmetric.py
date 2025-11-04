import random
from typing import Dict, Iterator, Iterable, Tuple, Optional, Generic, TypeVar

T = TypeVar("T")

class SymmetricMap(Generic[T]):
    """
    一对一双向映射：元素出现在映射中意味着它与唯一的伙伴绑定。
    语义约定：
    - 迭代/keys() 仅遍历“代表键”（pairs 的键），每对只出现一次。
    - x in m 表示 x 在任意一侧出现。
    """
    __slots__ = ("pairs", "reverse", "_allow_self")

    def __init__(self, allow_self: bool = False):
        self.pairs: Dict[T, T] = {}     # a -> b （代表键）
        self.reverse: Dict[T, T] = {}   # b -> a
        self._allow_self = allow_self

    def __contains__(self, x: T) -> bool:
        d = self.pairs
        return x in d or x in self.reverse

    def __len__(self) -> int:
        return len(self.pairs)

    # —— 基础操作 ——
    def __setitem__(self, a: T, b: T) -> None:
        if not self._allow_self and a == b:
            raise ValueError("Self-pair is not allowed (a == b).")

        # 已有相同配对则幂等返回
        existing = self.get(a)
        if existing == b:
            return

        # a 或 b 若已配对，先解绑
        if a in self:
            self.__delitem__(a)
        if b in self:
            self.__delitem__(b)

        self.pairs[a] = b
        self.reverse[b] = a
        # 调试期可启用：
        # self._check_invariants()

    def __getitem__(self, x: T) -> T:
        if x in self.pairs:
            return self.pairs[x]
        if x in self.reverse:
            return self.reverse[x]
        raise KeyError(f"{x!r} not found")

    def __delitem__(self, x: T) -> None:
        # 直接分支 + pop，避免借道 __getitem__
        if x in self.pairs:
            y = self.pairs.pop(x)
            del self.reverse[y]
            return
        if x in self.reverse:
            y = self.reverse.pop(x)
            del self.pairs[y]
            return
        raise KeyError(f"{x!r} not found")
    
    def pop(self, x: T) -> T:
        """移除并返回与 x 绑定的伙伴。"""
        if x in self.pairs:
            y = self.pairs.pop(x)
            del self.reverse[y]
            return y
        if x in self.reverse:
            y = self.reverse.pop(x)
            del self.pairs[y]
            return y
        raise KeyError(f"{x!r} not found")
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SymmetricMap):
            return NotImplemented
        return self.pairs == other.pairs or self.pairs == other.reverse

    # —— 视图/便捷方法 ——
    def get(self, x: T, default: Optional[T] = None) -> Optional[T]:
        if x in self.pairs:
            return self.pairs[x]
        if x in self.reverse:
            return self.reverse[x]
        return default

    def keys(self) -> Iterable[T]:
        return self.pairs.keys()  # 代表键

    def values(self) -> Iterable[T]:
        return self.pairs.values()  # 代表值（对应 keys 的伙伴）

    def items(self) -> Iterable[Tuple[T, T]]:
        return self.pairs.items()  # 每对一次

    def __iter__(self) -> Iterator[T]:
        return iter(self.pairs)  # 与 dict 语义一致

    def clear(self) -> None:
        self.pairs.clear()
        self.reverse.clear()

    def random_pair(self) -> T:
        if not self.pairs:
            raise IndexError("Cannot choose from an empty SymmetricMap")
        all_items = list(self.pairs.keys()) + list(self.pairs.values())
        random_item = random.choice(all_items)
        return random_item, self[random_item]

    def __repr__(self) -> str:
        """稳定、可读的输出"""
        pairs_sorted = sorted(self.pairs.items(), key=lambda kv: (repr(kv[0]), repr(kv[1])))
        body = ", ".join(f"{a!r} <-> {b!r}" for a, b in pairs_sorted)
        return f"SymmetricMap({body})"
    
    def __str__(self) -> str:
        """
        人类友好的输出版本，比 __repr__ 更简洁。
        """
        if not self.pairs:
            return "SymmetricMap()"
        return "{" + ", ".join(f"{a} <-> {b}" for a, b in self.pairs.items()) + "}"

    # —— 工厂方法 —— 
    @classmethod
    def from_dict(cls, d: Dict[T, T], allow_self: bool = False) -> "SymmetricMap[T]":
        """
        从普通字典构建一个 SymmetricMap。
        注意：若输入字典包含重复或冲突配对（如 a->b 与 b->c），
        后者将覆盖前者，以保证一对一关系。

        :param d: 一个普通字典，键值对将被视为对称映射的配对。
        :param allow_self: 是否允许 a <-> a 自配对。
        """
        m = cls(allow_self=allow_self)
        for a, b in d.items():
            m[a] = b
        return m
    
    @classmethod
    def from_pairs(cls, iterable: Iterable[Tuple[T, T]], allow_self: bool = False):
        m = cls(allow_self=allow_self)
        for a, b in iterable:
            m[a] = b
        return m

    # —— 调试工具 ——
    def _check_invariants(self) -> None:
        assert len(self.pairs) == len(self.reverse)
        for a, b in self.pairs.items():
            assert self.reverse.get(b) == a
