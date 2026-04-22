# `celestialvault.tools.FileOperations`

> 📅 最后更新日期: 2026/04/21

## 源文件

[src/celestialvault/tools/FileOperations.py](../../src/celestialvault/tools/FileOperations.py)

## 模块说明

文件操作工具模块，提供文件和文件夹的创建、复制、删除、压缩/解压缩、哈希计算、重复检测、批量处理等功能。是整个 celestialvault 工具链的核心模块，被其他模块广泛调用。

## 导入依赖

```python
import hashlib
import re
import shutil
import tarfile
import zipfile
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path
from typing import Any

import py7zr
import rarfile
from celestialflow import TaskExecutor
from tqdm import tqdm
from wcwidth import wcswidth

from ..constants import IMG_SUFFIXES, VIDEO_SUFFIXES
from ..instances.inst_units import HumanBytes, HumanTimestamp
from .TextTools import format_table
```

## 顶层函数

### `create_dir`

- 签名: `def create_dir(path: str | Path) -> Path`
- 说明: 判断系统是否存在该路径，没有则创建
- 参数:
  - `path` (str | Path): 要创建的文件夹路径
- 返回值: 创建或存在的文件夹路径
- 用法示例:
  ```python
  from celestialvault.tools.FileOperations import create_dir

  path = create_dir("output/results")
  ```
- 关联: 无

### `handle_item`

- 签名: `def handle_item(source: Path, destination: Path, action: Callable[[Path, Path, Any], Any], extra: dict)`
- 说明: 处理文件，如果目标文件不存在则执行指定的操作
- 参数:
  - `source` (Path): 源文件路径
  - `destination` (Path): 目标文件路径
  - `action` (Callable): 处理文件的函数或方法
  - `extra` (dict): 额外参数
- 返回值: 如果目标文件已存在，则返回提示字符串；否则返回 action 的结果
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.FileOperations import handle_item
  import shutil

  handle_item(Path("src.txt"), Path("dst.txt"), shutil.copy2, {})
  ```
- 关联: `handle_dir_files`, `handle_subdirs`

### `handle_dir_files`

- 签名: `def handle_dir_files(dir_path: str | Path, rules: dict[str, tuple[Callable[[Path, Path, dict], None], Callable[[Path], Path], dict]], execution_mode: str = "serial", progress_desc: str = "Processing files", dir_name_suffix: str = "_re") -> dict[tuple[str, str], list[Path]]`
- 说明: 遍历指定文件夹，根据文件后缀名对文件进行处理，并将处理后的文件存储到新的目录中。不属于指定后缀的文件将被直接复制。处理后的文件会保持原始的目录结构
- 参数:
  - `dir_path` (str | Path): 要处理的文件夹的路径
  - `rules` (dict): 键为文件后缀，值为 (处理函数, 重命名函数, 额外参数) 的元组
  - `execution_mode` (str): 执行模式，可以是 'serial'、'thread' 或 'process'，默认 'serial'
  - `progress_desc` (str): 进度条描述
  - `dir_name_suffix` (str): 新目录名后缀，默认 "_re"
- 返回值: 包含因错误未能正确处理的文件及其对应错误信息的字典
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.FileOperations import handle_dir_files

  rules = {".txt": (my_process_func, lambda x: x, {})}
  errors = handle_dir_files(Path("input_dir"), rules, execution_mode="thread")
  ```
- 关联: `handle_item`, `HandleFileExecutor`; 被 `celestialvault.tools.AudioProcessing`, `celestialvault.tools.VideoProcessing`, `celestialvault.tools.DocumentConversion` 等模块调用

### `handle_subdirs`

