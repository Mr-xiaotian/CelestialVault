# tools/TextTools.py

## 源文件
- `src/celestialvault/tools/TextTools.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- `import base64`
- `import re`
- `import math`
- `import string`
- `import zlib`
- `import struct`
- `import reedsolo`
- `from itertools import zip_longest`
- `from pathlib import Path`
- `from pprint import pprint`
- `import charset_normalizer`
- `from tqdm import tqdm`
- `from wcwidth import wcswidth`

## 模块常量
- 无

## 顶层函数
### `pro_slash`
- 签名: `def pro_slash(input_str: str) -> str`
- 说明: 移除字符串中多余的转义符。

:param input_str (str): 要处理的字符串。
:return str: 移除多余转义符后的字符串。

old:
re_strs = repr(strs)
while '\\' in re_strs:
    re_strs = re_strs.replace('\\', '\')
if re_strs[-2] == '\':
    print(re_strs[1:-2])
    re_strs = re_strs[1:-2]

try:
    pro_strs = eval(re_strs)
    return pro_strs
except Exception as e:
    print(e)
    return strs

### `str_to_dict`
- 签名: `def str_to_dict(string: str, line_delimiter: str = '\n', key_value_delimiter: str = ':') -> dict[str, str]`
- 说明: 将字符串转化为字典，每行格式为 `key:value`，以指定的分隔符分隔行。

:param string: 包含键值对的字符串，每行一个键值对。
:param line_delimiter: 用于分隔行的字符串，默认是换行符。
:param key_value_delimiter: 用于分隔键和值的字符，默认是冒号。
:return: 转化后的字典。

### `str_removes`
- 签名: `def str_removes(strs: str, _remove: str) -> str`
- 说明: 从字符串中移除指定的子串。

:param strs (str): 原始字符串。
:param _remove (str): 需要从原始字符串中移除的子串。
:return str: 移除指定子串后的新字符串。

### `str_replaces`
- 签名: `def str_replaces(strs: str, replace_list: list[tuple[str, str]]) -> str`
- 说明: 从字符串中替换指定的子串。

:param strs (str): 原始字符串。
:param replace_list (list[tuple[str, str]]): 需要替换的子串列表。
:return str: 替换指定子串后的新字符串。

### `iprint`
- 签名: `def iprint(obj: list | dict, start = '', end = '')`
- 说明: 根据对象的大小选择打印方式。
如果对象的长度小于16，那么就打印整个对象，否则只打印前10个和后5个元素。

:param obj (list | dict): 需要打印的对象，可以是列表或字典。

### `string_split`
- 签名: `def string_split(string: str, split_str: str = '\n') -> list[str]`
- 说明: 将字符串按指定分隔符分割，返回一个列表，每个元素是分割后非空的子字符串。

### `language_fingerprint`
- 签名: `def language_fingerprint(text: str) -> dict`
- 说明: 根据文本生成语言指纹字典。

### `calculate_valid_chinese_text`
- 签名: `def calculate_valid_chinese_text(text: str)`
- 说明: 计算文本中中文字符的比例。

### `calculate_valid_text`
- 签名: `def calculate_valid_text(text: str)`
- 说明: 计算文本中有效字符的比例。

### `is_valid_chinese_text`
- 签名: `def is_valid_chinese_text(text: str, threshold: int = 0.8)`
- 说明: 判断文本是否为有效文本，即文本中有效字符的比例是否大于阈值。

### `is_valid_text`
- 签名: `def is_valid_text(text: str, threshold: int = 0.8)`
- 说明: 判断文本是否为有效文本，即文本中有效字符的比例是否大于阈值。

### `crc_encode_text`
- 签名: `def crc_encode_text(actual_text: str) -> str`
- 说明: 在文本开头添加CRC32校验和。

### `crc_decode_text`
- 签名: `def crc_decode_text(crc_text: str) -> str`
- 说明: 从文本中提取CRC32校验和并验证。

### `crc_encode_bytes`
- 签名: `def crc_encode_bytes(data: bytes) -> bytes`
- 说明: 在字节串前附加 4 字节 big-endian CRC32。

### `crc_decode_bytes`
- 签名: `def crc_decode_bytes(crc_data: bytes) -> bytes`
- 说明: 分离并验证前置 CRC32，返回原始字节。

### `add_length_header_to_text`
- 签名: `def add_length_header_to_text(text: str) -> str`
- 说明: 将文本前加 4 字节长度头（注意：长度为“UTF-8字节长度”），并返回 str。
头部使用 latin1 解码，保证无损保留二进制。

### `restore_text_from_length_header`
- 签名: `def restore_text_from_length_header(data: str) -> str`
- 说明: 从带长度头的文本恢复原始 UTF-8 文本。

### `add_length_header_to_bytes`
- 签名: `def add_length_header_to_bytes(raw: bytes) -> bytes`
- 说明: 为 bytes 加上 4 字节长度头（big-endian）。
返回值为： [4字节长度] + [原始bytes]

### `restore_bytes_from_length_header`
- 签名: `def restore_bytes_from_length_header(data: bytes) -> bytes`
- 说明: 从带长度头的字节串中恢复原始 bytes。

### `encode_bytes_to_base64`
- 签名: `def encode_bytes_to_base64(data: bytes) -> str`
- 说明: 将字节串编码为 Base64 文本，并在前方加上 4 字节长度头（真实二进制长度）。
返回值为 UTF-8 文本。

### `decode_bytes_from_base64`
- 签名: `def decode_bytes_from_base64(text: str) -> bytes`
- 说明: 从 Base64 文本解码为字节串，解析前 4 字节长度头，截取真实数据。

### `compress_text_to_bytes`
- 签名: `def compress_text_to_bytes(text: str) -> bytes`
- 说明: 压缩文本并返回字节流，前 4 字节存储真实压缩长度。

### `decompress_text_from_bytes`
- 签名: `def decompress_text_from_bytes(compressed_data: bytes) -> str`
- 说明: 从字节流中解压缩文本，利用前 4 字节长度头截取真实压缩数据。

### `rs_encode`
- 签名: `def rs_encode(data: bytes, nsym: int) -> bytes`
- 说明: 把 data 分成 n 份，每份添加 nsym/n 个冗余，
保证 (len(data)/n + nsym/n) < 255。

### `rs_decode`
- 签名: `def rs_decode(encoded: bytes, nsym: int) -> bytes`
- 说明: 解码由 rs_encode 生成的数据。
输入: encoded (编码数据), nsym (总冗余字节数)
输出: 原始 data

### `pad_bytes`
- 签名: `def pad_bytes(data: bytes, target_len: int) -> bytes`
- 说明: 在 data 前加 4 字节长度头，并用 0xEC, 0x11 循环补齐到 target_len

### `unpad_bytes`
- 签名: `def unpad_bytes(data: bytes) -> bytes`
- 说明: 去掉补位并根据头部恢复原始数据

### `pad_to_align`
- 签名: `def pad_to_align(data: bytes, align: int) -> bytes`
- 说明: 把字节流补齐到 align 的倍数。

### `compress_to_base64`
- 签名: `def compress_to_base64(text: str) -> str`
- 说明: 压缩文本并转换为Base64编码, 长度为4的倍数。

:param text: 要压缩并转换为 Base64 的文本
:return: 压缩后并转换为 Base64 的字符串

### `decode_from_base64`
- 签名: `def decode_from_base64(base64_text: str) -> str`
- 说明: 从Base64编码中解码并解压缩文本。

### `safe_open_txt`
- 签名: `def safe_open_txt(file_path: str | Path) -> str`
- 说明: 尝试使用多种编码打开文本文件，并返回解码后的文本。

:param file_path: 文件路径，可以是字符串或 Path 对象
:return: 解码后的文本内容
:raises ValueError: 如果无法用任何编码解码文件，抛出异常

### `combine_txt_files`
- 签名: `def combine_txt_files(source_dir: str | Path, target_file: str | Path)`
- 说明: 将指定文件夹内的所有txt文件按文件名中的数字排序，合并为一个新的txt文件。
合并时每个文件的内容前面加入该文件的名字，合并文件名为文件夹名。

:param source_dir: 包含txt文件的文件夹路径。
:param target_file: 合并后的txt文件路径。

### `character_ratio`
- 签名: `def character_ratio(target_str: str) -> dict[str, float]`
- 说明: 统计字符串中各个字符的出现比率

:param target_str: 目标字符串
:return: 各个字符及其出现比率的字典

### `get_lcs`
- 签名: `def get_lcs(str1: str, str2: str) -> list[str]`
- 说明: 找出两个字符串的最大相似部分。
返回一个包含最大相似部分的字符串，如 "1-234-6"。

### `calculate_similarity`
- 签名: `def calculate_similarity(str1: str, str2: str, lcs_parts: list = None) -> float`
- 说明: 计算两个字符串的相似度。

:param str1: 第一个字符串
:param str2: 第二个字符串
:param lcs_parts: 最长公共子序列的字符部分列表
:return: 相似度，范围在 0 到 1 之间

### `find_nth_occurrence`
- 签名: `def find_nth_occurrence(target_str: str, similar_str: str, occurrence: int) -> tuple`
- 说明: 查找目标字符串中指定第n次出现的子字符串位置，并返回其起始和结束索引。

:param target_str: 目标字符串
:param similar_str: 待查找的子字符串
:param occurrence: 查找的第几次出现（从 1 开始计数）
:return: 子字符串在目标字符串中的起始和结束索引位置，若不存在则返回 (-1, -1)

### `format_table`
- 签名: `def format_table(data: list, column_names: list = None, row_names: list = None, index_header: str = '#', fill_value: str = 'N/A', align: str = 'left') -> str`
- 说明: 格式化并打印表格。

:param data: 表格数据，二维列表，每行代表一行数据
:param column_names: 自定义的列名，如果为None则使用默认列名（"A", "B", "C", ...）
:param row_names: 自定义的行号，如果为None则使用默认行号（0, 1, 2, 3...）
:param index_header: 左上角的名称，默认为 "#"
:param fill_value: 当数据为空时填充的值
:param align: 对齐方式，默认为 "left"
:return: 格式化后的表格字符串

## 类
- 无
