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
- `from ...tools.FileOperations import get_file_size, get_file_mtime`
- `from .file_node import FileNode, DirNode`
- `from .file_util import to_string`

## 模块常量
- 无

## 顶层函数
- 无

## 类
### `FileTree`
- 继承: `object`
- 说明: 无模块级文档字符串。
- 方法:
  - `def __init__(self, root: DirNode, path: Path)`
  - `def build_from_path(cls, root_path: Path)`
  - `def print_tree(self, exclude_names=None, exclude_exts=None, max_depth=3)`

## 节点判断
- `inst_file` 模块的基础节点设计已经引入 `BaseNode.is_dir`。
- 本目录下文档凡是涉及“节点是否为目录”的判断，统一以 `.is_dir` 作为理解方式。
