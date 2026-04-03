# tools/FileOperations.py

## 源文件
- `src/celestialvault/tools/FileOperations.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- `import hashlib`
- `import re`
- `import shutil`
- `import tarfile`
- `import zipfile`
- `from collections import defaultdict`
- `from pathlib import Path`
- `from collections.abc import Callable`
- `from typing import Any`
- `import py7zr`
- `import rarfile`
- `from tqdm import tqdm`
- `from wcwidth import wcswidth`
- `from celestialflow import TaskExecutor`
- `from ..constants import IMG_SUFFIXES, VIDEO_SUFFIXES`
- `from ..instances.inst_units import HumanBytes, HumanTimestamp`
- `from .TextTools import format_table`

## 模块常量
- 无

## 顶层函数
### `create_dir`
- 签名: `def create_dir(path: str | Path) -> Path`
- 说明: 判断系统是否存在该路径,没有则创建。

:param path: 要创建的文件夹路径。
:return: 创建或存在的文件夹路径。

### `handle_item`
- 签名: `def handle_item(source: Path, destination: Path, action: Callable[[Path, Path, Any], Any], extra: dict)`
- 说明: 处理文件，如果目标文件不存在则执行指定的操作。

:param source: 源文件路径。
:param destination: 目标文件路径。
:param action: 处理文件的函数或方法。
:return: 如果目标文件已存在，则返回 None；否则返回 action 的结果。

### `handle_dir_files`
- 签名: `def handle_dir_files(dir_path: str | Path, rules: dict[str, tuple[Callable[[Path, Path, dict], None], Callable[[Path], Path], dict]], execution_mode: str = 'serial', progress_desc: str = 'Processing files', dir_name_suffix: str = '_re') -> dict[tuple[str, str], list[Path]]`
- 说明: 遍历指定文件夹，根据文件后缀名对文件进行处理，并将处理后的文件存储到新的目录中。
不属于指定后缀的文件将被直接复制到新目录中。处理后的文件会保持原始的目录结构。
如果目标文件已存在，则会跳过处理。处理过程中遇到的任何错误都会被记录并返回。

:param dir_path: 要处理的文件夹的路径，可以是相对路径或绝对路径。
:param rules: 一个字典，键为文件后缀，值为处理该类型文件的函数和重命名函数的元组。
:param execution_mode: 执行模式，可以是 'serial' 或 'thread' 'process'。默认为 'serial'。
:param progress_desc: 进度条描述。
:return: 包含因错误未能正确处理的文件及其对应错误信息的列表。每个元素是一个元组，包括文件路径和错误对象。

### `handle_subdirs`
- 签名: `def handle_subdirs(dir_path: str | Path, rules: dict[str, tuple[Callable[[Path, Path, dict], None], Callable[[Path], Path], dict]], execution_mode: str = 'serial', progress_desc: str = 'Processing dirs', dir_name_suffix: str = '_re') -> dict[tuple[str, str], list[Path]]`
- 说明: 遍历指定文件夹，根据文件后缀名对文件进行处理，并将处理后的文件存储到新的目录中。
不属于指定后缀的文件将被直接复制到新目录中。处理后的文件会保持原始的目录结构。
如果目标文件已存在，则会跳过处理。处理过程中遇到的任何错误都会被记录并返回。

:param dir_path: 要处理的文件夹的路径，可以是相对路径或绝对路径。
:param rules: 一个字典，键为文件后缀，值为处理该类型文件的函数和重命名函数的元组。
:param execution_mode: 执行模式，可以是 'serial' 或 'thread' 'process'。默认为 'serial'。
:param progress_desc: 进度条描述。
:return: 包含因错误未能正确处理的文件及其对应错误信息的列表。每个元素是一个元组，包括文件路径和错误对象。

### `compress_dir`
- 签名: `def compress_dir(dir_path: str | Path, execution_mode: str = 'thread') -> list[tuple[Path, Exception]]`
- 说明: 遍历指定文件夹，根据文件后缀名对文件进行压缩处理，并将处理后的文件存储到新的目录中。
支持的文件类型包括图片、视频和PDF。不属于这三种类型的文件将被直接复制到新目录中。
压缩后的文件会保持原始的目录结构。如果目标文件已存在，则会跳过处理。处理过程中遇到的任何错误都会被记录并返回。

:param dir_path: 要处理的文件夹的路径，可以是相对路径或绝对路径。
:param execution_mode: 执行模式，可以是 'serial' 或 'thread' 'process'。默认为 'thread'。
:return: 包含因错误未能正确处理的文件及其对应错误信息的列表。每个元素是一个元组，包括文件路径和错误对象。

### `unzip_zip_file`
- 签名: `def unzip_zip_file(zip_file: Path, destination: Path)`
- 说明: 解压缩指定的 zip 文件。

:param zip_file: 要解压缩的 zip 文件路径。
:raises ValueError: 如果文件不是有效的 zip 文件或发生其他错误。

### `unzip_rar_file`
- 签名: `def unzip_rar_file(rar_file: Path, destination: Path)`
- 说明: 解压缩指定的 rar 文件。

:param rar_file: 要解压缩的 rar 文件路径。

### `unzip_tar_file`
- 签名: `def unzip_tar_file(tar_file: Path, destination: Path)`
- 说明: 解压缩指定的 tar 文件。

:param tar_file: 要解压缩的 tar 文件路径。
:param destination: 解压缩的目标路径。
:raises ValueError: 如果文件不是有效的 tar 文件或发生其他错误。

### `unzip_7z_file`
- 签名: `def unzip_7z_file(seven_zip_file: Path, destination: Path)`
- 说明: 解压缩指定的 7z 文件。

:param seven_zip_file: 要解压缩的 7z 文件路径。
:raises ValueError: 如果文件不是有效的 7z 文件或发生其他错误。

### `unzip_dir`
- 签名: `def unzip_dir(dir_path: str | Path)`
- 说明: 遍历指定文件夹，解压缩所有支持的压缩文件。支持的文件类型包括 zip 和 rar。

:param dir_path: 要处理的文件夹的路径，可以是相对路径或绝对路径。

### `delete_file_or_dir`
- 签名: `def delete_file_or_dir(path: Path) -> None`
- 说明: 删除文件或文件夹。

:param path: 文件或文件夹路径。

### `copy_file_or_dir`
- 签名: `def copy_file_or_dir(source: Path, target: Path) -> None`
- 说明: 复制文件或文件夹。

:param source: 源文件或文件夹路径。
:param target: 目标文件或文件夹路径。

### `get_file_size`
- 签名: `def get_file_size(file_path: Path) -> HumanBytes`
- 说明: 获取文件大小。

:param file_path: 文件路径。
:return: 文件大小（HumanBytes）。

### `get_dir_size`
- 签名: `def get_dir_size(dir_path: Path) -> HumanBytes`
- 说明: 计算文件夹的大小。
遍历指定文件夹中的所有文件和子目录，并计算它们的大小总和。

:param dir_path: 文件夹的路径。
:return: 文件夹的总大小（HumanBytes）。

### `get_file_hash`
- 签名: `def get_file_hash(file_path: Path, algo: str = 'sha256', chunk_size: int = 65536) -> str`
- 说明: 计算文件的哈希值。

:param file_path: 文件路径。
:param algo: 哈希算法名称（如 'md5', 'sha1', 'sha256', 'sha512', 'blake2b' 等）。
:param chunk_size: 每次读取的文件块大小。
:return: 文件哈希字符串（十六进制）

### `get_dir_hash`
- 签名: `def get_dir_hash(dir_path: Path, exclude_dirs: list[str] | None = None, exclude_exts: list[str] | None = None, algo: str = 'sha256') -> str`
- 说明: 计算整个文件夹的哈希值（递归包含子文件）。
算法规则与 FileNode.hash 一致（目录哈希来自子节点哈希的组合）。

:param dir_path: 文件夹路径。
:param exclude_dirs: 要排除的目录名（不含路径）。
:param exclude_exts: 要排除的文件扩展名（含点，例如 ".tmp"）。
:param algo: 哈希算法名称，例如 'sha256', 'blake2b' 等。
:return: 文件夹的哈希字符串。

### `get_file_mtime`
- 签名: `def get_file_mtime(file_path: Path) -> HumanTimestamp`
- 说明: 获取文件的最后修改时间 (mtime)

:param file_path: 文件路径
:return: 文件的修改时间戳 (HumanTimestamp)

### `get_dir_mtime`
- 签名: `def get_dir_mtime(dir_path: Path) -> HumanTimestamp`
- 说明: 获取整个目录及其子项的最大修改时间 (递归)
即：取目录中所有文件与子目录的 mtime 最大值。

:param dir_path: 目录路径
:return: 目录内最新修改时间戳 (HumanTimestamp)

### `detect_identical_files`
- 签名: `def detect_identical_files(dir_list: list[Path], execution_mode: str = 'thread') -> dict[tuple[str, int], list[Path]]`
- 说明: 检测文件夹中是否存在相同内容的文件，并在文件名后添加文件大小。

:param dir_list: 文件夹路径列表。
:return: 相同文件的字典，键为文件大小和哈希值，值为文件路径列表。

### `detect_identical_dirs`
- 签名: `def detect_identical_dirs(dir_list: list[Path], execution_mode: str = 'thread') -> dict[tuple[str, int], list[Path]]`
- 说明: 检测文件夹中是否存在相同内容的文件，并在文件名后添加文件大小。

:param dir_list: 文件夹路径列表。
:return: 相同文件的字典，键为文件大小和哈希值，值为文件路径列表。

### `duplicate_files_report`
- 签名: `def duplicate_files_report(identical_dict: dict[tuple[str, HumanBytes], list[Path]])`
- 说明: 生成一个详细报告，列出所有重复的文件及其位置。

:param identical_dict: 相同文件的字典，由 detect_identical_files 函数返回。

### `delete_identical_files`
- 签名: `def delete_identical_files(identical_dict: dict[tuple[str, int], list[Path]])`
- 说明: 删除文件夹中相同内容的文件。

:param identical_dict: 相同文件的字典，由 detect_identical_files 函数返回。
:return: 删除的文件列表。

### `move_identical_files`
- 签名: `def move_identical_files(identical_dict: dict[tuple[str, int], list[Path]], target_dir: str | Path, size_threshold: int = None)`
- 说明: 将相同内容的文件移动到指定的目标文件夹。

:param identical_dict: 相同文件的字典，由 detect_identical_files 函数返回。
:param target_dir: 目标文件夹路径。
:param size_threshold: 文件大小阈值，只有大于此阈值的文件会被移动。如果为 None，则不限制文件大小。
:return: 移动的文件列表。

### `dir_to_file_path`
- 签名: `def dir_to_file_path(dir_path: Path, file_extension: str, parent_dir: Path = None) -> Path`
- 说明: 将文件夹路径转换为与文件夹同名的文件路径。
例如，给定文件夹路径 '/home/user/dir1' 和文件扩展名 'txt'，函数会返回文件路径 '/home/user/dir1.txt'。

:param dir_path: 文件夹的路径。
:param file_extension: 文件扩展名。
:param parent_dir: 文件夹的父目录路径，如果为 None，则使用文件夹的父目录。
:return: 与文件夹同名的文件路径。

### `replace_filenames`
- 签名: `def replace_filenames(dir_path: Path | str, pattern: str, replacement: str)`
- 说明: 使用正则表达式替换文件夹中所有文件名中的匹配部分。
遍历指定文件夹，将其中每个文件的文件名中的匹配内容替换为 `replacement`。

:param dir_path: 文件夹的路径。
:param pattern: 用于匹配文件名的正则表达式。
:param replacement: 替换后的新内容。

### `split_text_and_number`
- 签名: `def split_text_and_number(s: str, special_keywords: dict[str, int]) -> tuple`
- 说明: 将路径部分中的文本与数字交替提取，同时根据关键词设置优先级。
例如，"a1bbb2ccc3" -> (keyword_priority, "a", 1, "bbb", 2, "ccc", 3)

:param s: 要处理的字符串。
:param special_keywords: 关键词与其优先级的字典。
:return: 包含关键词优先级、文本和数字交替的元组。

### `sort_by_number`
- 签名: `def sort_by_number(file_path: Path, special_keywords: dict[str, int]) -> tuple`
- 说明: 文件排序规则：
1. 按路径中的每一层（包括文件名）进行文本与数字交替排序，同时考虑关键词优先级。
2. 文件名中按关键字优先级和数字进行排序。

:param file_path: 要排序的文件路径。
:param special_keywords: 关键词与其优先级的字典。
:return: 用于排序的元组。

### `move_files_with_keyword`
- 签名: `def move_files_with_keyword(source_dir: Path | str, target_dir: Path | str, keyword: str = None)`
- 说明: 将 source_dir 中所有文件名包含 keyword 的文件移动到 target_dir。

:param source_dir: 源文件夹路径（str 或 Path）
:param target_dir: 目标文件夹路径（str 或 Path）
:param keyword: 需要匹配的关键词（str）

### `extract_dir_numbers`
- 签名: `def extract_dir_numbers(dir_path: Path | str) -> set`
- 说明: 遍历给定文件夹，提取所有文件夹名称中匹配*(\d+)的数字部分，返回字典 {文件夹名: 数字(str)}。

:param dir_path: 文件夹路径（str 或 Path）
:return: 字典，包含文件夹名称和对应的数字部分。

### `extract_file_numbers`
- 签名: `def extract_file_numbers(dir_path: Path | str, suffix: str) -> set`
- 说明: 遍历给定文件夹，提取所有文件名中匹配*(\d+)的数字部分，返回字典 {文件夹名: 数字(str)}。

:param dir_path: 文件夹路径（str 或 Path）
:param suffix: 文件后缀名
:return: 字典，包含文件夹名称和对应的数字部分。

### `find_pure_dirs`
- 签名: `def find_pure_dirs(root: str | Path, only_nonempty: bool = False) -> list[Path]`
- 说明: 查找指定路径下所有的“纯粹文件夹”，即只包含文件而不包含子文件夹的文件夹。

:param root: 根目录路径
:param only_nonempty: 是否只返回至少包含一个文件的纯粹文件夹
:return: 纯粹文件夹的 Path 列表

### `align_width`
- 签名: `def align_width(s: str, max_len: int) -> str`
- 说明: 将字符串 s 左对齐到最大长度 max_len，如果需要则添加空格。

:param s: 输入字符串
:param max_len: 最大长度
:return: 左对齐后的字符串

### `append_hash_to_filename`
- 签名: `def append_hash_to_filename(file_path: Path) -> Path`
- 说明: 在文件名中添加哈希值标识

:param file_path: 文件路径
:return: 新文件路径

## 类
### `HandleFileExecutor`
- 继承: `TaskExecutor`
- 说明: 文件处理执行器，根据后缀规则对目录中的文件进行批量处理。
- 方法:
  - `def __init__(self, func: Callable, dir_path: Path, new_dir_path: Path, rules: dict[str, tuple[Callable, Callable]], execution_mode: str, progress_desc: str)`
  - `def get_args(self, file_path: Path)`
  - `def handle_error_dict(self)`

### `HandleSubFolderExecutor`
- 继承: `HandleFileExecutor`
- 说明: 子文件夹处理执行器，继承自 HandleFileExecutor，以子文件夹为单位进行批量处理。
- 方法:
  - `def get_args(self, sub_dir_path: Path)`
  - `def handle_error_dict(self)`

### `ScanSizeExecutor`
- 继承: `TaskExecutor`
- 说明: 文件大小扫描执行器，按大小分组并筛选出大小相同的文件。
- 方法:
  - `def process_result_dict(self)`

### `ScanHashExecutor`
- 继承: `TaskExecutor`
- 说明: 文件哈希扫描执行器，计算文件哈希值并筛选出哈希相同的文件。
- 方法:
  - `def get_args(self, task)`
  - `def process_result_dict(self)`

### `DeleteReturnSizeExecutor`
- 继承: `TaskExecutor`
- 说明: 删除文件执行器，删除文件后累计并返回已删除文件的总大小。
- 方法:
  - `def process_result_dict(self)`
