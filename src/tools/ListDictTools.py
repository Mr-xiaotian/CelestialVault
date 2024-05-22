from typing import List, Dict, Any, Tuple, Callable, Type, Iterable
from functools import reduce
from dis import Bytecode
from inspect import getsource
from itertools import product


def list_removes(lists: list, _remove) -> list:
    """
    移除列表中所有指定的元素，返回新列表，不修改原始列表。
    
    :param lists: 需要进行移除操作的列表
    :param _remove: 要移除的元素
    :return: 移除指定元素后的新列表
    """
    return [item for item in lists if item != _remove]

def all_elements_are_type(elements: List[Any], element_type: Type) -> bool:
    """
    检查列表中的所有元素是否都是指定类型。

    :param elements: 需要检查的元素列表
    :param element_type: 要检查的类型
    :return: 如果所有元素均为指定类型，返回True；否则返回False
    """
    return all(isinstance(element, element_type) for element in elements)

def all_elements_same_type(elements: List[Any]) -> bool:
    """
    检查列表中的所有元素是否具有相同的类型。

    :param elements: 需要检查的元素列表
    :return: 如果所有元素类型相同，返回True；否则返回False
    """
    if not elements:
        return True  # 空列表视为所有元素类型相同

    return len(set(type(element) for element in elements)) == 1

def list_replace(lists: List[Any], replace_list: List[Tuple[Any, Any]]) -> List[Any]:
    """
    替换列表中的元素。
    
    :param lists: 需要进行替换操作的列表
    :param replace_list: 替换规则的列表，每个规则是一个包含两个元素的元组，第一个是要被替换的元素，第二个是替换后的元素
    :return: 替换后的列表
    """
    from .Utilities import functions_are_equal
    def replace_element(element: Any, replacement: Tuple[Any, Any]) -> Any:
        # 如果元素是字符串且替换列表中的第一个元素在该字符串中，则进行替换
        if all_elements_are_type([element, *replacement], str) and replacement[0] in element:
            return element.replace(replacement[0], replacement[1])
        # 如果元素与替换列表中的第一个元素类型相同且内容相同，则进行替换
        elif all_elements_same_type([element, replacement[0]]) and str(element) == str(replacement[0]):
            return replacement[1]
        # 如果元素是函数且与替换列表中的第一个元素相同，则进行替换
        elif all_elements_are_type([element, replacement[0]], Callable) and functions_are_equal(element, replacement[0]):
            return replacement[1]
        # 如果元素不是字符串但等于替换列表中的第一个元素，则进行替换
        elif element == replacement[0]:
            return replacement[1]
        else:
            return element

    # 遍历原始列表中的每个元素，并应用所有的替换规则
    return [
        reduce(replace_element, replace_list, l)
        for l in lists
    ]

def multi_loop_generator(*lists: List[Any]) -> Iterable[List[Any]]:
    """
    生成任意次数嵌套循环的组合。
    
    :param lists: 多个列表，每个列表将用于一次嵌套循环
    :return: 生成器，依次产生每种组合的结果
    """
    for combination in product(*lists):
        yield combination

def dictkey_mix(dict_a: dict, dict_b: dict) -> Tuple[List[Any], List[Any], List[Any], List[Any]]:
    """
    将两个字典的键进行混合，并返回混合后的键列表。
    
    :param dict_a: 第一个字典
    :param dict_b: 第二个字典
    :return: 混合后的键列表，包括两个字典的键和键的交集、键的差集
    """
    key_a = set(dict_a.keys())
    key_b = set(dict_b.keys())

    key_max = list(key_a | key_b)
    key_min = list(key_a & key_b)
    dif_key_a = list(key_a - key_b)
    dif_key_b = list(key_b - key_a)
    
    return key_max, key_min, dif_key_a, dif_key_b

def count_occurrences(lst: List[Tuple[Tuple[str, int], str]], value: str) -> int:
    """
    在列表中查找指定元素的出现次数。
    
    Args:
        lst (List[Tuple[Tuple[str, int], str]]): 原始列表，列表的元素是元组，元组的第一个元素是字符串。
        value (str): 需要查找的元素。

    Returns:
        int: 指定元素在列表中的出现次数。
    """
    return sum(1 for item in lst if item[0][0] == value)

def get_key_dict(lst: List[Tuple[str, int]]) -> Dict[str, Tuple[int]]:
    """
    从列表中获取键值对，创建并返回一个字典。
    
    Args:
        lst (List[Tuple[str, int]]): 原始列表，列表的元素是元组。

    Returns:
        Dict[str, Tuple[int]]: 从列表中获取的键值对组成的字典。
    """
    dict_result = {}
    for item in lst:
        key, value = item[0][0], item[0][1]
        dict_result.setdefault(key, []).append(value)
    return {key: tuple(values) for key, values in dict_result.items()}

def find_tuple(lst: List[Tuple[Tuple[str, int], str]], target: str) -> Tuple[str, int]:
    """
    在列表中查找指定的元组。
    
    Args:
        lst (List[Tuple[Tuple[str, int], str]]): 原始列表，列表的元素是元组。
        target (str): 需要查找的元素。

    Returns:
        Tuple[str, int]: 在列表中找到的元组，如果没有找到，则返回None。
    """
    return next((item for item in lst if item[0] == target), None)
