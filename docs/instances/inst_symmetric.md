# instances/inst_symmetric.py

## 源文件
- `src/celestialvault/instances/inst_symmetric.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- `import random`
- `from collections.abc import Iterator, Iterable`
- `from typing import Generic, TypeVar`

## 模块常量
- `T`

## 顶层函数
- 无

## 类
### `SymmetricMap`
- 继承: `Generic[T]`
- 说明: 一对一双向映射：元素出现在映射中意味着它与唯一的伙伴绑定。
语义约定：
- 迭代/keys() 仅遍历“代表键”（pairs 的键），每对只出现一次。
- x in m 表示 x 在任意一侧出现。
- 方法:
  - `def __init__(self, allow_self: bool = False)`
  - `def __contains__(self, x: T) -> bool`
  - `def __len__(self) -> int`
  - `def __setitem__(self, a: T, b: T) -> None`
  - `def __getitem__(self, x: T) -> T`
  - `def __delitem__(self, x: T) -> None`
  - `def pop(self, x: T) -> T`
  - `def __eq__(self, other: object) -> bool`
  - `def get(self, x: T, default: T | None = None) -> T | None`
  - `def keys(self) -> Iterable[T]`
  - `def values(self) -> Iterable[T]`
  - `def items(self) -> Iterable[tuple[T, T]]`
  - `def __iter__(self) -> Iterator[T]`
  - `def clear(self) -> None`
  - `def random_pair(self, mode: str = 'any') -> tuple[T, T]`
  - `def __repr__(self) -> str`
  - `def __str__(self) -> str`
  - `def from_dict(cls, d: dict[T, T], allow_self: bool = False) -> 'SymmetricMap[T]'`
  - `def from_pairs(cls, iterable: Iterable[tuple[T, T]], allow_self: bool = False)`
  - `def _check_invariants(self) -> None`