- 签名: `def handle_subdirs(dir_path: str | Path, rules: dict[str, tuple[Callable[[Path, Path, dict], None], Callable[[Path], Path], dict]], execution_mode: str = "serial", progress_desc: str = "Processing dirs", dir_name_suffix: str = "_re") -> dict[tuple[str, str], list[Path]]`
- 说明: 遍历指定文件夹，以子文件夹为单位进行批量处理
- 参数:
  - `dir_path` (str | Path): 要处理的文件夹的路径
  - `rules` (dict): 键为文件后缀，值为 (处理函数, 重命名函数, 额外参数) 的元组
  - `execution_mode` (str): 执行模式，默认 'serial'
  - `progress_desc` (str): 进度条描述
  - `dir_name_suffix` (str): 新目录名后缀，默认 "_re"
- 返回值: 包含因错误未能正确处理的文件及其对应错误信息的字典
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.FileOperations import handle_subdirs

  rules = {"dir": (process_dir, lambda x: x, {})}
  errors = handle_subdirs(Path("input_dir"), rules)
  ```
- 关联: `handle_item`, `HandleSubFolderExecutor`, `find_pure_dirs`; 被 `celestialvault.tools.ImageProcessing.combine_imgs_dir` 调用

### `compress_dir`

- 签名: `def compress_dir(dir_path: str | Path, execution_mode: str = "thread") -> list[tuple[Path, Exception]]`
- 说明: 遍历指定文件夹，根据文件后缀名对文件进行压缩处理。支持图片和视频类型
- 参数:
  - `dir_path` (str | Path): 要处理的文件夹的路径
  - `execution_mode` (str): 执行模式，默认 'thread'
- 返回值: 包含因错误未能正确处理的文件及其对应错误信息的列表
- 用法示例:
  ```python
  from celestialvault.tools.FileOperations import compress_dir

  errors = compress_dir("media_folder", execution_mode="thread")
  ```
- 关联: `handle_dir_files`, `celestialvault.tools.ImageProcessing.compress_img`, `celestialvault.tools.VideoProcessing.compress_video`

### `unzip_zip_file`

- 签名: `def unzip_zip_file(zip_file: Path, destination: Path)`
- 说明: 解压缩指定的 zip 文件
- 参数:
  - `zip_file` (Path): 要解压缩的 zip 文件路径
  - `destination` (Path): 解压缩的目标路径
- 返回值: 无
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.FileOperations import unzip_zip_file

  unzip_zip_file(Path("archive.zip"), Path("output/"))
  ```
- 关联: `unzip_dir`

### `unzip_rar_file`

- 签名: `def unzip_rar_file(rar_file: Path, destination: Path)`
- 说明: 解压缩指定的 rar 文件
- 参数:
  - `rar_file` (Path): 要解压缩的 rar 文件路径
  - `destination` (Path): 解压缩的目标路径
- 返回值: 无
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.FileOperations import unzip_rar_file

  unzip_rar_file(Path("archive.rar"), Path("output/"))
  ```
- 关联: `unzip_dir`

### `unzip_tar_file`

- 签名: `def unzip_tar_file(tar_file: Path, destination: Path)`
- 说明: 解压缩指定的 tar 文件
- 参数:
  - `tar_file` (Path): 要解压缩的 tar 文件路径
  - `destination` (Path): 解压缩的目标路径
- 返回值: 无
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.FileOperations import unzip_tar_file

  unzip_tar_file(Path("archive.tar.gz"), Path("output/"))
  ```
- 关联: `unzip_dir`

### `unzip_7z_file`

- 签名: `def unzip_7z_file(seven_zip_file: Path, destination: Path)`
- 说明: 解压缩指定的 7z 文件
- 参数:
  - `seven_zip_file` (Path): 要解压缩的 7z 文件路径
  - `destination` (Path): 解压缩的目标路径
