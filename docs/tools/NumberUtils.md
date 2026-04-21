# `celestialvault.tools.NumberUtils`

## 源文件

[src/celestialvault/tools/NumberUtils.py](../../src/celestialvault/tools/NumberUtils.py)

## 模块说明

数字工具模块，提供圆周率相关计算（获取指定位数、分段搜索、贪婪搜索）、随机数生成、数字组合检索、数字频率统计、幻方验证与生成、素数判定与生成、平方数容器计算、螺旋坐标生成等功能。

## 导入依赖

```python
import math
import random
from itertools import permutations

import mpmath
from tqdm import tqdm

from ..constants.pi_digit import PI_STR_1E6
from .ListDictTools import list_to_square_matrix
```

## 顶层函数

### `get_pi_digits`

- 签名: `def get_pi_digits(start: int, end: int) -> str`
- 说明: 获取 pi 的指定小数位
- 参数:
  - `start` (int): 起始位置（1-indexed）
  - `end` (int): 结束位置（1-indexed）
- 返回值: pi 的指定小数位字符串
- 用法示例:
  ```python
  from celestialvault.tools.NumberUtils import get_pi_digits

  digits = get_pi_digits(1, 10)
  print(digits)  # "1415926535"
  ```
- 关联: `get_pi_digits_from_ranges`, `segment_search_in_pi`, `greedy_search_in_pi`

### `get_pi_digits_from_ranges`

- 签名: `def get_pi_digits_from_ranges(position_list: list[tuple[int, int]]) -> str`
- 说明: 获取 pi 的指定多个位置范围的小数位并拼接
- 参数:
  - `position_list` (list[tuple[int, int]]): 位置列表，每个元素为 (start, end)
- 返回值: 拼接后的 pi 小数位字符串
- 用法示例:
  ```python
  from celestialvault.tools.NumberUtils import get_pi_digits_from_ranges

  result = get_pi_digits_from_ranges([(1, 5), (10, 15)])
  ```
- 关联: `get_pi_digits`

### `segment_search_in_pi`

- 签名: `def segment_search_in_pi(target: str, segment_len: int = 5) -> dict`
- 说明: 在 pi 的字符串表示中查找目标数字的位置，采用分段搜索策略
- 参数:
  - `target` (str): 要查找的目标数字
  - `segment_len` (int): 查找的初始分段长度，默认 5；-1 为数字长度的一半；-2 为数字长度减一
- 返回值: 目标数字在 pi 中的位置信息字典
- 用法示例:
  ```python
  from celestialvault.tools.NumberUtils import segment_search_in_pi

  result = segment_search_in_pi("14159", 5)
  print(result)  # {'14159': [(1, 5)]}
  ```
- 关联: `get_pi_digits`, `greedy_search_in_pi`

### `greedy_search_in_pi`

- 签名: `def greedy_search_in_pi(target: str) -> dict`
- 说明: 在 pi 的字符串表示中使用贪婪搜索查找目标数字的位置，每次尽可能匹配最长子串
- 参数:
  - `target` (str): 要查找的目标数字
- 返回值: 包含每个部分位置信息的字典
- 用法示例:
  ```python
  from celestialvault.tools.NumberUtils import greedy_search_in_pi

  result = greedy_search_in_pi("271828")
  print(result)
  ```
- 关联: `segment_search_in_pi`

### `generate_random_numbers`

- 签名: `def generate_random_numbers(num_digits: int, count: int = 1) -> list[str]`
- 说明: 生成指定位数的随机数
- 参数:
  - `num_digits` (int): 随机数的位数
  - `count` (int): 要生成的随机数的个数
- 返回值: 包含生成的随机数的列表
- 用法示例:
  ```python
  from celestialvault.tools.NumberUtils import generate_random_numbers

  nums = generate_random_numbers(6, count=3)
  print(nums)  # ['482916', '073251', '918374']
  ```
- 关联: 无

### `find_all_combinations_ratio`

- 签名: `def find_all_combinations_ratio(target_sequence: str, digit_length: int) -> float`
- 说明: 在被检索字符串中查找所有指定位数的数字组合，并计算找到的比率
- 参数:
  - `target_sequence` (str): 被检索的数字字符串
  - `digit_length` (int): 数字组合的位数（例如 2 表示 10 到 99）
- 返回值: 可以找到的数与总数的比率
- 用法示例:
  ```python
  from celestialvault.tools.NumberUtils import find_all_combinations_ratio, get_pi_digits

  pi_digits = get_pi_digits(1, 100000)
  ratio = find_all_combinations_ratio(pi_digits, 3)
  print(f"覆盖率: {ratio:.2%}")
  ```
- 关联: 无

### `digit_frequency`

- 签名: `def digit_frequency(target_str: str) -> dict[str, float]`
- 说明: 统计字符串中各个数字的出现比率
- 参数:
  - `target_str` (str): 目标数字字符串
- 返回值: 各个数字及其出现比率的字典
- 用法示例:
  ```python
  from celestialvault.tools.NumberUtils import digit_frequency

  freq = digit_frequency("314159265358979")
  print(freq)
  ```
- 关联: 无

### `check_target_sum`

