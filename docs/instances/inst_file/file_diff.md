# instances/inst_file/file_diff.py

## 源文件
- `src/celestialvault/instances/inst_file/file_diff.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- `from pathlib import Path`
- `from dataclasses import dataclass`
- `from celestialflow import TaskExecutor`
- `from typing import TYPE_CHECKING`
- `from ...instances.inst_units import HumanBytes, HumanTimestamp`
- `from ...tools.FileOperations import delete_file_or_dir, copy_file_or_dir, append_hash_to_filename`
- `from ...tools.TextTools import format_table`
- `from .file_node import FileNode, DirNode`

## 模块常量
- 无

## 顶层函数
- 无

## 类
### `DeleteExecutor`
- 继承: `TaskExecutor`
- 说明: 删除执行器，根据相对路径批量删除指定目录下的文件或文件夹。
- 方法:
  - `def __init__(self, func, parent_dir: Path)`
  - `def get_args(self, rel_path: Path)`

### `CopyExecutor`
- 继承: `TaskExecutor`
- 说明: 复制执行器，根据相对路径将文件从主目录批量复制到次目录。
- 方法:
  - `def __init__(self, func, main_dir: Path, minor_dir: Path, copy_mode: str)`
  - `def get_args(self, rel_path: Path)`

### `FileDiff`
- 继承: `object`
- 说明: 两个目录的差异比较结果，包含仅存在于单侧的文件和内容不同的文件列表。
- 方法:
  - `def is_identical(self) -> bool`
  - `def print_diff_tree(self)`
  - `def sync_dirs(self, mode: str = '->')`
  - `def to_dict(self)`

## 节点判断
- `inst_file` 中的节点模型以 `BaseNode.is_dir` 表示目录/文件类型。
- 本文档描述中，凡是涉及“节点是否为目录”的判断，统一按 `.is_dir` 理解。