- 返回值: 无
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.FileOperations import unzip_7z_file

  unzip_7z_file(Path("archive.7z"), Path("output/"))
  ```
- 关联: `unzip_dir`

### `unzip_dir`

- 签名: `def unzip_dir(dir_path: str | Path)`
- 说明: 遍历指定文件夹，解压缩所有支持的压缩文件。支持 zip、rar、tar、7z
- 参数:
  - `dir_path` (str | Path): 要处理的文件夹的路径
- 返回值: 处理结果字典
- 用法示例:
  ```python
  from celestialvault.tools.FileOperations import unzip_dir

  unzip_dir("compressed_files/")
  ```
- 关联: `unzip_zip_file`, `unzip_rar_file`, `unzip_tar_file`, `unzip_7z_file`, `handle_dir_files`

### `delete_file_or_dir`

- 签名: `def delete_file_or_dir(path: Path) -> None`
- 说明: 删除文件或文件夹
- 参数:
  - `path` (Path): 文件或文件夹路径
- 返回值: 无
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.FileOperations import delete_file_or_dir

  delete_file_or_dir(Path("temp_folder"))
  ```
- 关联: 无

### `copy_file_or_dir`

- 签名: `def copy_file_or_dir(source: Path, target: Path) -> None`
- 说明: 复制文件或文件夹
- 参数:
  - `source` (Path): 源文件或文件夹路径
  - `target` (Path): 目标文件或文件夹路径
- 返回值: 无
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.FileOperations import copy_file_or_dir

  copy_file_or_dir(Path("src/"), Path("backup/"))
  ```
- 关联: 无

### `get_file_size`

- 签名: `def get_file_size(file_path: Path) -> HumanBytes`
- 说明: 获取文件大小
- 参数:
  - `file_path` (Path): 文件路径
- 返回值: 文件大小（HumanBytes）
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.FileOperations import get_file_size

  size = get_file_size(Path("large_file.bin"))
  print(size)  # 例如 "1.5 GB"
  ```
- 关联: `detect_identical_files`, `get_file_info`

### `get_dir_size`

- 签名: `def get_dir_size(dir_path: Path) -> HumanBytes`
- 说明: 计算文件夹的大小，遍历所有文件和子目录并计算总大小
- 参数:
  - `dir_path` (Path): 文件夹的路径
- 返回值: 文件夹的总大小（HumanBytes）
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.FileOperations import get_dir_size

  total = get_dir_size(Path("project/"))
  print(f"文件夹大小: {total}")
  ```
- 关联: `detect_identical_dirs`

### `get_file_hash`

- 签名: `def get_file_hash(file_path: Path, algo: str = "sha256", chunk_size: int = 65536) -> str`
- 说明: 计算文件的哈希值
- 参数:
  - `file_path` (Path): 文件路径
  - `algo` (str): 哈希算法名称（如 'md5', 'sha1', 'sha256', 'sha512', 'blake2b' 等）
  - `chunk_size` (int): 每次读取的文件块大小
- 返回值: 文件哈希字符串（十六进制）
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.FileOperations import get_file_hash

  h = get_file_hash(Path("file.bin"), algo="md5")
  print(h)
  ```
- 关联: `detect_identical_files`, `get_dir_hash`, `append_hash_to_filename`, `get_file_info`

### `get_dir_hash`

- 签名: `def get_dir_hash(dir_path: Path, exclude_dirs: list[str] | None = None, exclude_exts: list[str] | None = None, algo: str = "sha256") -> str`
- 说明: 计算整个文件夹的哈希值（递归包含子文件），目录哈希来自子节点哈希的组合
- 参数:
  - `dir_path` (Path): 文件夹路径
  - `exclude_dirs` (list[str] | None): 要排除的目录名
  - `exclude_exts` (list[str] | None): 要排除的文件扩展名（含点，例如 ".tmp"）
  - `algo` (str): 哈希算法名称
