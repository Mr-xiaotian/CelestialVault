# instances/inst_file/file_node.py

## 源文件
- `src/celestialvault/instances/inst_file/file_node.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- `import hashlib`
- `from pathlib import Path`
- `from dataclasses import dataclass`
- `from ...instances.inst_units import HumanBytes, HumanTimestamp`
- `from ...tools.FileOperations import get_file_hash, get_file_mtime, get_dir_mtime`
- `from .file_util import to_string`

## 模块常量
- 无

## 顶层函数
- 无

## 类
### `BaseNode`
- 继承: `object`
- 说明: 文件与目录节点的公共基类，通过 `is_dir` 区分节点类型。
- 主要属性:
  - `name`
  - `node_path`
  - `size`
  - `mtime`
  - `icon`
  - `level`
  - `is_dir`
- 方法:
  - `def __init__(self, name: str, node_path: Path, size: HumanBytes, mtime: HumanTimestamp, icon: str, level: int, is_dir: bool)`
  - `def print(self, prefix: str = None, name: str = None, suffix: str = None, max_name_len: int = None)`

### `FileNode`
- 继承: `BaseNode`
- 说明: 无模块级文档字符串。
- 方法:
  - `def __init__(self, name: str, suffix: str, node_path: Path, size: HumanBytes, mtime: HumanTimestamp, icon: str, level: int)`
  - `def hash(self) -> str`

### `DirNode`
- 继承: `BaseNode`
- 说明: 目录节点，`is_dir=True`，并维护 `children` 列表。
- 方法:
  - `def __init__(self, name: str, node_path: Path, size: HumanBytes, mtime: HumanTimestamp, icon: str, level: int, children: list["DirNode"])`
  - `def hash(self) -> str`
  - `def _compute_dir_hash(self, algo: str = 'sha256') -> str`
