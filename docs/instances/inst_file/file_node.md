# `celestialvault.instances.inst_file.file_node`

> 📅 最后更新日期: 2026/04/21

## 源文件 - `src/celestialvault/instances/inst_file/file_node.py`

## 模块说明

定义文件树的节点类型：基类 `BaseNode`、文件节点 `FileNode` 和目录节点 `DirNode`。节点包含名称、路径、大小、修改时间等元信息，支持惰性哈希计算和格式化打印。

## 导入依赖

- `hashlib` - 哈希计算
- `pathlib.Path` - 路径操作
- `dataclasses.dataclass` - 数据类装饰器
- `celestialvault.instances.inst_units.HumanBytes` - 人类可读字节大小
- `celestialvault.instances.inst_units.HumanTimestamp` - 人类可读时间戳
- `celestialvault.tools.FileOperations.get_file_hash` - 文件哈希计算
- `celestialvault.tools.FileOperations.get_file_mtime` - 文件修改时间获取
- `celestialvault.tools.FileOperations.get_dir_mtime` - 目录修改时间获取
- `celestialvault.instances.inst_file.file_util.to_string` - 节点字符串格式化

## 类

### `BaseNode`

- 继承: 无
- 说明: 文件与目录节点的公共基类。

- 构造函数: `__init__(self, name: str, node_path: Path, size: HumanBytes, mtime: HumanTimestamp, icon: str, level: int)`
  - 参数:
    - `name` (`str`): 节点名称。
    - `node_path` (`Path`): 节点的文件系统路径。
    - `size` (`HumanBytes`): 节点大小。
    - `mtime` (`HumanTimestamp`): 节点修改时间。
    - `icon` (`str`): 节点显示图标。
    - `level` (`int`): 节点在文件树中的深度。
  - 属性:
    - `self._hash` (`str | None`): 缓存的哈希值，初始为 `None`。

- 方法:

  #### `print(self, level=None, prefix=None, name=None, suffix=None, max_name_len=None)`
  - 签名: `print(self, level: int = None, prefix: str = None, name: str = None, suffix: str = None, max_name_len: int = None) -> None`
  - 说明: 打印节点信息，使用 `to_string` 格式化输出。
  - 参数:
    - `level` (`int | None`): 缩进级别，默认使用节点自身层级。
    - `prefix` (`str | None`): 前缀字符串，默认空。
    - `name` (`str | None`): 显示名称，默认使用节点名称。
    - `suffix` (`str | None`): 后缀字符串，默认显示大小 `(size)`。
    - `max_name_len` (`int | None`): 名称对齐的最大长度。

- 关联: 被 `FileNode` 和 `DirNode` 继承。

---

### `FileNode`

- 继承: `BaseNode`（`@dataclass` 装饰）
- 说明: 文件节点，表示文件树中的一个文件。

- 构造函数: `__init__(self, name: str, suffix: str, node_path: Path, size: HumanBytes, mtime: HumanTimestamp, icon: str, level: int)`
  - 参数:
    - `name` (`str`): 文件名。
    - `suffix` (`str`): 文件后缀。
    - `node_path` (`Path`): 文件路径。
    - `size` (`HumanBytes`): 文件大小。
    - `mtime` (`HumanTimestamp`): 文件修改时间。
    - `icon` (`str`): 显示图标。
    - `level` (`int`): 节点深度。

- 方法:

  #### `hash` (属性)
  - 签名: `hash(self) -> str`
  - 说明: 惰性计算文件哈希。如果文件不存在返回空字符串；如果 mtime 未变化则返回缓存值；否则重新计算。

  #### `is_dir(self)`
  - 签名: `is_dir(self) -> bool`
  - 说明: 返回 `False`，表示文件节点。

- 关联: 被 `file_tree.FileTree` 构建和使用；被 `file_diff.compare_trees` 比较。

---

### `DirNode`

- 继承: `BaseNode`（`@dataclass` 装饰）
- 说明: 目录节点，维护子节点列表。图标固定为 "📁"。

- 构造函数: `__init__(self, name: str, node_path: Path, size: HumanBytes, mtime: HumanTimestamp, level: int, children: list[BaseNode])`
  - 参数:
    - `name` (`str`): 目录名。
    - `node_path` (`Path`): 目录路径。
    - `size` (`HumanBytes`): 目录总大小。
    - `mtime` (`HumanTimestamp`): 目录修改时间。
    - `level` (`int`): 节点深度。
    - `children` (`list[BaseNode]`): 子节点列表。

- 方法:

  #### `hash` (属性)
  - 签名: `hash(self) -> str`
  - 说明: 惰性计算目录哈希。基于子节点哈希值组合计算。如果目录不存在返回空字符串；如果 mtime 未变化则返回缓存值。

  #### `_compute_dir_hash(self, algo='sha256')`
  - 签名: `_compute_dir_hash(self, algo: str = 'sha256') -> str`
  - 说明: 根据子节点组合计算目录哈希。按目录优先、名称排序遍历子节点，将每个子节点的类型标记（D/F）、名称和哈希拼接后计算哈希。无子节点时使用 `[EMPTY]` 作为输入。
  - 参数: `algo` (`str`): 哈希算法，默认 `'sha256'`。
  - 返回值: 目录的哈希字符串。

  #### `is_dir(self)`
  - 签名: `is_dir(self) -> bool`
  - 说明: 返回 `True`，表示目录节点。

- 用法示例:

```python
from pathlib import Path
from celestialvault.instances.inst_file.file_node import FileNode, DirNode
from celestialvault.instances.inst_units import HumanBytes, HumanTimestamp

# 创建文件节点
file_node = FileNode(
    name="readme.txt",
    suffix=".txt",
    node_path=Path("/project/readme.txt"),
    size=HumanBytes(1024),
    mtime=HumanTimestamp.now(),
    icon="📄",
    level=1,
)
file_node.print()  # 打印文件节点信息

# 创建目录节点
dir_node = DirNode(
    name="project",
    node_path=Path("/project"),
    size=HumanBytes(4096),
    mtime=HumanTimestamp.now(),
    level=0,
    children=[file_node],
)
print(dir_node.hash)  # 计算目录哈希
```

- 关联: 被 `file_tree.FileTree` 构建和使用；被 `file_diff.compare_trees` 和 `file_diff.FileDiff` 使用；使用 `inst_units.HumanBytes` 和 `HumanTimestamp` 表示大小和时间；使用 `file_util.to_string` 格式化打印。
