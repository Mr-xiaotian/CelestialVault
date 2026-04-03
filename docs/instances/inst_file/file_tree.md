# instances/inst_file/file_tree.py

## 源文件
- `src/celestialvault/instances/inst_file/file_tree.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- `from pathlib import Path`
- `from wcwidth import wcswidth`
- `from ...constants import FILE_ICONS`
- `from ...instances.inst_units import HumanBytes, HumanTimestamp`
- `from ...tools.FileOperations import get_file_size, get_dir_size, get_file_mtime, get_dir_mtime`
- `from .file_node import FileNode`
- `from .file_diff import FileDiff`

## 模块常量
- 无

## 顶层函数
- 无

## 类
### `FileTree`
- 继承: `object`
- 说明: 无模块级文档字符串。
- 方法:
  - `def __init__(self, root: FileNode, path: Path)`
  - `def build_from_path(cls, root_path: Path, exclude_dirs = None, exclude_exts = None, max_depth = 3)`
  - `def print_tree(self)`
  - `def compare_with(self, other: 'FileTree', compare_hash: bool = False) -> 'FileDiff'`
