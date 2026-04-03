# instances/inst_units.py

## 源文件
- `src/celestialvault/instances/inst_units.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- `from __future__ import annotations`
- `import re`
- `from datetime import datetime`
- `from zoneinfo import ZoneInfo`

## 模块常量
- 无

## 顶层函数
- 无

## 类
### `HumanBytes`
- 继承: `int`
- 说明: 一个基于 int 的类，自动以人类可读格式显示字节大小
- 方法:
  - `def __new__(cls, value)`
  - `def _parse_human(cls, text: str) -> int`
  - `def _to_human(self) -> str`
  - `def __str__(self)`
  - `def __repr__(self)`
  - `def _wrap(self, result)`
  - `def __add__(self, other)`
  - `def __sub__(self, other)`
  - `def __mul__(self, other)`
  - `def __floordiv__(self, other)`
  - `def __truediv__(self, other)`
  - `def __mod__(self, other)`

### `HumanTime`
- 继承: `float`
- 说明: 表示可读的时间长度（duration），单位为秒（float）。
- 运算行为与 float 一致，可加减乘除
- 打印时自动格式化为 1d 2h 3m 4.56s 形式
- 支持从字符串初始化，如 "1d 2h 3m 4.56s"
- 方法:
  - `def __new__(cls, value: str | float | int)`
  - `def _parse_human(cls, text: str) -> float`
  - `def _to_human(self, precision = 2, show_zero = False) -> str`
  - `def __str__(self)`
  - `def __repr__(self)`
  - `def _wrap(self, result)`
  - `def __add__(self, other)`
  - `def __sub__(self, other)`
  - `def __mul__(self, other)`
  - `def __truediv__(self, other)`
  - `def __floordiv__(self, other)`
  - `def __radd__(self, other)`
  - `def __rsub__(self, other)`
  - `def __rmul__(self, other)`

### `HumanTimestamp`
- 继承: `float`
- 说明: 基于 float 的 UNIX 时间戳（单位：秒，支持小数）。
- 显示（print/str）为人类可读的本地时间（含时区偏移）
- 默认时区：Asia/Shanghai；可用 with_tz() 切换视图时区
- 加/减『秒数』返回 HumanTimestamp；两个 HumanTimestamp 相减返回 HumanTime
- 方法:
  - `def __new__(cls, value: float | int | str | datetime, tz = None)`
  - `def tz(self)`
  - `def with_tz(self, tz) -> 'HumanTimestamp'`
  - `def to_datetime(self, tz = None) -> datetime`
  - `def to_iso(self, tz = None, timespec: str = 'milliseconds') -> str`
  - `def __str__(self)`
  - `def __repr__(self)`
  - `def _wrap(self, epoch: float) -> 'HumanTimestamp'`
  - `def __add__(self, other)`
  - `def __radd__(self, other)`
  - `def __sub__(self, other)`
  - `def __rsub__(self, other)`
  - `def __mul__(self, other)`
  - `def __rmul__(self, other)`
  - `def __truediv__(self, other)`
  - `def __floordiv__(self, other)`
  - `def now(cls, tz = None) -> 'HumanTimestamp'`
