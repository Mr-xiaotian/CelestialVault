# `celestialvault.tools.SampleGenerate`

> 📅 最后更新日期: 2026/04/21

## 源文件

[src/celestialvault/tools/SampleGenerate.py](../../src/celestialvault/tools/SampleGenerate.py)

## 模块说明

样本生成工具模块，提供测试用文件结构生成（图片目录树、多尺寸 PDF、对比文件夹对）和测试数据生成（随机值、递增序列、随机矩阵、定长序列、间隔元组）等功能。

## 导入依赖

```python
import random
import string
import shutil
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
```

## 顶层函数

### `make_image_tree`

- 签名: `def make_image_tree(root_dir: str | Path, num_dirs: int = 3, images_per_dir: int = 5)`
- 说明: 在指定路径下生成多个子文件夹，每个文件夹中包含若干张大小随机、颜色不同的测试图片
- 参数:
  - `root_dir` (str | Path): 根目录路径，将在其下创建子文件夹和图片
  - `num_dirs` (int): 子文件夹数量
  - `images_per_dir` (int): 每个子文件夹中生成的图片数量
- 返回值: 无
- 用法示例:
  ```python
  from celestialvault.tools.SampleGenerate import make_image_tree

  make_image_tree("test_images/", num_dirs=5, images_per_dir=10)
  ```
- 关联: `celestialvault.tools.ImageProcessing.combine_imgs_dir`

### `make_multisize_pdf`

- 签名: `def make_multisize_pdf(file_path: str | Path)`
- 说明: 创建一个包含不同尺寸页面（A5、A4、A3）的示例 PDF 文件
- 参数:
  - `file_path` (str | Path): 输出 PDF 文件的路径
- 返回值: 无
- 用法示例:
  ```python
  from celestialvault.tools.SampleGenerate import make_multisize_pdf

  make_multisize_pdf("test_multisize.pdf")
  ```
- 关联: `celestialvault.tools.DocumentConversion.resize_pdf_to_max_width`

### `make_dirpair_fixture`

- 签名: `def make_dirpair_fixture(base_path: str | Path)`
- 说明: 在 base_path 下生成 dirA 和 dirB 两个文件夹，用于测试文件夹对比功能。覆盖四种情况：名称/大小/内容均不同、名称相同但大小/内容不同、名称和大小相同但内容不同、完全相同
- 参数:
  - `base_path` (str | Path): 基础路径
- 返回值: (dirA, dirB) 路径元组
- 用法示例:
  ```python
  from celestialvault.tools.SampleGenerate import make_dirpair_fixture

  dirA, dirB = make_dirpair_fixture("test_fixture/")
  ```
- 关联: `celestialvault.tools.FileOperations.detect_identical_files`, `celestialvault.tools.FileOperations.detect_identical_dirs`

### `random_values`

- 签名: `def random_values(length: int, data_types: str | list[str] = None) -> list`
- 说明: 生成测试数据，支持多种数据类型
- 参数:
  - `length` (int): 数据数量
  - `data_types` (str | list[str]): 数据类型，可以是字符串或列表。支持 'str', 'int', 'float', 'bool', 'none', 'list', 'dict', 'bytes', 'choice'。如果为 None，则默认全选
- 返回值: 随机数据列表
- 用法示例:
  ```python
  from celestialvault.tools.SampleGenerate import random_values

  data = random_values(10, data_types=["int", "str"])
  print(data)

  mixed = random_values(5)  # 所有类型混合
  ```
- 关联: 无

### `rand_strict_increasing_ints`

- 签名: `def rand_strict_increasing_ints(length: int, start: int = 0, max_step: int = 10) -> list[int]`
- 说明: 生成一个随机递增整数序列
- 参数:
  - `length` (int): 序列长度
  - `start` (int): 起始值
  - `max_step` (int): 每次递增的最大步长（至少 1）
- 返回值: 随机递增整数列表
- 用法示例:
  ```python
  from celestialvault.tools.SampleGenerate import rand_strict_increasing_ints

  seq = rand_strict_increasing_ints(5, start=0, max_step=5)
  print(seq)  # 例如 [0, 3, 7, 8, 12]
  ```
- 关联: `gapped_range_tuples`

### `rand_int_matrix`

- 签名: `def rand_int_matrix(size, min_val=1, max_val=9)`
- 说明: 生成一个方形二维数组（矩阵），元素为随机正整数
- 参数:
  - `size`: 矩阵大小（行数 = 列数）
  - `min_val`: 元素最小值
  - `max_val`: 元素最大值
- 返回值: 二维数组
- 用法示例:
  ```python
  from celestialvault.tools.SampleGenerate import rand_int_matrix

  matrix = rand_int_matrix(3, 1, 99)
  for row in matrix:
      print(row)
  ```
- 关联: 无

### `fixed_length_series`

- 签名: `def fixed_length_series(n: int, digits: str = "0123456789") -> str`
- 说明: 生成一个"长度数"序列
- 参数:
  - `n` (int): 目标长度（1 <= n < 100），输出字符串的总长度
  - `digits` (str): 用来填充的字符序列，默认 "0123456789"
- 返回值: 一个长度恰好为 n 的字符串
- 用法示例:
  ```python
  from celestialvault.tools.SampleGenerate import fixed_length_series

  s = fixed_length_series(20)
  print(s, len(s))  # 长度恰好为 20
  ```
- 关联: 无

### `gapped_range_tuples`

- 签名: `def gapped_range_tuples(length: int, tuple_size: int)`
- 说明: 生成指定数量和元组长度的递增数列元组列表
- 参数:
  - `length` (int): 元组数量
  - `tuple_size` (int): 每个元组的长度
- 返回值: 递增数列元组列表
- 用法示例:
  ```python
  from celestialvault.tools.SampleGenerate import gapped_range_tuples

  result = gapped_range_tuples(3, 2)
  print(result)  # 例如 [(0, 5), (3, 9), (6, 14)]
  ```
- 关联: `rand_strict_increasing_ints`
