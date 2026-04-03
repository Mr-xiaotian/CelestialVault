# tools/Utilities.py

## 源文件
- `src/celestialvault/tools/Utilities.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- `import sys`
- `import time`
- `from collections.abc import Callable, Container, Mapping`
- `from functools import wraps`
- `from time import localtime, strftime`
- `from types import FunctionType`
- `from ..instances.inst_units import HumanBytes`

## 模块常量
- 无

## 顶层函数
### `get_format_time`
- 签名: `def get_format_time(now_time = None) -> str`
- 说明: 获取当前时间
:return:

### `functions_are_equal`
- 签名: `def functions_are_equal(func1: Callable, func2: Callable) -> bool`
- 说明: 判断两个函数是否相等

:param func1:
:param func2:
:return:

### `get_total_size`
- 签名: `def get_total_size(obj, seen = None) -> HumanBytes`
- 说明: 递归计算对象及其内部元素的总内存大小。
:param obj: 任意 Python 对象。
:param seen: 用于记录已经访问过的对象，避免重复计算。
:return: 对象占用的总内存大小（字节数）。

### `log_time`
- 签名: `def log_time(func: Callable) -> Callable`
- 说明: 记录函数执行时间的装饰器
:param func: 要装饰的函数
:return:

## 类
- 无