- 返回值: 文件夹的哈希字符串
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.FileOperations import get_dir_hash

  h = get_dir_hash(Path("project/"), exclude_dirs=["__pycache__"], exclude_exts=[".pyc"])
  ```
- 关联: `get_file_hash`, `detect_identical_dirs`

### `get_file_mtime`

- 签名: `def get_file_mtime(file_path: Path) -> HumanTimestamp`
- 说明: 获取文件的最后修改时间 (mtime)
- 参数:
  - `file_path` (Path): 文件路径
- 返回值: 文件的修改时间戳 (HumanTimestamp)
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.FileOperations import get_file_mtime

  mtime = get_file_mtime(Path("file.txt"))
  print(mtime)
  ```
- 关联: `get_dir_mtime`, `get_file_info`

### `get_dir_mtime`

- 签名: `def get_dir_mtime(dir_path: Path) -> HumanTimestamp`
- 说明: 获取整个目录及其子项的最大修改时间（递归）
- 参数:
  - `dir_path` (Path): 目录路径
- 返回值: 目录内最新修改时间戳 (HumanTimestamp)
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.FileOperations import get_dir_mtime

  mtime = get_dir_mtime(Path("project/"))
  print(f"最近修改: {mtime}")
  ```
- 关联: `get_file_mtime`

### `get_file_info`

- 签名: `def get_file_info(file_path: Path, include_hash: bool = False) -> dict[str, Any]`
- 说明: 获取文件的详细信息，包括大小、修改时间和可选的哈希值
- 参数:
  - `file_path` (Path): 文件路径
  - `include_hash` (bool): 是否包含哈希值
- 返回值: 包含文件信息的字典
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.FileOperations import get_file_info

  info = get_file_info(Path("data.csv"), include_hash=True)
  print(info)  # {'size': ..., 'mtime': ..., 'hash': ...}
  ```
- 关联: `get_file_size`, `get_file_hash`, `get_file_mtime`

### `detect_identical_files`

- 签名: `def detect_identical_files(dir_list: list[Path], execution_mode: str = "thread") -> dict[tuple[str, int], list[Path]]`
- 说明: 检测文件夹中是否存在相同内容的文件
- 参数:
  - `dir_list` (list[Path]): 文件夹路径列表
  - `execution_mode` (str): 执行模式，默认 "thread"
- 返回值: 相同文件的字典，键为 (哈希值, 文件大小)，值为文件路径列表
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.FileOperations import detect_identical_files

  duplicates = detect_identical_files([Path("folder1"), Path("folder2")])
  for key, paths in duplicates.items():
      print(f"重复: {key} -> {paths}")
  ```
- 关联: `get_file_size`, `get_file_hash`, `duplicate_report`, `delete_identical`, `move_identical`, `ScanSizeExecutor`, `ScanHashExecutor`

### `detect_identical_dirs`

- 签名: `def detect_identical_dirs(dir_list: list[Path], execution_mode: str = "thread") -> dict[tuple[str, HumanBytes], list[Path]]`
- 说明: 检测文件夹中是否存在相同内容的文件夹
- 参数:
  - `dir_list` (list[Path]): 文件夹路径列表
  - `execution_mode` (str): 执行模式，默认 "thread"
- 返回值: 相同文件夹的字典，键为 (哈希值, 文件夹大小)，值为文件夹路径列表
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.FileOperations import detect_identical_dirs

  duplicates = detect_identical_dirs([Path("root_folder")])
  ```
- 关联: `get_dir_size`, `get_dir_hash`, `find_pure_dirs`, `duplicate_report`

### `duplicate_report`

- 签名: `def duplicate_report(identical_dict: dict[tuple[str, HumanBytes], list[Path]]) -> str`
- 说明: 生成一个详细报告，列出所有重复的文件/文件夹及其位置
- 参数:
  - `identical_dict` (dict): 相同文件的字典，由 detect_identical_files/detect_identical_dirs 返回
- 返回值: 详细报告字符串
- 用法示例:
  ```python
  from celestialvault.tools.FileOperations import detect_identical_files, duplicate_report

  duplicates = detect_identical_files([Path("folder")])
  report = duplicate_report(duplicates)
  print(report)
  ```
