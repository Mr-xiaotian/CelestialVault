import types
from time import strftime, localtime
from typing import Callable


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