# `celestialvault.tools.TextTools`

## 源文件

[src/celestialvault/tools/TextTools.py](../../src/celestialvault/tools/TextTools.py)

## 模块说明

文本处理工具模块，提供字符串转义处理、字典转换、字符串替换/移除/分割、语言指纹分析、中文/有效文本检测、CRC32 编解码、长度头编解码、Base64 编解码、文本压缩/解压缩、Reed-Solomon 纠错编解码、字节补齐、文件编码自动检测、文本文件合并、字符频率统计、最长公共子序列、相似度计算、表格格式化等功能。

## 导入依赖

```python
import base64
import re
import math
import string
import zlib
import struct
import reedsolo
from itertools import zip_longest
from pathlib import Path
from pprint import pprint

import charset_normalizer
from tqdm import tqdm
from wcwidth import wcswidth
```

## 顶层函数

### `pro_slash`

- 签名: `def pro_slash(input_str: str) -> str`
- 说明: 移除字符串中多余的转义符
- 参数:
  - `input_str` (str): 要处理的字符串
- 返回值: 移除多余转义符后的字符串
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import pro_slash

  result = pro_slash("C:\\\\Users\\\\test")
  print(result)  # "C:\\Users\\test"
  ```
- 关联: 无

### `str_to_dict`

- 签名: `def str_to_dict(string: str, line_delimiter: str = "\n", key_value_delimiter: str = ":") -> dict[str, str]`
- 说明: 将字符串转化为字典，每行格式为 `key:value`
- 参数:
  - `string` (str): 包含键值对的字符串，每行一个键值对
  - `line_delimiter` (str): 用于分隔行的字符串，默认换行符
  - `key_value_delimiter` (str): 用于分隔键和值的字符，默认冒号
- 返回值: 转化后的字典
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import str_to_dict

  text = "name:Alice\nage:30\ncity:Beijing"
  d = str_to_dict(text)
  print(d)  # {'name': 'Alice', 'age': '30', 'city': 'Beijing'}
  ```
- 关联: 无

### `str_removes`

- 签名: `def str_removes(strs: str, _remove: str) -> str`
- 说明: 从字符串中移除指定的子串
- 参数:
  - `strs` (str): 原始字符串
  - `_remove` (str): 需要移除的子串
- 返回值: 移除指定子串后的新字符串
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import str_removes

  print(str_removes("hello world", " world"))  # "hello"
  ```
- 关联: `str_replaces`

### `str_replaces`

- 签名: `def str_replaces(strs: str, replace_list: list[tuple[str, str]]) -> str`
- 说明: 从字符串中依次替换指定的子串
- 参数:
  - `strs` (str): 原始字符串
  - `replace_list` (list[tuple[str, str]]): 需要替换的子串列表
- 返回值: 替换指定子串后的新字符串
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import str_replaces

  result = str_replaces("hello world", [("hello", "hi"), ("world", "python")])
  print(result)  # "hi python"
  ```
- 关联: `str_removes`

### `iprint`

- 签名: `def iprint(obj: list | dict, start="", end="")`
- 说明: 根据对象的大小选择打印方式。如果长度小于 16 则打印整个对象，否则只打印前 10 个和后 5 个元素
- 参数:
  - `obj` (list | dict): 需要打印的对象
  - `start` (str): 打印前缀
  - `end` (str): 打印后缀
- 返回值: 无
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import iprint

  iprint(list(range(100)))
  ```
- 关联: 无

### `string_split`

- 签名: `def string_split(string: str, split_str: str = "\n") -> list[str]`
- 说明: 将字符串按指定分隔符分割，返回非空子字符串列表
- 参数:
  - `string` (str): 待分割的字符串
  - `split_str` (str): 分隔符，默认换行符
- 返回值: 分割后的非空子字符串列表
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import string_split

  parts = string_split("a\n\nb\nc")
  print(parts)  # ['a', 'b', 'c']
  ```
- 关联: 无

### `language_fingerprint`

- 签名: `def language_fingerprint(text: str) -> dict`
- 说明: 根据文本生成语言指纹字典，包括词数、字符数、词长分布、停用词比例和高频词等信息（当前版本未启用，需要 jieba 依赖）
- 参数:
  - `text` (str): 待分析的文本
