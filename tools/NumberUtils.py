import random
import mpmath
import math
from tqdm import tqdm
from itertools import permutations
from typing import List, Dict, Union, Tuple
from constants.pi_digit import PI_STR_1E6
from tools.ListDictTools import list_to_square_matrix


def get_pi_digits(start: int, end: int) -> str:
    """
    获取π的指定小数位
    
    :param start: 起始位置（1-indexed）
    :param end: 结束位置（1-indexed）
    :return: π的指定小数位
    """
    if end < 1e6:
        pi_str = PI_STR_1E6[2:]
    else:
        # 设置mpmath的精度，至少需要end位小数
        mpmath.mp.dps = end + 2  # 加2以确保足够的精度
        pi_str = str(mpmath.pi)[2:]  # 获取π的字符串形式，去掉"3."
    
    # 判断起始和结束位置是否合理
    if start < 1 or end < start:
        raise ValueError("Invalid input. Ensure start >= 1 and end >= start.")
    
    # 转换成0索引并获取对应的数字序列
    digits = [d for d in pi_str[start-1:end]]
    
    return ''.join(digits)

def get_pi_digits_from_ranges(position_list: List[Tuple[int, int]]) -> str:
    """
    获取π的指定位置的小数位

    :param position_list: 位置列表
    :return: π的指定位置的小数位
    """
    return ''.join([get_pi_digits(pos[0], pos[1]) for pos in position_list])

def segment_search_in_pi(target: str, segment_len: int=5) -> dict:
    """
    在π的字符串表示中查找目标数字的位置

    :Example:
    segment_search_in_pi('546546516514564651654845', 5) = {
    '546546516514564651654845': [
        (92573, 92577),
        (56196, 56200),
        (250, 254),
        (56196, 56200),
        (10933, 10936)
        ],
    '54654': (92573, 92577),
    '65165': (56196, 56200),
    '14564': (250, 254),
    '4845': (10933, 10936)
    }

    :param target: 要查找的目标数字
    :param segment_len: 查找的初始分段长度, 默认为5, 当为-1时为数字长度的一半, 当为-2时为数字长度减一
    :return: 目标数字在π中的位置信息
    """
    def get_segment_len_by_half(target_len):
        return target_len // 2
    
    def get_segment_len_by_decrement(target_len):
        return target_len - 1

    # 封装查找逻辑为内部函数
    def segment_search(split_str, segment_len):
        split_str_len = len(split_str)
        
        segments = [split_str[i:i + segment_len] for i in range(0, split_str_len, segment_len)]
        
        for segment in segments:
            start_pos = pi_str.find(segment) # if segment not in position_results else position_results[segment]
            if start_pos != -1:
                end_pos = start_pos + len(segment)
                position = (start_pos + 1, end_pos)
                position_results[segment] = position
                position_results[target_str].append(position)
            else:
                # 递归调用以逐步缩小分段长度
                new_segment_len = get_segment_len(segment_len)
                segment_search(segment, new_segment_len)

    pi_str = PI_STR_1E6[2:]  # 移除 '3.' 部分
    target_str = str(target).replace('-', '')

    # 尝试查找完整数字
    start_pos = pi_str.find(target_str)

    if start_pos != -1:
        # 计算最后一个位置
        end_pos = start_pos + len(target_str)
        return {target_str: [(start_pos + 1, end_pos)]}

    # 如果找不到完整数字，进行分段查找
    position_results = {}
    position_results[target_str] = []  # 用于按顺序存储每个分段的位置信息

    # 初始分段长度
    if segment_len == -1:
        get_segment_len = get_segment_len_by_half
        segment_len = get_segment_len(len(target_str))
    elif segment_len == -2:
        get_segment_len = get_segment_len_by_decrement
        segment_len = get_segment_len(len(target_str))
    elif segment_len > len(target_str):
        get_segment_len = get_segment_len_by_half
        segment_len = get_segment_len(len(target_str))
    else:
        get_segment_len = get_segment_len_by_decrement

    # 开始分段查找
    segment_search(target_str, segment_len)
    
    return position_results

def greedy_search_in_pi(target: str) -> dict:
    """
    在 π 的字符串表示中使用贪婪搜索查找目标数字的位置。

    :Example:
    greedy_search_in_pi('546546516514564651654845') = {
    '546546516514564651654845': [(993795, 993801),
        (56198, 56202),
        (201390, 201394),
        (143633, 143637),
        (60, 61)],
    '5465465': (993795, 993801),
    '16514': (56198, 56202),
    '56465': (201390, 201394),
    '16548': (143633, 143637),
    '45': (60, 61)}
    
    :param target: 要查找的目标数字
    :return: 包含每个部分位置信息的字典
    """
    def greedy_search(remaining_str):
        # 从完整字符串逐步减少末尾字符，直到找到匹配
        for i in range(len(remaining_str), 0, -1):
            substring = remaining_str[:i]
            start_pos = pi_str.find(substring)
            
            if start_pos != -1:
                end_pos = start_pos + len(substring)
                position = (start_pos + 1, end_pos)
                position_results[substring] = position
                position_results[target_str].append(position)
                
                # 对剩余部分递归调用
                remaining_part = remaining_str[i:]
                if remaining_part:
                    greedy_search(remaining_part)
                
                break
            
    pi_str = PI_STR_1E6[2:]  # 移除 '3.'
    target_str = str(target).replace('-', '')

    # 尝试查找完整数字
    start_pos = pi_str.find(target_str)

    if start_pos != -1:
        # 计算最后一个位置
        end_pos = start_pos + len(target_str)
        return {target_str: [(start_pos + 1, end_pos)]}
    
    # 如果找不到完整数字，进行贪婪搜索
    position_results = {}
    position_results[target_str] = []

    # 开始贪婪搜索
    greedy_search(target_str)
    
    return position_results

