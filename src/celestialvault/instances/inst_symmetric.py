import random
from collections.abc import Iterable, Iterator
from typing import Generic, TypeVar

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
        self.pairs: dict[T, T] = {}  # a -> b （代表键）
        self.reverse: dict[T, T] = {}  # b -> a
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
        """
        移除并返回与 x 绑定的伙伴。

        :param x: 要移除的元素。
        :return: 与 x 绑定的伙伴元素。
        """
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
    def get(self, x: T, default: T | None = None) -> T | None:
        """
        获取与 x 绑定的伙伴，若不存在则返回 default。

        :param x: 要查找的元素。
        :param default: 未找到时返回的默认值。
        :return: 与 x 绑定的伙伴，或 default。
        """
        if x in self.pairs:
            return self.pairs[x]
        if x in self.reverse:
            return self.reverse[x]
        return default

    def keys(self) -> Iterable[T]:
        """
        返回所有代表键（每对只出现一次）。

        :return: 代表键的可迭代对象。
        """
        return self.pairs.keys()  # 代表键

    def values(self) -> Iterable[T]:
        """
        返回所有代表值（代表键对应的伙伴）。

        :return: 代表值的可迭代对象。
        """
        return self.pairs.values()  # 代表值（对应 keys 的伙伴）

    def items(self) -> Iterable[tuple[T, T]]:
        """
        返回所有配对的 (键, 值) 元组，每对只出现一次。

        :return: 配对元组的可迭代对象。
        """
        return self.pairs.items()  # 每对一次

    def __iter__(self) -> Iterator[T]:
        return iter(self.pairs)  # 与 dict 语义一致

    def clear(self) -> None:
        """
        清空所有配对关系。
        """
        self.pairs.clear()
        self.reverse.clear()

    def random_pair(self, mode: str = "any") -> tuple[T, T]:
        """
        随机返回一对配对。

        :param mode: 选择模式，可选 'forward'、'backward' 或 'any'。
        :return: 随机选出的配对元组 (元素, 伙伴)。
        """
        if not self.pairs:
            raise IndexError("Cannot choose from an empty SymmetricMap")

        if mode == "forward":
            return random.choice(list(self.pairs.items()))
        elif mode == "backward":
            return random.choice(list(self.reverse.items()))
        elif mode == "any":
            # 从所有元素中随机选取一个作为起点
            all_items = list(self.pairs.keys()) + list(self.pairs.values())
            random_item = random.choice(all_items)
            return random_item, self[random_item]
        else:
            raise ValueError(
                f"Invalid mode: {mode!r} (expected 'forward' | 'backward' | 'any')"
            )

    def __repr__(self) -> str:
        """稳定、可读的输出"""
        pairs_sorted = sorted(
            self.pairs.items(), key=lambda kv: (repr(kv[0]), repr(kv[1]))
        )
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
    def from_dict(cls, d: dict[T, T], allow_self: bool = False) -> "SymmetricMap[T]":
        """
        从普通字典构建一个 SymmetricMap。

        :param d: 包含配对关系的字典。
        :param allow_self: 是否允许自身配对。
        :return: 构建的 SymmetricMap 实例。
        """
        m = cls(allow_self=allow_self)
        for a, b in d.items():
            m[a] = b
        return m

    @classmethod
    def from_pairs(cls, iterable: Iterable[tuple[T, T]], allow_self: bool = False):
        """
        从可迭代对象构建一个 SymmetricMap。

        :param iterable: 包含 (a, b) 配对元组的可迭代对象。
        :param allow_self: 是否允许自身配对。
        :return: 构建的 SymmetricMap 实例。
        """
        m = cls(allow_self=allow_self)
        for a, b in iterable:
            m[a] = b
        return m

    # —— 调试工具 ——
    def _check_invariants(self) -> None:
        assert len(self.pairs) == len(self.reverse)
        for a, b in self.pairs.items():
            assert self.reverse.get(b) == a
