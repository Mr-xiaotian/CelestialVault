# `celestialvault.tools.Utilities`

## 源文件

[src/celestialvault/tools/Utilities.py](../../src/celestialvault/tools/Utilities.py)

## 模块说明

通用工具模块，提供时间格式化、函数相等性比较、对象内存大小计算、函数执行时间记录等实用功能。

## 导入依赖

```python
import sys
import time
from collections.abc import Callable, Container, Mapping
from functools import wraps
from time import localtime, strftime
from types import FunctionType

from ..instances.inst_units import HumanBytes
```

## 顶层函数

### `get_format_time`

- 签名: `def get_format_time(now_time=None) -> str`
- 说明: 获取格式化的时间字符串
- 参数:
  - `now_time`: 时间戳，默认为当前时间
- 返回值: 格式化的时间字符串，如 "2024-01-01 12:00:00"
- 用法示例:
  ```python
  from celestialvault.tools.Utilities import get_format_time

  print(get_format_time())  # "2024-01-01 12:00:00"

  import time
  print(get_format_time(time.time() - 3600))  # 一小时前
  ```
- 关联: `log_time`

### `functions_are_equal`

- 签名: `def functions_are_equal(func1: Callable, func2: Callable) -> bool`
- 说明: 判断两个函数是否相等，通过比较字节码、常量、变量名等属性
- 参数:
  - `func1` (Callable): 第一个函数
  - `func2` (Callable): 第二个函数
- 返回值: 如果两个函数相等返回 True，否则返回 False
- 用法示例:
  ```python
  from celestialvault.tools.Utilities import functions_are_equal

  def add(a, b): return a + b
  def add2(a, b): return a + b

  print(functions_are_equal(add, add2))  # True
  ```
- 关联: `celestialvault.tools.ListDictTools.list_replace`

### `get_total_size`

- 签名: `def get_total_size(obj, seen=None) -> HumanBytes`
- 说明: 递归计算对象及其内部元素的总内存大小
- 参数:
  - `obj`: 任意 Python 对象
  - `seen`: 用于记录已经访问过的对象，避免重复计算
- 返回值: 对象占用的总内存大小（HumanBytes）
- 用法示例:
  ```python
  from celestialvault.tools.Utilities import get_total_size

  data = {"key": [1, 2, 3], "nested": {"a": "hello"}}
  size = get_total_size(data)
  print(f"Total size: {size}")
  ```
- 关联: 无

### `log_time`

- 签名: `def log_time(func: Callable) -> Callable`
- 说明: 记录函数执行时间的装饰器
- 参数:
  - `func` (Callable): 要装饰的函数
- 返回值: 装饰后的函数
- 用法示例:
  ```python
  from celestialvault.tools.Utilities import log_time

  @log_time
  def heavy_task():
      import time
      time.sleep(1)
      return "done"

  result = heavy_task()
  # [heavy_task] 开始执行: 2024-01-01 12:00:00
  # [heavy_task] 结束执行: 2024-01-01 12:00:01
  # [heavy_task] 总耗时: 1.0012 秒
  ```
- 关联: `get_format_time`