- 关联: `detect_identical_files`, `detect_identical_dirs`, `celestialvault.tools.TextTools.format_table`

### `delete_identical`

- 签名: `def delete_identical(identical_dict: dict[tuple[str, HumanBytes], list[Path]])`
- 说明: 删除文件夹中相同内容的文件
- 参数:
  - `identical_dict` (dict): 相同文件的字典，由 detect_identical_files/detect_identical_dirs 返回
- 返回值: 无
- 用法示例:
  ```python
  from celestialvault.tools.FileOperations import detect_identical_files, delete_identical

  duplicates = detect_identical_files([Path("folder")])
  delete_identical(duplicates)
  ```
- 关联: `detect_identical_files`, `DeleteReturnSizeExecutor`

### `move_identical`

- 签名: `def move_identical(identical_dict: dict[tuple[str, HumanBytes], list[Path]], target_dir: str | Path, size_threshold: HumanBytes = None)`
- 说明: 将相同内容的文件移动到指定的目标文件夹
- 参数:
  - `identical_dict` (dict): 相同文件的字典
  - `target_dir` (str | Path): 目标文件夹路径
  - `size_threshold` (HumanBytes): 文件大小阈值，只有大于此阈值的文件会被移动。如果为 None，则不限制
- 返回值: 移动的文件字典
- 用法示例:
  ```python
  from celestialvault.tools.FileOperations import detect_identical_files, move_identical

  duplicates = detect_identical_files([Path("folder")])
  move_identical(duplicates, "duplicates_backup/")
  ```
- 关联: `detect_identical_files`

### `dir_to_file_path`

- 签名: `def dir_to_file_path(dir_path: Path, file_extension: str, parent_dir: Path = None) -> Path`
- 说明: 将文件夹路径转换为与文件夹同名的文件路径。例如 '/home/user/dir1' + 'txt' -> '/home/user/dir1.txt'
- 参数:
  - `dir_path` (Path): 文件夹的路径
  - `file_extension` (str): 文件扩展名
  - `parent_dir` (Path): 文件夹的父目录路径，如果为 None 则使用文件夹的父目录
- 返回值: 与文件夹同名的文件路径
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.FileOperations import dir_to_file_path

  file_path = dir_to_file_path(Path("images/album"), "pdf")
  print(file_path)  # images/album.pdf
  ```
- 关联: 被 `celestialvault.tools.ImageProcessing.combine_imgs_to_pdf`, `celestialvault.tools.DocumentConversion.merge_pdfs_in_order` 调用

### `replace_filenames`

- 签名: `def replace_filenames(dir_path: Path | str, pattern: str, replacement: str)`
- 说明: 使用正则表达式替换文件夹中所有文件名中的匹配部分
- 参数:
  - `dir_path` (Path | str): 文件夹的路径
  - `pattern` (str): 用于匹配文件名的正则表达式
  - `replacement` (str): 替换后的新内容
- 返回值: 无
- 用法示例:
  ```python
  from celestialvault.tools.FileOperations import replace_filenames

  replace_filenames("photos/", r"IMG_(\d+)", r"photo_\1")
  ```
- 关联: 无

### `split_text_and_number`

- 签名: `def split_text_and_number(s: str, special_keywords: dict[str, int]) -> tuple`
- 说明: 将路径部分中的文本与数字交替提取，同时根据关键词设置优先级。例如 "a1bbb2ccc3" -> (keyword_priority, "a", 1, "bbb", 2, "ccc", 3)
- 参数:
  - `s` (str): 要处理的字符串
  - `special_keywords` (dict[str, int]): 关键词与其优先级的字典
- 返回值: 包含关键词优先级、文本和数字交替的元组
- 用法示例:
  ```python
  from celestialvault.tools.FileOperations import split_text_and_number

  result = split_text_and_number("chapter3part2", {"附录": 1})
  # (inf, 'chapter', 3, 'part', 2)
  ```
- 关联: `sort_by_number`

### `sort_by_number`

- 签名: `def sort_by_number(file_path: Path, special_keywords: dict[str, int]) -> tuple`
- 说明: 文件排序规则，按路径中的每一层进行文本与数字交替排序，同时考虑关键词优先级
- 参数:
  - `file_path` (Path): 要排序的文件路径
  - `special_keywords` (dict[str, int]): 关键词与其优先级的字典
- 返回值: 用于排序的元组
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.FileOperations import sort_by_number

  files = [Path("ch1.pdf"), Path("ch10.pdf"), Path("ch2.pdf")]
  sorted_files = sorted(files, key=lambda p: sort_by_number(p, {}))
  ```