- 返回值: 包含语言指纹信息的字典
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import language_fingerprint

  fp = language_fingerprint("这是一个测试文本")
  ```
- 关联: 无

### `calculate_valid_chinese_text`

- 签名: `def calculate_valid_chinese_text(text: str) -> float`
- 说明: 计算文本中中文字符（含中文标点和数字字母）的比例
- 参数:
  - `text` (str): 待分析的文本
- 返回值: 中文字符占总字符数的比例
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import calculate_valid_chinese_text

  ratio = calculate_valid_chinese_text("你好，世界 hello")
  print(f"{ratio:.2%}")
  ```
- 关联: `is_valid_chinese_text`

### `calculate_valid_text`

- 签名: `def calculate_valid_text(text: str) -> float`
- 说明: 计算文本中有效字符（中文、英文、数字及常见标点）的比例
- 参数:
  - `text` (str): 待分析的文本
- 返回值: 有效字符占总字符数的比例
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import calculate_valid_text

  ratio = calculate_valid_text("Hello, World! 你好世界")
  ```
- 关联: `is_valid_text`, `safe_open_txt`

### `is_valid_chinese_text`

- 签名: `def is_valid_chinese_text(text: str, threshold: float = 0.8) -> bool`
- 说明: 判断文本是否为有效中文文本，即中文字符比例是否大于阈值
- 参数:
  - `text` (str): 待判断的文本
  - `threshold` (float): 有效字符比例阈值，默认 0.8
- 返回值: 如果中文字符比例大于阈值返回 True
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import is_valid_chinese_text

  print(is_valid_chinese_text("这是一段纯中文文本"))  # True
  ```
- 关联: `calculate_valid_chinese_text`

### `is_valid_text`

- 签名: `def is_valid_text(text: str, threshold: float = 0.8) -> bool`
- 说明: 判断文本是否为有效文本，即有效字符比例是否大于阈值
- 参数:
  - `text` (str): 待判断的文本
  - `threshold` (float): 有效字符比例阈值，默认 0.8
- 返回值: 如果有效字符比例大于阈值返回 True
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import is_valid_text

  print(is_valid_text("Hello World"))  # True
  ```
- 关联: `calculate_valid_text`, `safe_open_txt`

### `crc_encode_text`

- 签名: `def crc_encode_text(actual_text: str) -> str`
- 说明: 在文本开头添加 4 字节 CRC32 校验和
- 参数:
  - `actual_text` (str): 原始文本
- 返回值: 前置 CRC32 校验和后的文本
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import crc_encode_text, crc_decode_text

  encoded = crc_encode_text("Hello")
  original = crc_decode_text(encoded)
  ```
- 关联: `crc_decode_text`

### `crc_decode_text`

- 签名: `def crc_decode_text(crc_text: str) -> str`
- 说明: 从文本中提取 CRC32 校验和并验证，返回原始文本
- 参数:
  - `crc_text` (str): 带 CRC32 校验和前缀的文本
- 返回值: 验证通过后的原始文本
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import crc_decode_text

  original = crc_decode_text(encoded_text)
  ```
- 关联: `crc_encode_text`

### `crc_encode_bytes`

- 签名: `def crc_encode_bytes(data: bytes) -> bytes`
- 说明: 在字节串前附加 4 字节 big-endian CRC32
- 参数:
  - `data` (bytes): 原始字节串
- 返回值: 前置 CRC32 校验和后的字节串
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import crc_encode_bytes, crc_decode_bytes

  encoded = crc_encode_bytes(b"hello")
  original = crc_decode_bytes(encoded)
  ```
- 关联: `crc_decode_bytes`

### `crc_decode_bytes`

- 签名: `def crc_decode_bytes(crc_data: bytes) -> bytes`
- 说明: 分离并验证前置 CRC32，返回原始字节
- 参数:
  - `crc_data` (bytes): 带 CRC32 前缀的字节串
