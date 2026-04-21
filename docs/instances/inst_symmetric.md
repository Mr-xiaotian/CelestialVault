# `celestialvault.instances.inst_symmetric`

## 源文件 - `src/celestialvault/instances/inst_symmetric.py`

## 模块说明

提供一对一双向映射类 `SymmetricMap`，支持泛型。元素出现在映射中即与唯一的伙伴绑定。迭代和 `keys()` 仅遍历代表键（每对只出现一次），`x in m` 判断 x 是否在任意一侧出现。

## 导入依赖

- `random` - 随机选取配对
- `collections.abc.Iterator`, `collections.abc.Iterable` - 类型协议
- `typing.Generic`, `typing.TypeVar` - 泛型支持
- `T = TypeVar("T")` - 泛型类型变量

## 类

### `SymmetricMap`

- 继承: `Generic[T]`
- 说明: 一对一双向映射，通过 `pairs`（正向）和 `reverse`（反向）两个内部字典维护双向关系。赋值时若元素已有配对则先自动解绑。

- `__slots__`: `('pairs', 'reverse', '_allow_self')`

- 构造函数: `__init__(self, allow_self: bool = False)`
  - 参数:
    - `allow_self` (`bool`): 是否允许自身配对（`a == b`），默认 `False`。
  - 属性:
    - `self.pairs` (`dict[T, T]`): 正向映射（代表键 -> 代表值）。
    - `self.reverse` (`dict[T, T]`): 反向映射（代表值 -> 代表键）。

- 方法:

  #### `__setitem__(self, a, b)`
  - 签名: `__setitem__(self, a: T, b: T) -> None`
  - 说明: 设置配对关系 `a <-> b`。若 `a == b` 且不允许自身配对则抛出 `ValueError`。若 `a` 或 `b` 已有配对则先解绑。已有相同配对时幂等返回。

  #### `__getitem__(self, x)`
  - 签名: `__getitem__(self, x: T) -> T`
  - 说明: 获取 x 的伙伴。在 pairs 和 reverse 中查找。
  - 异常: `KeyError` - x 未找到。

  #### `__delitem__(self, x)`
  - 签名: `__delitem__(self, x: T) -> None`
  - 说明: 删除 x 所在的配对（同时清除正向和反向引用）。
  - 异常: `KeyError` - x 未找到。

  #### `__contains__(self, x)`
  - 签名: `__contains__(self, x: T) -> bool`
  - 说明: 判断 x 是否在任意一侧出现。

  #### `__len__(self)`
  - 签名: `__len__(self) -> int`
  - 说明: 返回配对数量。

  #### `__eq__(self, other)`
  - 签名: `__eq__(self, other: object) -> bool`
  - 说明: 比较两个 SymmetricMap 是否等价（正向或反向字典相等）。

  #### `__iter__(self)`
  - 签名: `__iter__(self) -> Iterator[T]`
  - 说明: 迭代所有代表键（与 dict 语义一致）。

  #### `pop(self, x)`
  - 签名: `pop(self, x: T) -> T`
  - 说明: 移除并返回与 x 绑定的伙伴。
  - 异常: `KeyError` - x 未找到。

  #### `get(self, x, default=None)`
  - 签名: `get(self, x: T, default: T | None = None) -> T | None`
  - 说明: 获取与 x 绑定的伙伴，若不存在则返回 default。

  #### `keys(self)`
  - 签名: `keys(self) -> Iterable[T]`
  - 说明: 返回所有代表键（每对只出现一次）。

  #### `values(self)`
  - 签名: `values(self) -> Iterable[T]`
  - 说明: 返回所有代表值（代表键对应的伙伴）。

  #### `items(self)`
  - 签名: `items(self) -> Iterable[tuple[T, T]]`
  - 说明: 返回所有配对的 (键, 值) 元组，每对只出现一次。

  #### `clear(self)`
  - 签名: `clear(self) -> None`
  - 说明: 清空所有配对关系。

  #### `random_pair(self, mode='any')`
  - 签名: `random_pair(self, mode: str = 'any') -> tuple[T, T]`
  - 说明: 随机返回一对配对。
  - 参数:
    - `mode` (`str`): 选择模式:
      - `'forward'`: 从 pairs 中随机选取。
      - `'backward'`: 从 reverse 中随机选取。
      - `'any'`: 从所有元素中随机选取一个，返回其配对。
  - 返回值: 随机选出的配对元组 `(元素, 伙伴)`。
  - 异常: `IndexError` - 映射为空时抛出；`ValueError` - mode 无效时抛出。

  #### `__repr__(self)`
  - 说明: 稳定、可读的输出，按键排序显示所有配对。

  #### `__str__(self)`
  - 说明: 人类友好的输出版本，如 `{a <-> b, c <-> d}`。

  #### `from_dict(cls, d, allow_self=False)` (类方法)
  - 签名: `from_dict(cls, d: dict[T, T], allow_self: bool = False) -> SymmetricMap[T]`
  - 说明: 从普通字典构建一个 SymmetricMap。

  #### `from_pairs(cls, iterable, allow_self=False)` (类方法)
  - 签名: `from_pairs(cls, iterable: Iterable[tuple[T, T]], allow_self: bool = False) -> SymmetricMap[T]`
  - 说明: 从可迭代对象构建一个 SymmetricMap。

  #### `_check_invariants(self)`
  - 说明: 调试工具，验证 pairs 和 reverse 的长度一致且互为反映射。

- 用法示例:

```python
from celestialvault.instances.inst_symmetric import SymmetricMap

# 从字典构建
m = SymmetricMap.from_dict({"apple": "苹果", "cat": "猫"})

# 双向查找
print(m["apple"])   # "苹果"
print(m["苹果"])    # "apple"

# 设置和删除
m["dog"] = "狗"
del m["cat"]

# 检查存在性
print("dog" in m)   # True
print("狗" in m)    # True

# 随机配对
pair = m.random_pair(mode="any")
print(pair)  # 如 ("apple", "苹果")

# 遍历
for key in m:
    print(f"{key} <-> {m[key]}")

# 从配对列表构建
m2 = SymmetricMap.from_pairs([("a", "1"), ("b", "2")])
print(m2)  # {a <-> 1, b <-> 2}
```

- 关联: 被 `inst_quiz.DictationQuiz` 使用作为单词映射表。
