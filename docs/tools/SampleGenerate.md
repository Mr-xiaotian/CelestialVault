# tools/SampleGenerate.py

## 源文件
- `src/celestialvault/tools/SampleGenerate.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- `import random`
- `import string`
- `import shutil`
- `from pathlib import Path`
- `import fitz`
- `from PIL import Image, ImageDraw, ImageFont`

## 模块常量
- 无

## 顶层函数
### `make_image_tree`
- 签名: `def make_image_tree(root_dir: str | Path, num_dirs: int = 3, images_per_dir: int = 5)`
- 说明: 在指定路径下生成多个子文件夹，每个文件夹中包含若干张大小随机、颜色不同的测试图片。

:param root_dir: 根目录路径，将在其下创建子文件夹和图片
:param num_dirs: 子文件夹数量
:param images_per_dir: 每个子文件夹中生成的图片数量

### `make_multisize_pdf`
- 签名: `def make_multisize_pdf(file_path: str | Path)`
- 说明: 创建一个包含不同尺寸页面的示例 PDF 文件。

:param file_path: 输出 PDF 文件的路径

### `make_dirpair_fixture`
- 签名: `def make_dirpair_fixture(base_path: str | Path)`
- 说明: 在 base_path 下生成 dirA 和 dirB 两个文件夹，用于测试文件夹对比功能。
覆盖四种情况：
1. 名称、大小、内容均不同；
2. 名称相同但大小、内容不同；
3. 名称和大小相同但内容不同；
4. 名称、大小、内容完全相同。

:param base_path: 基础路径

### `random_values`
- 签名: `def random_values(length: int, data_types: str | list[str] = None) -> list`
- 说明: 生成测试数据

:param length: 数据数量
:param data_types: 数据类型，可以是字符串（'str', 'int', 'float', 'bool', 'none', 'list', 'dict', 'bytes', 'choice'）
                   或列表（支持多选）。如果为 None，则默认全选所有类型。
:return: 随机数据列表

### `rand_strict_increasing_ints`
- 签名: `def rand_strict_increasing_ints(length: int, start: int = 0, max_step: int = 10) -> list[int]`
- 说明: 生成一个随机递增整数序列

:param length: 序列长度
:param start: 起始值
:param max_step: 每次递增的最大步长（至少 1）

### `rand_int_matrix`
- 签名: `def rand_int_matrix(size, min_val = 1, max_val = 9)`
- 说明: 生成一个方形二维数组（矩阵），元素为随机正整数。

:param size: 矩阵大小（行数 = 列数）
:param min_val: 元素最小值
:param max_val: 元素最大值
:return: 二维数组

### `fixed_length_series`
- 签名: `def fixed_length_series(n: int, digits: str = '0123456789') -> str`
- 说明: 生成一个“长度数”序列。

:param n: 目标长度（1 <= n < 100），输出字符串的总长度。
:param digits: 用来填充的字符序列，如 "0123456789" 或 "零一二三四五六七八九"。
               默认值为 "0123456789"。
:return: 一个长度恰好为 n 的字符串。

### `gapped_range_tuples`
- 签名: `def gapped_range_tuples(length: int, tuple_size: int)`
- 说明: 生成指定数量和元组长度的递增数列元组列表

:param length: 元组数量
:param tuple_size: 每个元组的长度

## 类
- 无