- 返回值: 验证通过后的原始字节串
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import crc_decode_bytes

  original = crc_decode_bytes(encoded_bytes)
  ```
- 关联: `crc_encode_bytes`

### `add_length_header_to_text`

- 签名: `def add_length_header_to_text(text: str) -> str`
- 说明: 将文本前加 4 字节长度头（UTF-8 字节长度），头部使用 latin1 解码保证无损保留二进制
- 参数:
  - `text` (str): 原始文本
- 返回值: 带 4 字节长度头的文本
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import add_length_header_to_text, restore_text_from_length_header

  with_header = add_length_header_to_text("Hello")
  original = restore_text_from_length_header(with_header)
  ```
- 关联: `restore_text_from_length_header`

### `restore_text_from_length_header`

- 签名: `def restore_text_from_length_header(data: str) -> str`
- 说明: 从带长度头的文本恢复原始 UTF-8 文本
- 参数:
  - `data` (str): 带 4 字节长度头的文本
- 返回值: 恢复的原始 UTF-8 文本
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import restore_text_from_length_header

  original = restore_text_from_length_header(data_with_header)
  ```
- 关联: `add_length_header_to_text`

### `add_length_header_to_bytes`

- 签名: `def add_length_header_to_bytes(raw: bytes) -> bytes`
- 说明: 为 bytes 加上 4 字节长度头（big-endian）
- 参数:
  - `raw` (bytes): 原始字节串
- 返回值: 带 4 字节长度头的字节串
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import add_length_header_to_bytes, restore_bytes_from_length_header

  with_header = add_length_header_to_bytes(b"hello")
  original = restore_bytes_from_length_header(with_header)
  ```
- 关联: `restore_bytes_from_length_header`

### `restore_bytes_from_length_header`

- 签名: `def restore_bytes_from_length_header(data: bytes) -> bytes`
- 说明: 从带长度头的字节串中恢复原始 bytes
- 参数:
  - `data` (bytes): 带 4 字节长度头的字节串
- 返回值: 恢复的原始字节串
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import restore_bytes_from_length_header

  original = restore_bytes_from_length_header(data_with_header)
  ```
- 关联: `add_length_header_to_bytes`

### `encode_bytes_to_base64`

- 签名: `def encode_bytes_to_base64(data: bytes) -> str`
- 说明: 将字节串编码为 Base64 文本，并在前方加上 4 字节长度头（真实二进制长度）
- 参数:
  - `data` (bytes): 原始字节串
- 返回值: Base64 编码后的 UTF-8 文本
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import encode_bytes_to_base64, decode_bytes_from_base64

  encoded = encode_bytes_to_base64(b"hello world")
  original = decode_bytes_from_base64(encoded)
  ```
- 关联: `decode_bytes_from_base64`

### `decode_bytes_from_base64`

- 签名: `def decode_bytes_from_base64(text: str) -> bytes`
- 说明: 从 Base64 文本解码为字节串，解析前 4 字节长度头，截取真实数据
- 参数:
  - `text` (str): Base64 编码的文本
- 返回值: 解码后的原始字节串
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import decode_bytes_from_base64

  original = decode_bytes_from_base64(encoded_text)
  ```
- 关联: `encode_bytes_to_base64`

### `compress_text_to_bytes`

- 签名: `def compress_text_to_bytes(text: str) -> bytes`
- 说明: 压缩文本并返回字节流，前 4 字节存储真实压缩长度
- 参数:
  - `text` (str): 待压缩的文本
- 返回值: 带 4 字节长度头的压缩字节流
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import compress_text_to_bytes, decompress_text_from_bytes

  compressed = compress_text_to_bytes("Hello " * 1000)
  original = decompress_text_from_bytes(compressed)
  ```
- 关联: `decompress_text_from_bytes`, `compress_to_base64`

### `decompress_text_from_bytes`

- 签名: `def decompress_text_from_bytes(compressed_data: bytes) -> str`
- 说明: 从字节流中解压缩文本，利用前 4 字节长度头截取真实压缩数据
- 参数:
  - `compressed_data` (bytes): 带 4 字节长度头的压缩字节流
