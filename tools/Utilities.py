import sys, re
from types import FunctionType
from typing import Callable
from collections.abc import Mapping, Container
from time import strftime, localtime


def get_now_time():
    """
    获取当前时间
    :return:
    """
    return strftime("%Y-%m-%d", localtime())

def functions_are_equal(func1: Callable, func2: Callable) -> bool:
    """
    判断两个函数是否相等

    :param func1:
    :param func2:
    :return:
    """
    if not (isinstance(func1, FunctionType) and isinstance(func2, FunctionType)):
        return False
    return (func1.__code__.co_code == func2.__code__.co_code and
            func1.__code__.co_consts == func2.__code__.co_consts and
            func1.__code__.co_varnames == func2.__code__.co_varnames and
            func1.__code__.co_argcount == func2.__code__.co_argcount and
            func1.__defaults__ == func2.__defaults__ and
            func1.__closure__ == func2.__closure__)

def bytes_to_human_readable(size_in_bytes: int) -> str:
    """
    将字节大小转换为人类可读的格式
    :param size_in_bytes:
    :return: 人类可读格式的大小 (str)，如 "1GB 512MB"
    """
    if size_in_bytes <= 0:
        return "0B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    result = []
    
    for unit in reversed(units):
        unit_size = 1024 ** units.index(unit)
        if size_in_bytes >= unit_size:
            value = size_in_bytes // unit_size
            size_in_bytes %= unit_size
            result.append(f"{value}{unit}")
    
    return ' '.join(result)

def human_readable_to_bytes(human_readable: str) -> int:
    """
    将人类可读的大小字符串转换为字节数。
    :param human_readable: 人类可读格式的大小 (str)，如 "1GB 512MB"
    :return: 字节大小 (int)
    """
    units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
    size_in_bytes = 0

    matches = re.findall(r'(\d+(?:\.\d+)?)([A-Za-z]+)', human_readable)
    if not matches:
        raise ValueError(f"无法解析输入: {human_readable}")

    for value, unit in matches:
        unit = unit.upper()
        if unit not in units:
            raise ValueError(f"未知单位: {unit}")
        size_in_bytes += float(value) * units[unit]

    return int(size_in_bytes)

def get_total_size(obj, seen=None):
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
    size = sys.getsizeof(obj)

    # 如果对象是映射类型（如 dict）
    if isinstance(obj, Mapping):
        size += sum(get_total_size(k, seen) + get_total_size(v, seen) for k, v in obj.items())

    # 如果对象是容器类型（如 list、tuple、set 等），但不包括字符串和字节类型
    elif isinstance(obj, Container) and not isinstance(obj, (str, bytes, bytearray)):
        size += sum(get_total_size(i, seen) for i in obj)

    return size

