import types, sys
import random
from mpmath import mp
from typing import Callable
from time import strftime, localtime


def get_now_time():
    return strftime("%Y-%m-%d", localtime())

def functions_are_equal(func1: Callable, func2: Callable) -> bool:
    """
    判断两个函数是否相等

    :param func1:
    :param func2:
    :return:
    """
    if not isinstance(func1, types.FunctionType) or not isinstance(func2, types.FunctionType):
        return False
    return (func1.__code__.co_code == func2.__code__.co_code and
            func1.__code__.co_consts == func2.__code__.co_consts and
            func1.__code__.co_varnames == func2.__code__.co_varnames and
            func1.__code__.co_argcount == func2.__code__.co_argcount and
            func1.__defaults__ == func2.__defaults__ and
            func1.__closure__ == func2.__closure__)

def bytes_to_human_readable(size_in_bytes):
    """
    将字节大小转换为人类可读的格式
    :param size_in_bytes:
    :return:
    """
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    result = []
    
    for unit in reversed(units):
        unit_size = 1024 ** units.index(unit)
        if size_in_bytes >= unit_size:
            value = size_in_bytes // unit_size
            size_in_bytes %= unit_size
            result.append(f"{value}{unit}")
    
    return ' '.join(result)

def human_readable_to_bytes(human_readable):
    units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
    size_in_bytes = 0

    # Split the input by spaces
    parts = human_readable.split()
    
    for part in parts:
        # Extract the numeric value and unit
        value = int(''.join(filter(str.isdigit, part)))
        unit = ''.join(filter(str.isalpha, part)).upper()
        
        # Convert the value to bytes
        if unit in units:
            size_in_bytes += value * units[unit]

    return size_in_bytes

def get_total_size(obj, seen=None):
    """
    递归计算对象及其内部元素的总内存大小
    :param obj:
    :param seen:
    """
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # 标记当前对象为已处理
    seen.add(obj_id)
    size = sys.getsizeof(obj)
    # 递归计算内部元素的大小
    if isinstance(obj, dict):
        size += sum(get_total_size(v, seen) for v in obj.values())
        size += sum(get_total_size(k, seen) for k in obj.keys())
    elif isinstance(obj, (list, tuple, set, frozenset)):
        size += sum(get_total_size(i, seen) for i in obj)
    return size

def pi_digits(start, end):
    """
    获取π的指定小数位
    
    :param start: 起始位置（1-indexed）
    :param end: 结束位置（1-indexed）
    :return: π的指定小数位
    """
    # 设置mpmath的精度，至少需要end位小数
    mp.dps = end + 2  # 加2以确保足够的精度
    pi_str = str(mp.pi)[2:]  # 获取π的字符串形式，去掉"3."
    
    # 判断起始和结束位置是否合理
    if start < 1 or end < start:
        return "Invalid input. Ensure start >= 1 and end >= start."
    
    # 转换成0索引并获取对应的数字序列
    digits = [d for d in pi_str[start-1:end]]
    
    return ''.join(digits)

def generate_random_number(n):
    """
    生成一个n位随机数

    :param n: 随机数的位数
    :return: 随机数
    """
    if n <= 0:
        raise ValueError("Number of digits must be greater than zero.")
    
    digits = [random.randint(0, 9) for _ in range(n)]
    
    # Combine the digits into a single number
    random_number_str = ''.join(map(str, digits))
    return random_number_str