- 签名: `def check_target_sum(matrix)`
- 说明: 检查方阵的每一行、每一列、两个对角线的和是否等于目标和
- 参数:
  - `matrix`: 方阵（二维列表）
- 返回值: 如果所有行、列、对角线的和都等于目标和，返回 True，否则返回 False
- 用法示例:
  ```python
  from celestialvault.tools.NumberUtils import check_target_sum

  matrix = [[2, 7, 6], [9, 5, 1], [4, 3, 8]]
  print(check_target_sum(matrix))  # True
  ```
- 关联: `is_magic_square`, `generate_magic_squares_by_random`

### `check_numbers_validity`

- 签名: `def check_numbers_validity(matrix)`
- 说明: 检查方阵中的数字是否是从 1 到 n^2 的所有整数，且没有重复
- 参数:
  - `matrix`: 方阵（二维列表）
- 返回值: 如果数字是从 1 到 n^2 的连续整数且没有重复，返回 True，否则返回 False
- 用法示例:
  ```python
  from celestialvault.tools.NumberUtils import check_numbers_validity

  matrix = [[2, 7, 6], [9, 5, 1], [4, 3, 8]]
  print(check_numbers_validity(matrix))  # True
  ```
- 关联: `is_magic_square`

### `is_magic_square`

- 签名: `def is_magic_square(matrix)`
- 说明: 判断一个方阵是否是幻方
- 参数:
  - `matrix`: 方阵（二维列表）
- 返回值: 如果是幻方，返回 True，否则返回 False
- 用法示例:
  ```python
  from celestialvault.tools.NumberUtils import is_magic_square

  matrix = [[2, 7, 6], [9, 5, 1], [4, 3, 8]]
  print(is_magic_square(matrix))  # True
  ```
- 关联: `check_target_sum`, `check_numbers_validity`

### `generate_magic_squares_by_random`

- 签名: `def generate_magic_squares_by_random(num)`
- 说明: 通过穷举所有排列生成所有可能的 n x n 幻方
- 参数:
  - `num`: 幻方的阶数
- 返回值: 所有可能的 n x n 幻方的列表
- 用法示例:
  ```python
  from celestialvault.tools.NumberUtils import generate_magic_squares_by_random

  squares = generate_magic_squares_by_random(3)
  print(f"找到 {len(squares)} 个 3x3 幻方")
  ```
- 关联: `check_target_sum`, `celestialvault.tools.ListDictTools.list_to_square_matrix`

### `is_probable_prime`

- 签名: `def is_probable_prime(n: int, k: int = 10) -> bool`
- 说明: Miller-Rabin 素数判定
- 参数:
  - `n` (int): 要检测的整数
  - `k` (int): 测试轮数（轮数越多，错误率越低）
- 返回值: True 表示可能是素数，False 表示合数
- 用法示例:
  ```python
  from celestialvault.tools.NumberUtils import is_probable_prime

  print(is_probable_prime(104729))  # True
  print(is_probable_prime(104730))  # False
  ```
- 关联: `generate_large_prime`

### `generate_large_prime`

- 签名: `def generate_large_prime(bits=512) -> int`
- 说明: 生成一个大素数，位数由 bits 参数指定
- 参数:
  - `bits` (int): 素数的位数
- 返回值: 大素数
- 用法示例:
  ```python
  from celestialvault.tools.NumberUtils import generate_large_prime

  prime = generate_large_prime(256)
  print(prime)
  ```
- 关联: `is_probable_prime`

### `choose_square_container`

- 签名: `def choose_square_container(n: int, threshold: float = 0.7)`
- 说明: 给定原始数据长度 n，选择一个平方数容器
- 参数:
  - `n` (int): 原始数据长度
  - `threshold` (float): 控制最大允许的填充率（0~1）
- 返回值: (容器边长, 最大可用数据长度, 冗余长度)
- 用法示例:
  ```python
  from celestialvault.tools.NumberUtils import choose_square_container

  side, max_payload, redundancy = choose_square_container(1000, 0.7)
  print(f"边长: {side}, 容器: {side*side}, 冗余: {redundancy}")
  ```
- 关联: `redundancy_from_container`

### `redundancy_from_container`

- 签名: `def redundancy_from_container(container: int, threshold: float = 0.7) -> int`
- 说明: 已知容器长度（平方数），计算对应冗余长度
- 参数:
  - `container` (int): 容器长度（平方数）
  - `threshold` (float): 控制最大允许的填充率（0~1）
- 返回值: 冗余长度
- 用法示例:
  ```python
  from celestialvault.tools.NumberUtils import redundancy_from_container

  redundancy = redundancy_from_container(10000, 0.7)
  print(f"冗余: {redundancy}")
  ```
- 关联: `choose_square_container`

### `layered_coordinates`

- 签名: `def layered_coordinates(size)`
- 说明: 生成一个大小为 size 的螺旋矩阵的坐标列表
- 参数:
  - `size`: 矩阵的大小
- 返回值: 坐标列表
- 用法示例:
  ```python
  from celestialvault.tools.NumberUtils import layered_coordinates

  coords = layered_coordinates(3)
  print(coords)
  # [(0, 0), (0, 1), (1, 0), (2, 0), (1, 1), (0, 2), (1, 2), (2, 1), (2, 2)]
  ```
- 关联: 无