- 关联: `split_text_and_number`; 被 `celestialvault.tools.ImageProcessing.combine_imgs_to_pdf`, `celestialvault.tools.DocumentConversion.merge_pdfs_in_order` 调用

### `move_files_with_keyword`

- 签名: `def move_files_with_keyword(source_dir: Path | str, target_dir: Path | str, keyword: str = None)`
- 说明: 将 source_dir 中所有文件名包含 keyword 的文件移动到 target_dir
- 参数:
  - `source_dir` (Path | str): 源文件夹路径
  - `target_dir` (Path | str): 目标文件夹路径
  - `keyword` (str): 需要匹配的关键词
- 返回值: 无
- 用法示例:
  ```python
  from celestialvault.tools.FileOperations import move_files_with_keyword

  move_files_with_keyword("downloads/", "images/", keyword=".jpg")
  ```
- 关联: 无

### `extract_dir_numbers`

- 签名: `def extract_dir_numbers(dir_path: Path | str) -> set`
- 说明: 遍历给定文件夹，提取所有文件夹名称中匹配 `(\d+)` 的数字部分
- 参数:
  - `dir_path` (Path | str): 文件夹路径
- 返回值: 包含数字部分的集合
- 用法示例:
  ```python
  from celestialvault.tools.FileOperations import extract_dir_numbers

  nums = extract_dir_numbers("comics/")
  print(nums)  # {'1', '2', '15'}
  ```
- 关联: `extract_file_numbers`

### `extract_file_numbers`

- 签名: `def extract_file_numbers(dir_path: Path | str, suffix: str) -> set`
- 说明: 遍历给定文件夹，提取所有指定后缀文件名中匹配 `(\d+)` 的数字部分
- 参数:
  - `dir_path` (Path | str): 文件夹路径
  - `suffix` (str): 文件后缀名
- 返回值: 包含数字部分的集合
- 用法示例:
  ```python
  from celestialvault.tools.FileOperations import extract_file_numbers

  nums = extract_file_numbers("books/", ".txt")
  ```
- 关联: `extract_dir_numbers`

### `is_pure_dir`

- 签名: `def is_pure_dir(dir: Path | str, only_nonempty: bool = False) -> bool`
- 说明: 判断一个文件夹是否为"纯粹文件夹"，即只包含文件而不包含子文件夹
- 参数:
  - `dir` (Path | str): 文件夹路径
  - `only_nonempty` (bool): 是否只返回至少包含一个文件的纯粹文件夹
- 返回值: True 表示是纯粹文件夹，False 表示不是
- 用法示例:
  ```python
  from celestialvault.tools.FileOperations import is_pure_dir

  print(is_pure_dir("flat_folder/"))  # True
  ```
- 关联: `find_pure_dirs`

### `find_pure_dirs`

- 签名: `def find_pure_dirs(root: str | Path, only_nonempty: bool = False) -> list[Path]`
- 说明: 查找指定路径下所有的"纯粹文件夹"，即只包含文件而不包含子文件夹的文件夹
- 参数:
  - `root` (str | Path): 根目录路径
  - `only_nonempty` (bool): 是否只返回至少包含一个文件的纯粹文件夹
