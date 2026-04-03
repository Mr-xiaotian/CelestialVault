# tools/NumberUtils.py

## 源文件
- `src/celestialvault/tools/NumberUtils.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- `import math`
- `import random`
- `from itertools import permutations`
- `import mpmath`
- `from tqdm import tqdm`
- `from ..constants.pi_digit import PI_STR_1E6`
- `from .ListDictTools import list_to_square_matrix`

## 模块常量
- 无

## 顶层函数
### `get_pi_digits`
- 签名: `def get_pi_digits(start: int, end: int) -> str`
- 说明: 获取π的指定小数位

:param start: 起始位置（1-indexed）
:param end: 结束位置（1-indexed）
:return: π的指定小数位

### `get_pi_digits_from_ranges`
- 签名: `def get_pi_digits_from_ranges(position_list: list[tuple[int, int]]) -> str`
- 说明: 获取π的指定位置的小数位

:param position_list: 位置列表
:return: π的指定位置的小数位

### `segment_search_in_pi`
- 签名: `def segment_search_in_pi(target: str, segment_len: int = 5) -> dict`
- 说明: 在π的字符串表示中查找目标数字的位置

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

### `greedy_search_in_pi`
- 签名: `def greedy_search_in_pi(target: str) -> dict`
- 说明: 在 π 的字符串表示中使用贪婪搜索查找目标数字的位置。

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

### `generate_random_numbers`
- 签名: `def generate_random_numbers(num_digits: int, count: int = 1) -> list[str]`
- 说明: 生成指定位数的随机数

:param num_digits: 随机数的位数
:param count: 要生成的随机数的个数
:return: 包含生成的随机数的列表

### `find_all_combinations_ratio`
- 签名: `def find_all_combinations_ratio(target_sequence: str, digit_length: int) -> float`
- 说明: 在被检索字符串中查找所有指定位数的数字组合，并计算找到和未找到的比率。

:param target_sequence: 被检索的数字字符串
:param digit_length: 数字组合的位数（例如 2 表示 10 到 99）
:return: 可以找到的数与找不到的数的比率

### `digit_frequency`
- 签名: `def digit_frequency(target_str: str) -> dict[str, float]`
- 说明: 统计字符串中各个数字的出现比率

:param target_str: 目标数字字符串
:return: 各个数字及其出现比率的字典

### `check_target_sum`
- 签名: `def check_target_sum(matrix)`
- 说明: 检查方阵的每一行、每一列、两个对角线的和是否等于目标和。

:param matrix: 方阵（二维列表）
:return: 如果所有行、列、对角线的和都等于目标和，返回 True，否则返回 False

### `check_numbers_validity`
- 签名: `def check_numbers_validity(matrix)`
- 说明: 检查方阵中的数字是否是从 1 到 n^2 的所有整数，且没有重复。

:param matrix: 方阵（二维列表）
:return: 如果数字是从 1 到 n^2 的连续整数且没有重复，返回 True，否则返回 False

### `is_magic_square`
- 签名: `def is_magic_square(matrix)`
- 说明: 判断一个方阵是否是幻方。

:param matrix: 方阵（二维列表）
:return: 如果是幻方，返回 True，否则返回 False

### `generate_magic_squares_by_random`
- 签名: `def generate_magic_squares_by_random(num)`
- 说明: 生成所有可能的 n x n 幻方。

:param num: 幻方的阶数
:return: 所有可能的 n x n 幻方的列表

### `is_probable_prime`
- 签名: `def is_probable_prime(n: int, k: int = 10) -> bool`
- 说明: Miller-Rabin 素数判定

:param n: 要检测的整数
:param k: 测试轮数 (轮数越多，错误率越低)
:return: True 表示可能是素数，False 表示合数

### `generate_large_prime`
- 签名: `def generate_large_prime(bits = 512) -> int`
- 说明: 生成一个大素数，位数由 bits 参数指定。

:param bits: 素数的位数
:return: 大素数

### `choose_square_container`
- 签名: `def choose_square_container(n: int, threshold: float = 0.7)`
- 说明: 给定原始数据长度 n，选择一个平方数容器。

:param n 原始数据长度
:param threshold 控制最大允许的填充率（0~1）。
:return (容器边长, 最大可用数据长度, 冗余长度)

### `redundancy_from_container`
- 签名: `def redundancy_from_container(container: int, threshold: float = 0.7) -> int`
- 说明: 已知容器长度（平方数），计算对应冗余长度。

:param container 容器长度（平方数）
:param threshold 控制最大允许的填充率（0~1）。
:return 冗余长度

### `layered_coordinates`
- 签名: `def layered_coordinates(size)`
- 说明: 生成一个大小为 size 的螺旋矩阵的坐标列表。

:param size: 矩阵的大小
:return: 坐标列表

## 类
- 无
