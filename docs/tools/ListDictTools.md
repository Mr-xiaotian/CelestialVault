# tools/ListDictTools.py

## 源文件
- `src/celestialvault/tools/ListDictTools.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- `from functools import reduce`
- `from itertools import islice`
- `from collections.abc import Callable, Iterable`
- `from typing import Any`

## 模块常量
- 无

## 顶层函数
### `list_removes`
- 签名: `def list_removes(lists: list, _remove) -> list`
- 说明: 移除列表中所有指定的元素，返回新列表，不修改原始列表。

:param lists: 需要进行移除操作的列表
:param _remove: 要移除的元素
:return: 移除指定元素后的新列表

### `all_elements_are_type`
- 签名: `def all_elements_are_type(elements: list[Any], element_type: type) -> bool`
- 说明: 检查列表中的所有元素是否都是指定类型。

:param elements: 需要检查的元素列表
:param element_type: 要检查的类型
:return: 如果所有元素均为指定类型，返回True；否则返回False

### `all_elements_same_type`
- 签名: `def all_elements_same_type(elements: list[Any]) -> bool`
- 说明: 检查列表中的所有元素是否具有相同的类型。

:param elements: 需要检查的元素列表
:return: 如果所有元素类型相同，返回True；否则返回False

### `list_replace`
- 签名: `def list_replace(lists: list[Any], replace_rules: list[tuple[Any, Any]]) -> list[Any]`
- 说明: 替换列表中的元素。

:param lists: 需要进行替换操作的列表
:param replace_rules: 替换规则的列表，每个规则是一个包含两个元素的元组，第一个是要被替换的元素，第二个是替换后的元素
:return: 替换后的列表

### `dictkey_mix`
- 签名: `def dictkey_mix(dict_a: dict, dict_b: dict) -> tuple[list[Any], list[Any], list[Any], list[Any]]`
- 说明: 将两个字典的键进行混合，并返回混合后的键列表。

:param dict_a: 第一个字典
:param dict_b: 第二个字典
:return: 混合后的键列表，包括两个字典的键和键的交集、键的差集

### `batch_generator`
- 签名: `def batch_generator(generator: Iterable, batch_size: int)`
- 说明: 批量生成器：每次从原生成器中获取 batch_size 个元素。

:param generator: 原始生成器
:param batch_size: 每批次的元素数量
:return: 批量生成器，每次生成一个包含 batch_size 个元素的列表

### `list_to_square_matrix`
- 签名: `def list_to_square_matrix(lst: list)`
- 说明: 将长度为 n^2 的列表转换为 n x n 的方阵。

:param lst: 长度为 n^2 的列表
:return: n x n 的方阵（二维列表）

### `format_simple_matrix`
- 签名: `def format_simple_matrix(matrix: list)`
- 说明: 格式化简单矩阵
:param matrix: 矩阵
:return: 格式化后的字符串

## 类
- 无