- 返回值: 解压缩后的原始文本
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import decompress_text_from_bytes

  text = decompress_text_from_bytes(compressed_data)
  ```
- 关联: `compress_text_to_bytes`, `decode_from_base64`

### `rs_encode`

- 签名: `def rs_encode(data: bytes, nsym: int) -> bytes`
- 说明: 对数据进行 Reed-Solomon 编码，自动分块以满足 GF(256) 长度限制
- 参数:
  - `data` (bytes): 原始字节数据
  - `nsym` (int): 总冗余字节数（必须 >= 1）
- 返回值: 编码后的字节串
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import rs_encode, rs_decode

  encoded = rs_encode(b"important data", nsym=10)
  decoded = rs_decode(encoded, nsym=10)
  ```
- 关联: `rs_decode`

### `rs_decode`

- 签名: `def rs_decode(encoded: bytes, nsym: int) -> bytes`
- 说明: 解码由 rs_encode 生成的 Reed-Solomon 编码数据，恢复原始数据
- 参数:
  - `encoded` (bytes): rs_encode 生成的编码数据
  - `nsym` (int): 总冗余字节数（必须 >= 1）
- 返回值: 解码后的原始字节数据
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import rs_decode

  original = rs_decode(encoded_data, nsym=10)
  ```
- 关联: `rs_encode`

### `pad_bytes`

- 签名: `def pad_bytes(data: bytes, target_len: int) -> bytes`
- 说明: 在 data 前加 4 字节长度头，并用 0xEC, 0x11 循环补齐到 target_len
- 参数:
  - `data` (bytes): 原始字节数据
  - `target_len` (int): 目标总长度（包含 4 字节头）
- 返回值: 补齐后的字节串
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import pad_bytes, unpad_bytes

  padded = pad_bytes(b"hello", 100)
  original = unpad_bytes(padded)
  ```
- 关联: `unpad_bytes`

### `unpad_bytes`

- 签名: `def unpad_bytes(data: bytes) -> bytes`
- 说明: 去掉补位并根据头部恢复原始数据
- 参数:
  - `data` (bytes): 带 4 字节长度头和补位的字节串
- 返回值: 恢复的原始字节数据
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import unpad_bytes

  original = unpad_bytes(padded_data)
  ```
- 关联: `pad_bytes`

### `pad_to_align`

- 签名: `def pad_to_align(data: bytes, align: int) -> bytes`
- 说明: 把字节流补齐到 align 的倍数，使用 0xEC, 0x11 循环填充
- 参数:
  - `data` (bytes): 原始字节流
  - `align` (int): 对齐目标（字节数）
- 返回值: 补齐后的字节流
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import pad_to_align

  aligned = pad_to_align(b"hello", 8)
  print(len(aligned))  # 8
  ```
- 关联: `compress_to_base64`

### `compress_to_base64`

- 签名: `def compress_to_base64(text: str) -> str`
- 说明: 压缩文本并转换为 Base64 编码，长度为 4 的倍数
- 参数:
  - `text` (str): 要压缩并转换为 Base64 的文本
- 返回值: 压缩后并转换为 Base64 的字符串
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import compress_to_base64, decode_from_base64

  b64 = compress_to_base64("Hello World " * 100)
  original = decode_from_base64(b64)
  ```
- 关联: `decode_from_base64`, `compress_text_to_bytes`, `pad_to_align`

### `decode_from_base64`

- 签名: `def decode_from_base64(base64_text: str) -> str`
- 说明: 从 Base64 编码中解码并解压缩文本
- 参数:
  - `base64_text` (str): Base64 编码的压缩文本
- 返回值: 解压缩后的原始文本
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import decode_from_base64

  original = decode_from_base64(base64_text)
  ```
- 关联: `compress_to_base64`, `decompress_text_from_bytes`

### `safe_open_txt`

- 签名: `def safe_open_txt(file_path: str | Path) -> str`
- 说明: 尝试使用多种编码打开文本文件，并返回解码后的文本。自动检测编码，依次尝试 charset-normalizer 检测结果、GB18030、Big5、UTF-8、UTF-16、Latin-1
- 参数:
  - `file_path` (str | Path): 文件路径
