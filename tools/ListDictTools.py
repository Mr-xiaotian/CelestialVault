from typing import List, Any, Tuple, Callable, Type, Iterable
from itertools import islice
from functools import reduce


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

def list_replace(lists: List[Any], replace_rules: List[Tuple[Any, Any]]) -> List[Any]:
    """
    替换列表中的元素。
    
    :param lists: 需要进行替换操作的列表
    :param replace_rules: 替换规则的列表，每个规则是一个包含两个元素的元组，第一个是要被替换的元素，第二个是替换后的元素
    :return: 替换后的列表
    """
    from tools.Utilities import functions_are_equal
    def replace_element(element: Any, replacement: Tuple[Any, Any]) -> Any:
        target, replacement_value = replacement
        if not all_elements_same_type([element, target]):
            return element
        
        # 如果元素与替换列表中的第一个元素内容相同，则进行替换
        if element == target:
            return replacement_value
        
        # 如果元素是字符串且替换列表中的第一个元素在该字符串中，则进行替换
        elif isinstance(element, str) and target in element:
            return element.replace(target, replacement_value)
        
        # 如果元素是函数且与替换列表中的第一个元素相同，则进行替换
        elif isinstance(element,  Callable) and functions_are_equal(element, target):
            return replacement_value
        
        return element

    # 遍历原始列表中的每个元素，并应用所有的替换规则
    return [
        reduce(replace_element, replace_rules, l)
        for l in lists
    ]

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

def batch_generator(generator: Iterable, batch_size: int):
    """
    批量生成器：每次从原生成器中获取 batch_size 个元素。

    :param generator: 原始生成器
    :param batch_size: 每批次的元素数量
    :return: 批量生成器，每次生成一个包含 batch_size 个元素的列表
    """
    generator = iter(generator)  # 确保是迭代器
    while True:
        batch = list(islice(generator, batch_size))
        if not batch:
            break
        yield batch

def list_to_square_matrix(lst: list):
    """
    将长度为 n^2 的列表转换为 n x n 的方阵。
    
    :param lst: 长度为 n^2 的列表
    :return: n x n 的方阵（二维列表）
    """
    n = int(len(lst) ** 0.5)  # 计算方阵的阶数n
    if n * n != len(lst):
        raise ValueError("列表的长度必须是 n^2")
    
    # 将列表分割成 n 个子列表，每个子列表表示方阵的一行
    matrix = [lst[i * n: (i + 1) * n] for i in range(n)]
    
    return matrix

def format_simple_matrix(matrix: list):
    '''
    格式化简单矩阵
    :param matrix: 矩阵
    :return: 格式化后的字符串
    '''
    # 确定每个元素的最大宽度
    max_width = max(len(str(item)) for row in matrix for item in row)
    
    formatted_rows = []
    for row in matrix:
        formatted_row = "  [" + ", ".join(f"{item:>{max_width}}" for item in row) + "]"
        formatted_rows.append(formatted_row)
    
    formatted_string = "[\n" + ",\n".join(formatted_rows) + "\n]"
    return formatted_string