- 返回值: 纯粹文件夹的 Path 列表
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.FileOperations import find_pure_dirs

  pure = find_pure_dirs(Path("project/"))
  for d in pure:
      print(d)
  ```
- 关联: `is_pure_dir`, `FindPureExecutor`, `handle_subdirs`, `detect_identical_dirs`

### `align_width`

- 签名: `def align_width(s: str, max_len: int) -> str`
- 说明: 将字符串左对齐到最大长度，如果需要则添加空格（考虑宽字符）
- 参数:
  - `s` (str): 输入字符串
  - `max_len` (int): 最大长度
- 返回值: 左对齐后的字符串
- 用法示例:
  ```python
  from celestialvault.tools.FileOperations import align_width

  print(align_width("hello", 10))
  ```
- 关联: 无

### `append_hash_to_filename`

- 签名: `def append_hash_to_filename(file_path: Path) -> Path`
- 说明: 在文件名中添加哈希值标识
- 参数:
  - `file_path` (Path): 文件路径
- 返回值: 新文件路径
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.FileOperations import append_hash_to_filename

  new_path = append_hash_to_filename(Path("photo.jpg"))
  # photo(a1b2c3...).jpg
  ```
- 关联: `get_file_hash`

## 类

### `HandleFileExecutor`

- 继承: `TaskExecutor` (from celestialflow)
- 说明: 文件处理执行器，根据后缀规则对目录中的文件进行批量处理
- 方法:
  - #### `__init__`
    - 签名: `def __init__(self, func: Callable, dir_path: Path, new_dir_path: Path, rules: dict[str, tuple[Callable, Callable]], execution_mode: str, progress_desc: str)`
    - 说明: 初始化文件处理执行器
  - #### `get_args`
    - 签名: `def get_args(self, task: Path)`
    - 说明: 根据文件后缀匹配处理规则，返回传递给处理函数的参数元组
    - 参数:
      - `task` (Path): 待处理文件的绝对路径
    - 返回值: (源路径, 目标路径, 处理函数, 额外参数) 的元组
- 关联: `handle_dir_files`, `HandleSubFolderExecutor`

### `HandleSubFolderExecutor`

- 继承: `HandleFileExecutor`
- 说明: 子文件夹处理执行器，继承自 HandleFileExecutor，以子文件夹为单位进行批量处理
- 方法:
  - #### `get_args`
    - 签名: `def get_args(self, task: Path)`
    - 说明: 根据子文件夹匹配 'dir' 规则，返回传递给处理函数的参数元组
    - 参数:
      - `task` (Path): 待处理子文件夹的绝对路径
    - 返回值: (源路径, 目标路径, 处理函数, 额外参数) 的元组
- 关联: `handle_subdirs`

### `ScanSizeExecutor`

- 继承: `TaskExecutor`
- 说明: 文件大小扫描执行器，按大小分组并筛选出大小相同的文件
- 关联: `detect_identical_files`, `detect_identical_dirs`

### `ScanHashExecutor`

- 继承: `TaskExecutor`
- 说明: 文件哈希扫描执行器，计算文件哈希值并筛选出哈希相同的文件
- 方法:
  - #### `get_args`
    - 签名: `def get_args(self, task)`
    - 说明: 从 (path, size) 元组中提取文件路径作为哈希计算的参数
    - 参数:
      - `task`: (文件路径, 文件大小) 元组
    - 返回值: 仅包含文件路径的元组
- 关联: `detect_identical_files`, `detect_identical_dirs`

### `DeleteReturnSizeExecutor`

- 继承: `TaskExecutor`
- 说明: 删除文件执行器，删除文件后累计并返回已删除文件的总大小
- 关联: `delete_identical`

### `FindPureExecutor`

- 继承: `TaskExecutor`
- 说明: 查找纯粹文件夹执行器，返回所有纯粹文件夹的路径
- 关联: `find_pure_dirs`
