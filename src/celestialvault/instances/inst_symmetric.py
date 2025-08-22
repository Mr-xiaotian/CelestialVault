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
        return x in self.pairs or x in self.reverse

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

    def __repr__(self) -> str:
        # 稳定、可读的输出
        pairs_sorted = sorted(self.pairs.items(), key=lambda kv: (repr(kv[0]), repr(kv[1])))
        body = ", ".join(f"{a!r} <-> {b!r}" for a, b in pairs_sorted)
        return f"SymmetricMap({body})"

    # —— 调试工具 ——
    def _check_invariants(self) -> None:
        assert len(self.pairs) == len(self.reverse)
        for a, b in self.pairs.items():
            assert self.reverse.get(b) == a
