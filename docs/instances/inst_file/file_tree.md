# `celestialvault.instances.inst_file.file_tree`

> 📅 最后更新日期: 2026/06/28

## 源文件 - `src/celestialvault/instances/inst_file/file_tree.py`

## 模块说明

提供文件树类 `FileTree`，支持从文件系统路径递归构建文件树、序列化/反序列化为 JSON、基于 mtime 的增量更新和格式化打印。

## 导入依赖

- `json` - JSON 序列化
- `pathlib.Path` - 路径操作
- `typing.Any` - 类型注解
- `wcwidth.wcswidth` - 宽字符宽度计算
- `celestialvault.constants.FILE_ICONS` - 文件图标映射
- `celestialvault.instances.inst_units.HumanBytes` - 人类可读字节大小
- `celestialvault.instances.inst_units.HumanTimestamp` - 人类可读时间戳
- `celestialvault.tools.FileOperations.get_dir_mtime` - 获取目录修改时间
- `celestialvault.tools.FileOperations.get_dir_size` - 获取目录大小
- `celestialvault.tools.FileOperations.get_file_mtime` - 获取文件修改时间
- `celestialvault.tools.FileOperations.get_file_size` - 获取文件大小
- `celestialvault.instances.inst_file.file_node.BaseNode` - 基础节点
- `celestialvault.instances.inst_file.file_node.FileNode` - 文件节点
- `celestialvault.instances.inst_file.file_node.DirNode` - 目录节点
- `celestialvault.instances.inst_file.file_node.ExcludedDirsNode` - 被排除目录汇总节点
- `celestialvault.instances.inst_file.file_node.ExcludedFilesNode` - 被排除文件汇总节点

## 类

### `FileTree`

- 继承: 无
- 说明: 文件树，包含根目录节点和路径。支持从文件系统构建、JSON 序列化/反序列化、增量更新和格式化打印。

- 构造函数: `__init__(self, root: DirNode, path: Path)`
  - 参数:
    - `root` (`DirNode`): 根目录节点。
    - `path` (`Path`): 根目录路径。

- 类属性:
  - `_CACHE_DIR` (`str`): 缓存目录名，值为 `".file_tree"`。

- 方法:

  #### `build_from_path(cls, root_path, exclude_names=None, exclude_exts=None)` (类方法)
  - 签名: `build_from_path(cls, root_path: Path | str, exclude_names: set[str] | None = None, exclude_exts: set[str] | None = None) -> FileTree`
  - 说明: 从路径递归构建文件树。构建过程中会跳过 `exclude_names` 中的目录名和 `exclude_exts` 中的文件扩展名（扩展名比较时忽略大小写），并以汇总节点形式记录被排除项。
  - 参数:
    - `root_path` (`Path | str`): 根目录路径。
    - `exclude_names` (`set[str] | None`): 要排除的目录名称集合。
    - `exclude_exts` (`set[str] | None`): 要排除的文件扩展名集合。
  - 返回值: 构建的 `FileTree` 对象。
  - 异常: `ValueError` - 路径不是目录时抛出。

  #### `save(self)`
  - 签名: `save(self) -> Path`
  - 说明: 将文件树序列化为 JSON 并保存到 `<root>/.file_tree/<root_name>.json`。JSON 中额外存储 `root_mtime` 供 `update` 时比对。
  - 返回值: 写入的 JSON 文件路径。

  #### `load(cls, root_path)` (类方法)
  - 签名: `load(cls, root_path: str | Path) -> FileTree`
  - 说明: 从 `<root_path>/.file_tree/<dir_name>.json` 还原文件树。
  - 参数:
    - `root_path` (`str | Path`): 根目录路径。
  - 返回值: 还原的 `FileTree` 对象。
  - 异常: `FileNotFoundError` - 缓存文件不存在时抛出。

  #### `update(self)`
  - 签名: `update(self) -> bool`
  - 说明: 检查目录 mtime 是否变化，若变化则重新构建并保存。比较方式：重新计算 root 的 mtime 与缓存 JSON 中记录的 `root_mtime` 比对。
  - 返回值: `True` 表示已更新，`False` 表示无变化。

  #### `print_tree(self, max_depth=3, show_files=True)`
  - 签名: `print_tree(self, max_depth: int = 3, show_files: bool = True) -> None`
  - 说明: 递归打印整棵文件树，目录在前、文件在后。超过最大深度的非空目录显示为折叠状态；`show_files=False` 时只打印目录结构。
  - 参数:
    - `max_depth` (`int`): 最大打印深度，默认 `3`。
    - `show_files` (`bool`): 是否显示文件节点，默认 `True`。

  #### `_node_to_dict(self, node)` (内部方法)
  - 说明: 将节点递归转换为可 JSON 序列化的字典。

  #### `_dict_to_node(d)` (静态方法)
  - 说明: 将字典递归还原为节点。

  #### `_cache_path(self)` (内部方法)
  - 说明: 返回缓存 JSON 的路径 `<root>/.file_tree/<root_name>.json`。

- 用法示例:

```python
from pathlib import Path
from celestialvault.instances.inst_file.file_tree import FileTree

# 从路径构建文件树，排除 .git 和 node_modules，以及 .pyc/.log 文件
tree = FileTree.build_from_path(
    Path("/path/to/directory"),
    exclude_names={".git", "node_modules"},
    exclude_exts={".pyc", ".log"},
)

# 打印文件树（最大深度 4，显示文件）
tree.print_tree(max_depth=4, show_files=True)

# 保存到 JSON 缓存
tree.save()

# 从缓存加载
tree = FileTree.load("/path/to/directory")

# 增量更新（目录变化时重建）
updated = tree.update()
if updated:
    print("文件树已更新")

# 仅打印目录结构
tree.print_tree(show_files=False)
```

- 关联: 使用 `file_node.FileNode`、`file_node.DirNode`、`file_node.ExcludedDirsNode` 和 `file_node.ExcludedFilesNode` 构建节点树；被 `file_diff.compare_trees` 用于目录对比；使用 `inst_units.HumanBytes` 和 `HumanTimestamp` 表示文件属性。
