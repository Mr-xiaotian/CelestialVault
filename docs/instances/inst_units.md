# `celestialvault.instances.inst_units`

## 源文件 - `src/celestialvault/instances/inst_units.py`

## 模块说明

提供三种人类可读单位类型：`HumanBytes`（字节大小）、`HumanTime`（时间长度）和 `HumanTimestamp`（时间戳），均继承自 Python 内置数值类型，运算行为与底层类型一致，打印时自动格式化为人类可读形式。

## 导入依赖

- `from __future__ import annotations`
- `re` - 正则表达式（解析字符串）
- `datetime.datetime` - 日期时间
- `zoneinfo.ZoneInfo` - 时区信息

## 类

### `HumanBytes`

- 继承: `int`
- 说明: 基于 `int` 的字节大小类，自动以人类可读格式显示（如 `"1GB 512MB"`）。支持从字符串或数字初始化。

- 构造函数: `__new__(cls, value)`
  - 参数:
    - `value` (`int | str`): 字节数或可读字符串（如 `"1GB 512MB"`、`"1.5 GB"`）。

- 类属性:
  - `_units` (`list[str]`): `["B", "KB", "MB", "GB", "TB"]`
  - `_unit_map` (`dict`): 单位到字节数的映射（1KB=1024, 1MB=1024^2, ...）。

- 方法:
  - `_parse_human(cls, text: str) -> int` (类方法): 解析人类可读字符串为字节数。支持组合格式如 `"1GB 512MB"`。
  - `_to_human(self) -> str`: 转换为人类可读字符串。
  - `__str__`, `__repr__`: 人类可读显示。
  - `__add__`, `__sub__`, `__mul__`, `__floordiv__`, `__truediv__`, `__mod__`: 运算后保持 `HumanBytes` 类型。

- 用法示例:

```python
from celestialvault.instances.inst_units import HumanBytes

size = HumanBytes(1073741824)
print(size)  # "1GB"

size = HumanBytes("1GB 512MB")
print(int(size))  # 1610612736

total = HumanBytes(1024) + HumanBytes(2048)
print(total)  # "3KB"
```

- 关联: 被 `inst_file.file_node`、`inst_file.file_tree`、`inst_file.file_diff` 广泛使用表示文件大小。

---

### `HumanTime`

- 继承: `float`
- 说明: 表示可读的时间长度（duration），单位为秒。打印时自动格式化为 `"1d 2h 3m 4.56s"` 形式。支持从字符串初始化。

- 构造函数: `__new__(cls, value: str | float | int)`
  - 参数:
    - `value` (`str | float | int`): 秒数或可读字符串（如 `"1d 2h 3m 4s"`）。

- 类属性:
  - `_units` (`list[tuple[str, int]]`): `[("d", 86400), ("h", 3600), ("m", 60), ("s", 1)]`

- 方法:
  - `_parse_human(cls, text: str) -> float` (类方法): 解析人类可读字符串为秒数。
  - `_to_human(self, precision=2, show_zero=False) -> str`: 格式化为可读字符串。
    - 参数:
      - `precision` (`int`): 小数秒的精度，默认 `2`。
      - `show_zero` (`bool`): 是否显示零值单位，默认 `False`。
  - `__str__`, `__repr__`: 人类可读显示。
  - `__add__`, `__sub__`, `__mul__`, `__truediv__`, `__floordiv__`, `__radd__`, `__rsub__`, `__rmul__`: 运算后保持 `HumanTime` 类型。

- 用法示例:

```python
from celestialvault.instances.inst_units import HumanTime

t = HumanTime(3661.5)
print(t)  # "1h 1m 1.50s"

t = HumanTime("2h 30m")
print(float(t))  # 9000.0

total = HumanTime(60) + HumanTime(120)
print(total)  # "3m"
```

- 关联: 被 `HumanTimestamp.__sub__` 返回作为时间差；被 `inst_file` 模块使用表示时间间隔。

---

### `HumanTimestamp`

- 继承: `float`
- 说明: 基于 `float` 的 UNIX 时间戳（单位：秒，支持小数）。显示为人类可读的本地时间（含时区偏移），默认时区 `Asia/Shanghai`。支持时区切换、datetime 转换和 ISO 8601 输出。

- 构造函数: `__new__(cls, value: float | int | str | datetime, tz=None)`
  - 参数:
    - `value` (`float | int | str | datetime`): 时间戳数值、ISO 字符串（如 `"2025-01-01 00:00:00"`）或 `datetime` 对象。字符串支持纯数字（作为时间戳）和 ISO 格式。
    - `tz` (`ZoneInfo | None`): 显示时区，默认 `Asia/Shanghai`。
  - 异常: `ValueError` - 无法解析字符串时抛出；`TypeError` - 不支持的初始化类型时抛出。

- 类属性:
  - `DEFAULT_TZ`: `ZoneInfo("Asia/Shanghai")`

- 方法:

  #### `tz` (属性)
  - 返回当前显示时区。

  #### `with_tz(self, tz)`
  - 签名: `with_tz(self, tz) -> HumanTimestamp`
  - 说明: 返回一个仅改变显示时区的新对象（纪元秒不变）。

  #### `to_datetime(self, tz=None)`
  - 签名: `to_datetime(self, tz=None) -> datetime`
  - 说明: 转换为 `datetime` 对象。

  #### `to_iso(self, tz=None, timespec='milliseconds')`
  - 签名: `to_iso(self, tz=None, timespec: str = 'milliseconds') -> str`
  - 说明: 返回 ISO 8601 字符串（含偏移）。

  #### `now(cls, tz=None)` (类方法)
  - 签名: `now(cls, tz=None) -> HumanTimestamp`
  - 说明: 返回当前时间的 HumanTimestamp。

  #### 运算语义
  - `时间戳 + 秒数/HumanTime -> HumanTimestamp`
  - `时间戳 + 时间戳 -> TypeError`
  - `时间戳 - 秒数/HumanTime/HumanTimestamp -> HumanTime`（时间差）
  - `时间戳 * 数字 -> HumanTimestamp`
  - `时间戳 / 数字 -> HumanTimestamp`
  - `时间戳 / 时间戳 -> float`

- 用法示例:

```python
from celestialvault.instances.inst_units import HumanTimestamp, HumanTime
from zoneinfo import ZoneInfo

# 当前时间
now = HumanTimestamp.now()
print(now)  # "2025-03-25T12:49:22.104+08:00 (CST)"

# 从字符串创建
ts = HumanTimestamp("2025-01-01 00:00:00")
print(ts.to_iso())

# 时区切换
ts_tokyo = ts.with_tz(ZoneInfo("Asia/Tokyo"))
print(ts_tokyo)

# 时间差
diff = HumanTimestamp.now() - ts
print(diff)  # 如 "83d 12h 49m 22.10s"（HumanTime 类型）

# 加秒数
future = now + HumanTime("1h 30m")
print(future)
```

- 关联: 被 `inst_file.file_node`、`inst_file.file_tree`、`inst_file.file_diff` 广泛使用表示文件修改时间。`HumanTime` 作为时间差的返回类型。
