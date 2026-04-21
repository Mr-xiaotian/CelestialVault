# `celestialvault.instances.inst_file.file_diff`

## 源文件 - `src/celestialvault/instances/inst_file/file_diff.py`

## 模块说明

提供目录差异比较功能，包含批量删除/复制执行器、差异结果数据类 `FileDiff` 和目录树对比函数 `compare_trees`。

## 导入依赖

- `pathlib.Path` - 路径操作
- `dataclasses.dataclass` - 数据类
- `celestialflow.TaskExecutor` - 任务执行器
- `wcwidth.wcswidth` - 宽字符宽度计算
- `celestialvault.instances.inst_units.HumanBytes` - 人类可读字节大小
- `celestialvault.instances.inst_units.HumanTimestamp` - 人类可读时间戳
- `celestialvault.tools.FileOperations.delete_file_or_dir` - 文件/目录删除
- `celestialvault.tools.FileOperations.copy_file_or_dir` - 文件/目录复制
- `celestialvault.tools.FileOperations.append_hash_to_filename` - 文件名追加哈希
- `celestialvault.tools.TextTools.format_table` - 表格格式化
- `celestialvault.instances.inst_file.file_node.BaseNode` - 基础节点
- `celestialvault.instances.inst_file.file_node.DirNode` - 目录节点
- `celestialvault.instances.inst_file.file_tree.FileTree` - 文件树

## 类

### `DeleteExecutor`

- 继承: `TaskExecutor` (from `celestialflow`)
- 说明: 删除执行器，根据相对路径批量删除指定目录下的文件或文件夹。

- 构造函数: `__init__(self, func, parent_dir: Path)`
  - 参数:
    - `func`: 删除函数（如 `delete_file_or_dir`）。
    - `parent_dir` (`Path`): 父目录路径。

- 方法:

  #### `get_args(self, rel_path)`
  - 签名: `get_args(self, rel_path: Path) -> tuple`
  - 说明: 根据相对路径计算要删除的目标绝对路径。
  - 参数: `rel_path` (`Path`): 文件的相对路径。
  - 返回值: 包含目标绝对路径的元组 `(parent_dir / rel_path,)`。

- 关联: 被 `FileDiff.sync_dirs` 使用。

---

### `CopyExecutor`

- 继承: `TaskExecutor` (from `celestialflow`)
- 说明: 复制执行器，根据相对路径将文件从主目录批量复制到次目录。

- 构造函数: `__init__(self, func, main_dir: Path, minor_dir: Path, copy_mode: str)`
  - 参数:
    - `func`: 复制函数（如 `copy_file_or_dir`）。
    - `main_dir` (`Path`): 源目录。
    - `minor_dir` (`Path`): 目标目录。
    - `copy_mode` (`str`): 复制模式标识（用于进度显示）。

- 方法:

  #### `get_args(self, rel_path)`
  - 签名: `get_args(self, rel_path: Path) -> tuple`
  - 说明: 根据相对路径计算源文件和目标文件的绝对路径，并确保目标目录存在。
  - 参数: `rel_path` (`Path`): 文件的相对路径。
  - 返回值: `(source, target)` 元组。

- 关联: 被 `FileDiff.sync_dirs` 使用。

---

### `FileDiff`

- 继承: 无（`@dataclass`）
- 说明: 两个目录的差异比较结果，包含仅存在于单侧的文件和内容不同的文件列表。

- 字段:
  - `left_path` (`Path`): 左侧目录路径。
  - `right_path` (`Path`): 右侧目录路径。
  - `only_in_left` (`list[Path]`): 仅存在于左侧的文件相对路径列表。
  - `only_in_right` (`list[Path]`): 仅存在于右侧的文件相对路径列表。
  - `different_files` (`list[Path]`): 两侧均存在但内容不同的文件相对路径列表。
  - `compare_hash` (`bool`): 是否通过哈希值比较文件内容。
  - `diff_size_left` (`HumanBytes`): 左侧差异文件总大小，默认 `HumanBytes(0)`。
  - `diff_size_right` (`HumanBytes`): 右侧差异文件总大小，默认 `HumanBytes(0)`。
  - `diff_tree` (`FileTree | None`): 差异文件树，默认 `None`。

- 方法:

  #### `is_identical(self)`
  - 签名: `is_identical(self) -> bool`
  - 说明: 判断两个目录是否完全相同（无差异文件）。

  #### `print_diff_tree(self)`
  - 签名: `print_diff_tree(self) -> None`
  - 说明: 以树形结构打印差异文件，并显示两侧目录的差异大小汇总表。若无差异则打印 "No different files found."。

  #### `sync_dirs(self, mode='->')`
  - 签名: `sync_dirs(self, mode: str = '->') -> None`
  - 说明: 根据差异结果同步两个文件夹。
  - 参数:
    - `mode` (`str`): 同步模式:
      - `'->'`: 以左侧为主，删除右侧独有文件，复制左侧独有和差异文件到右侧。
      - `'<-'`: 以右侧为主，反向操作。
      - `'<->'`: 双向同步，差异文件在文件名中追加哈希后分别复制。
  - 异常: `ValueError` - 无效的模式。

  #### `to_dict(self)`
  - 签名: `to_dict(self) -> dict`
  - 说明: 将差异结果转换为可序列化的字典。

- 用法示例:

```python
from celestialvault.instances.inst_file.file_diff import compare_trees
from celestialvault.instances.inst_file.file_tree import FileTree

tree1 = FileTree.build_from_path("/path/to/dir1")
tree2 = FileTree.build_from_path("/path/to/dir2")

diff = compare_trees(tree1, tree2, compare_hash=True)

if not diff.is_identical():
    diff.print_diff_tree()
    # 以 dir1 为主同步到 dir2
    diff.sync_dirs(mode="->")
```

- 关联: 使用 `file_node.BaseNode`/`DirNode` 构建差异树；使用 `file_tree.FileTree` 存储差异树；使用 `inst_units.HumanBytes`/`HumanTimestamp` 表示大小和时间。

## 顶层函数

### `compare_trees(tree1, tree2, compare_hash=False)`
- 签名: `compare_trees(tree1: FileTree, tree2: FileTree, compare_hash: bool = False) -> FileDiff`
- 说明: 将两棵文件树对比，返回包含差异信息的 `FileDiff` 对象。递归比较两棵树的节点：
  - 左独有节点加入 `only_in_left`
  - 右独有节点加入 `only_in_right`
  - 双方均为文件但大小或哈希不同时加入 `different_files`
  - 双方均为目录时递归比较
  - 一方文件一方目录时分别加入各自的独有列表
- 参数:
  - `tree1` (`FileTree`): 第一棵文件树。
  - `tree2` (`FileTree`): 第二棵文件树。
  - `compare_hash` (`bool`): 是否通过哈希值比较文件内容，默认 `False`（仅比较大小）。
- 返回值: 包含两棵树差异信息的 `FileDiff` 对象。
