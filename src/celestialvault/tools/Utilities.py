import re
import sys
import time
from collections.abc import Container, Mapping
from functools import wraps
from time import localtime, strftime
from types import FunctionType
from typing import Callable

from ..instances.inst_units import HumanBytes

def get_format_time(now_time=None):
    """
    获取当前时间
    :return:
    """
    now_time = localtime(now_time) or localtime()
    return strftime("%Y-%m-%d %H:%M:%S", now_time)


def functions_are_equal(func1: Callable, func2: Callable) -> bool:
    """
    判断两个函数是否相等

    :param func1:
    :param func2:
    :return:
    """
    if not (isinstance(func1, FunctionType) and isinstance(func2, FunctionType)):
        return False
    return (
        func1.__code__.co_code == func2.__code__.co_code
        and func1.__code__.co_consts == func2.__code__.co_consts
        and func1.__code__.co_varnames == func2.__code__.co_varnames
        and func1.__code__.co_argcount == func2.__code__.co_argcount
        and func1.__defaults__ == func2.__defaults__
        and func1.__closure__ == func2.__closure__
    )


def get_total_size(obj, seen=None) -> HumanBytes:
    """
    递归计算对象及其内部元素的总内存大小。
    :param obj: 任意 Python 对象。
    :param seen: 用于记录已经访问过的对象，避免重复计算。
    :return: 对象占用的总内存大小（字节数）。
    """
    if seen is None:
        seen = set()

    obj_id = id(obj)
    if obj_id in seen:  # 如果对象已被处理，直接返回 0
        return 0

    # 将当前对象标记为已处理
    seen.add(obj_id)

    # 基础大小
    size = HumanBytes(sys.getsizeof(obj))

    # 如果对象是映射类型（如 dict）
    if isinstance(obj, Mapping):
        size += sum(
            get_total_size(k, seen) + get_total_size(v, seen) for k, v in obj.items()
        )

    # 如果对象是容器类型（如 list、tuple、set 等），但不包括字符串和字节类型
    elif isinstance(obj, Container) and not isinstance(obj, (str, bytes, bytearray)):
        size += sum(get_total_size(i, seen) for i in obj)

    return size


def log_time(func: Callable) -> Callable:
    """
    记录函数执行时间的装饰器
    :param func: 要装饰的函数
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        print(f"[{func.__name__}] 开始执行: {get_format_time(start_time)}")

        result = func(*args, **kwargs)

        end_time = time.time()
        print(f"[{func.__name__}] 结束执行: {get_format_time(end_time)}")
        print(f"[{func.__name__}] 总耗时: {end_time - start_time:.4f} 秒")
        return result

    return wrapper
