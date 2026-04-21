# `celestialvault.tools.ListDictTools`

## 源文件

[src/celestialvault/tools/ListDictTools.py](../../src/celestialvault/tools/ListDictTools.py)

## 模块说明

列表和字典工具模块，提供列表元素移除、类型检查、元素替换、字典键混合、批量生成器、方阵转换等实用函数。

## 导入依赖

```python
from functools import reduce
from itertools import islice
from collections.abc import Callable, Iterable
from typing import Any
```

## 顶层函数

### `list_removes`

- 签名: `def list_removes(lists: list, _remove) -> list`
- 说明: 移除列表中所有指定的元素，返回新列表，不修改原始列表
- 参数:
  - `lists` (list): 需要进行移除操作的列表
  - `_remove`: 要移除的元素
- 返回值: 移除指定元素后的新列表
- 用法示例:
  ```python
  from celestialvault.tools.ListDictTools import list_removes

  result = list_removes([1, 2, 3, 2, 4], 2)
  print(result)  # [1, 3, 4]
  ```
- 关联: 无

### `all_elements_are_type`

- 签名: `def all_elements_are_type(elements: list[Any], element_type: type) -> bool`
- 说明: 检查列表中的所有元素是否都是指定类型
- 参数:
  - `elements` (list[Any]): 需要检查的元素列表
  - `element_type` (type): 要检查的类型
- 返回值: 如果所有元素均为指定类型，返回 True；否则返回 False
- 用法示例:
  ```python
  from celestialvault.tools.ListDictTools import all_elements_are_type

  print(all_elements_are_type([1, 2, 3], int))  # True
  print(all_elements_are_type([1, "2", 3], int))  # False
  ```
- 关联: `all_elements_same_type`

### `all_elements_same_type`

- 签名: `def all_elements_same_type(elements: list[Any]) -> bool`
- 说明: 检查列表中的所有元素是否具有相同的类型
- 参数:
  - `elements` (list[Any]): 需要检查的元素列表
- 返回值: 如果所有元素类型相同，返回 True；否则返回 False
- 用法示例:
  ```python
  from celestialvault.tools.ListDictTools import all_elements_same_type

  print(all_elements_same_type([1, 2, 3]))  # True
  print(all_elements_same_type([1, "2"]))   # False
  print(all_elements_same_type([]))          # True
  ```
- 关联: `all_elements_are_type`, `list_replace`

### `list_replace`

- 签名: `def list_replace(lists: list[Any], replace_rules: list[tuple[Any, Any]]) -> list[Any]`
- 说明: 替换列表中的元素，支持值替换、字符串子串替换和函数替换
- 参数:
  - `lists` (list[Any]): 需要进行替换操作的列表
  - `replace_rules` (list[tuple[Any, Any]]): 替换规则的列表，每个规则是 (被替换元素, 替换后元素) 的元组
- 返回值: 替换后的列表
- 用法示例:
  ```python
  from celestialvault.tools.ListDictTools import list_replace

  result = list_replace(["hello world", "foo"], [("world", "python")])
  print(result)  # ["hello python", "foo"]
  ```
- 关联: `all_elements_same_type`, `celestialvault.tools.Utilities.functions_are_equal`

### `dictkey_mix`

- 签名: `def dictkey_mix(dict_a: dict, dict_b: dict) -> tuple[list[Any], list[Any], list[Any], list[Any]]`
- 说明: 将两个字典的键进行混合，返回并集、交集和各自的差集
- 参数:
  - `dict_a` (dict): 第一个字典
  - `dict_b` (dict): 第二个字典
- 返回值: (键并集, 键交集, A独有的键, B独有的键)
- 用法示例:
  ```python
  from celestialvault.tools.ListDictTools import dictkey_mix

  a = {"x": 1, "y": 2}
  b = {"y": 3, "z": 4}
  key_max, key_min, dif_a, dif_b = dictkey_mix(a, b)
  # key_min = ['y'], dif_a = ['x'], dif_b = ['z']
  ```
- 关联: 无

### `batch_generator`

- 签名: `def batch_generator(generator: Iterable, batch_size: int)`
- 说明: 批量生成器：每次从原生成器中获取 batch_size 个元素
- 参数:
  - `generator` (Iterable): 原始生成器或可迭代对象
  - `batch_size` (int): 每批次的元素数量
- 返回值: 批量生成器，每次生成一个包含 batch_size 个元素的列表
- 用法示例:
  ```python
  from celestialvault.tools.ListDictTools import batch_generator

  for batch in batch_generator(range(10), 3):
      print(batch)
  # [0, 1, 2]
  # [3, 4, 5]
  # [6, 7, 8]
  # [9]
  ```
- 关联: 无

### `list_to_square_matrix`

- 签名: `def list_to_square_matrix(lst: list)`
- 说明: 将长度为 n^2 的列表转换为 n x n 的方阵
- 参数:
  - `lst` (list): 长度为 n^2 的列表
- 返回值: n x n 的方阵（二维列表）
- 用法示例:
  ```python
  from celestialvault.tools.ListDictTools import list_to_square_matrix

  matrix = list_to_square_matrix([1, 2, 3, 4, 5, 6, 7, 8, 9])
  # [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
  ```
- 关联: `format_simple_matrix`, `celestialvault.tools.NumberUtils.generate_magic_squares_by_random`

### `format_simple_matrix`

- 签名: `def format_simple_matrix(matrix: list)`
- 说明: 格式化简单矩阵为对齐的字符串表示
- 参数:
  - `matrix` (list): 二维列表（矩阵）
- 返回值: 格式化后的字符串
- 用法示例:
  ```python
  from celestialvault.tools.ListDictTools import format_simple_matrix

  matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
  print(format_simple_matrix(matrix))
  ```
- 关联: `list_to_square_matrix`
