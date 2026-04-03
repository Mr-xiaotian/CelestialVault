# instances/inst_file/file_node.py

## 源文件
- `src/celestialvault/instances/inst_file/file_node.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- `import hashlib`
- `from pathlib import Path`
- `from dataclasses import dataclass, field`
- `from ...instances.inst_units import HumanBytes, HumanTimestamp`
- `from ...tools.FileOperations import get_file_hash, get_file_mtime, get_dir_mtime, align_width`

## 模块常量
- 无

## 顶层函数
- 无

## 类
### `FileNode`
- 继承: `object`
- 说明: 无模块级文档字符串。
- 方法:
  - `def to_string(self, indent: str = '', prefix: str = '', suffix: str = '') -> str`
  - `def __repr__(self)`
  - `def hash(self) -> str`
  - `def _compute_dir_hash(self, algo: str = 'sha256') -> str`
