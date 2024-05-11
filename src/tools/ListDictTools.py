from typing import List, Dict, Union, Tuple


def list_removes(lists: list, _remove) -> list:
    """
    移除列表中所有指定的元素，返回新列表，不修改原始列表。
    """
    return [item for item in lists if item != _remove]

def list_replace(lists: List[str], replace_list: List[Tuple[str, str]]) -> List[str]:
    """
    替换列表中的字符串。
    """
    new_list = []
    for l in lists:
        for r in replace_list:
            l = l.replace(r[0], r[1])
        new_list.append(l)
    return new_list

def dictkey_mix(dict_a: dict, dict_b: dict):
    key_a = list(dict_a.keys())
    key_b = list(dict_b.keys())

    key_max = key_a[:]
    key_min = []
    dif_key_a = []
    dif_key_b = []
    
    for each in key_b:
        if each not in key_a:
            key_max.append(each)
            dif_key_b.append(each)
        else:
            key_min.append(each)
    for each in key_a:
        if each not in key_b:
            key_max.append(each)
            dif_key_a.append(each)
    
    return key_max,key_min,dif_key_a,dif_key_b


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