def generate_random_numbers(num_digits: int, count: int=1) -> List[str]:
    """
    生成指定位数的随机数

    :param num_digits: 随机数的位数
    :param count: 要生成的随机数的个数
    :return: 包含生成的随机数的列表
    """
    if num_digits <= 0:
        raise ValueError("Number of digits must be greater than zero.")
    
    # 使用 random.choices 直接生成 num_digits 个随机数，每个数在 0 到 9 之间
    return [''.join(random.choices('0123456789', k=num_digits)) for _ in range(count)]

def find_all_combinations_ratio(target_sequence: str, digit_length: int) -> float:
    """
    在被检索字符串中查找所有指定位数的数字组合，并计算找到和未找到的比率。
    
    :param target_sequence: 被检索的数字字符串
    :param digit_length: 数字组合的位数（例如 2 表示 10 到 99）
    :return: 可以找到的数与找不到的数的比率
    """
    # 根据位数生成所有可能的数字组合
    start = 10**(digit_length - 1)
    end = 10**digit_length
    all_combinations = [str(i) for i in range(start, end)]
    
    found_count = 0
    
    for combination in all_combinations:
        if combination in target_sequence:
            found_count += 1
    
    return found_count / (end-start)

def digit_frequency(target_str: str) -> Dict[str, float]:
    """
    统计字符串中各个数字的出现比率

    :param target_str: 目标数字字符串
    :return: 各个数字及其出现比率的字典
    """
    frequency = {}
    total_length = 0

    for digit in target_str:
        if digit.isdigit():  # 只统计数字字符
            frequency[digit] = frequency.get(digit, 0) + 1
            total_length += 1

    # 将频率转换为比率
    ratio = {char: count / total_length for char, count in frequency.items()}

    return ratio

def check_target_sum(matrix):
    """
    检查方阵的每一行、每一列、两个对角线的和是否等于目标和。
    
    :param matrix: 方阵（二维列表）
    :return: 如果所有行、列、对角线的和都等于目标和，返回 True，否则返回 False
    """
    # 获取方阵的阶数
    n = len(matrix)
    
    # 计算目标和
    target_sum = n * (n**2 + 1) // 2

    # 检查每一行的和
    for row in matrix:
        if sum(row) != target_sum:
            return False

    # 检查每一列的和
    for col in range(n):
        col_sum = sum(matrix[row][col] for row in range(n))
        if col_sum != target_sum:
            return False

    # 检查主对角线的和（从左上到右下）
    diagonal_sum_1 = sum(matrix[i][i] for i in range(n))
    if diagonal_sum_1 != target_sum:
        return False

    # 检查副对角线的和（从右上到左下）
    diagonal_sum_2 = sum(matrix[i][n - 1 - i] for i in range(n))
    if diagonal_sum_2 != target_sum:
        return False

    return True

def check_numbers_validity(matrix):
    """
    检查方阵中的数字是否是从 1 到 n^2 的所有整数，且没有重复。
    
    :param matrix: 方阵（二维列表）
    :return: 如果数字是从 1 到 n^2 的连续整数且没有重复，返回 True，否则返回 False
    """
    # 获取方阵的阶数
    n = len(matrix)
    numbers = set()

    for row in matrix:
        for num in row:
            if num < 1 or num > n**2 or num in numbers:
                return False
            numbers.add(num)
    
    return True

def is_magic_square(matrix):
    """
    判断一个方阵是否是幻方。
    
    :param matrix: 方阵（二维列表）
    :return: 如果是幻方，返回 True，否则返回 False
    """
    
    # 检查目标和是否符合
    if not check_target_sum(matrix):
        return False
    
    # 检查数字是否符合要求
    if not check_numbers_validity(matrix):
        return False
    
    return True

def generate_magic_squares_by_random(num):
    """
    生成所有可能的 n x n 幻方。

    :param num: 幻方的阶数
    :return: 所有可能的 n x n 幻方的列表
    """
    # 所有数字集合，用于生成排列
    nums = list(range(1, num**2 + 1))

    # 存放所有有效幻方的列表
    magic_squares = []

    total = math.factorial(num ** 2)
    progress_bar = tqdm(total=total, desc='Generating Magic Squares')

    # 生成所有可能的n x n排列
    for perm in permutations(nums):
        matrix = list_to_square_matrix(perm)
        magic_squares.append(matrix) if check_target_sum(matrix) else None
        progress_bar.update(1)

    progress_bar.close()

    return magic_squares