- 返回值: 解码后的文本内容
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import safe_open_txt

  text = safe_open_txt("chinese_text.txt")
  print(text[:100])
  ```
- 关联: `is_valid_text`

### `combine_txt_files`

- 签名: `def combine_txt_files(source_dir: str | Path, target_file: str | Path)`
- 说明: 将指定文件夹内的所有 txt 文件按文件名中的数字排序，合并为一个新的 txt 文件
- 参数:
  - `source_dir` (str | Path): 包含 txt 文件的文件夹路径
  - `target_file` (str | Path): 合并后的 txt 文件路径
- 返回值: 无
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import combine_txt_files

  combine_txt_files("chapters/", "combined_book.txt")
  ```
- 关联: 无

### `character_ratio`

- 签名: `def character_ratio(target_str: str) -> dict[str, float]`
- 说明: 统计字符串中各个字符的出现比率
- 参数:
  - `target_str` (str): 目标字符串
- 返回值: 各个字符及其出现比率的字典
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import character_ratio

  ratio = character_ratio("hello world")
  print(ratio)  # {'h': 0.09, 'e': 0.09, 'l': 0.27, ...}
  ```
- 关联: `celestialvault.tools.NumberUtils.digit_frequency`

### `get_lcs`

- 签名: `def get_lcs(str1: str, str2: str) -> list[str]`
- 说明: 找出两个字符串的最长公共子序列，并按连续段落分组返回。空字符串 "" 表示不匹配的间隔
- 参数:
  - `str1` (str): 第一个字符串
  - `str2` (str): 第二个字符串
- 返回值: 最长公共子序列的分段列表
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import get_lcs

  parts = get_lcs("abcde", "ace")
  print(parts)  # ['a', '', 'c', '', 'e']
  ```
- 关联: `calculate_similarity`

### `calculate_similarity`

- 签名: `def calculate_similarity(str1: str, str2: str, lcs_parts: list = None) -> float`
- 说明: 计算两个字符串的相似度
- 参数:
  - `str1` (str): 第一个字符串
  - `str2` (str): 第二个字符串
  - `lcs_parts` (list): 最长公共子序列的字符部分列表，可选
- 返回值: 相似度，范围在 0 到 1 之间
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import calculate_similarity

  sim = calculate_similarity("hello world", "hello python")
  print(f"相似度: {sim:.2%}")
  ```
- 关联: `get_lcs`

### `find_nth_occurrence`

- 签名: `def find_nth_occurrence(target_str: str, similar_str: str, occurrence: int) -> tuple`
- 说明: 查找目标字符串中指定第 n 次出现的子字符串位置
- 参数:
  - `target_str` (str): 目标字符串
  - `similar_str` (str): 待查找的子字符串
  - `occurrence` (int): 查找的第几次出现（从 1 开始计数）
- 返回值: (起始索引, 结束索引)，若不存在则返回 (-1, -1)
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import find_nth_occurrence

  pos = find_nth_occurrence("abcabcabc", "abc", 2)
  print(pos)  # (3, 6)
  ```
- 关联: 无

### `format_table`

- 签名: `def format_table(data: list, column_names: list = None, row_names: list = None, index_header: str = "#", fill_value: str = "N/A", align: str = "left") -> str`
- 说明: 格式化并生成对齐的表格字符串
- 参数:
  - `data` (list): 表格数据，二维列表
  - `column_names` (list): 自定义列名，默认使用 Excel 风格列名
  - `row_names` (list): 自定义行号，默认使用数字索引
  - `index_header` (str): 左上角名称，默认 "#"
  - `fill_value` (str): 空值填充，默认 "N/A"
  - `align` (str): 对齐方式，可选 "left"、"right"、"center"
- 返回值: 格式化后的表格字符串
- 用法示例:
  ```python
  from celestialvault.tools.TextTools import format_table

  data = [["Alice", 90, "A"], ["Bob", 85, "B"]]
  table = format_table(data, column_names=["Name", "Score", "Grade"])
  print(table)
  ```
- 关联: 被 `celestialvault.tools.FileOperations.duplicate_report`, `celestialvault.tools.ImageProcessing.compare_random_pixels` 调用
