# `celestialvault.instances.inst_file.file_tree`

## 源文件 - `src/celestialvault/instances/inst_file/file_tree.py`

## 模块说明

提供文件树类 `FileTree`，支持从文件系统路径构建文件树、序列化/反序列化为 JSON、增量更新和格式化打印。

## 导入依赖

- `json` - JSON 序列化
- `pathlib.Path` - 路径操作
- `wcwidth.wcswidth` - 宽字符宽度计算
- `celestialflow.TaskExecutor` - 多线程文件扫描
- `celestialvault.constants.FILE_ICONS` - 文件图标映射
- `celestialvault.instances.inst_units.HumanBytes` - 人类可读字节大小
- `celestialvault.instances.inst_units.HumanTimestamp` - 人类可读时间戳
- `celestialvault.tools.FileOperations.get_file_info` - 获取文件信息
- `celestialvault.tools.FileOperations.get_dir_mtime` - 获取目录修改时间
- `celestialvault.instances.inst_file.file_node.BaseNode` - 基础节点
- `celestialvault.instances.inst_file.file_node.FileNode` - 文件节点
- `celestialvault.instances.inst_file.file_node.DirNode` - 目录节点

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

  #### `build_from_path(cls, root_path)` (类方法)
  - 签名: `build_from_path(cls, root_path: Path) -> FileTree`
  - 说明: 从路径构建文件树。使用多线程（4 workers）扫描所有文件信息，然后递归构建节点树。
  - 参数:
    - `root_path` (`Path`): 根目录路径。
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

  #### `print_tree(self, exclude_names=None, exclude_exts=None, max_depth=3)`
  - 签名: `print_tree(self, exclude_names=None, exclude_exts=None, max_depth=3) -> None`
  - 说明: 递归打印整棵文件树，目录在前、文件在后。支持排除指定目录名和文件扩展名，超过最大深度的目录显示为折叠状态。
  - 参数:
    - `exclude_names` (`set | list | None`): 要排除的目录名称集合。
    - `exclude_exts` (`set | list | None`): 要排除的文件扩展名集合。
    - `max_depth` (`int`): 最大打印深度，默认 `3`。

  #### `_node_to_dict(self, node)` (内部方法)
  - 说明: 将节点递归转换为可 JSON 序列化的字典。

  #### `_dict_to_node(d)` (静态方法)
  - 说明: 将字典递归还原为节点。

- 用法示例:

```python
from pathlib import Path
from celestialvault.instances.inst_file.file_tree import FileTree

# 从路径构建文件树
tree = FileTree.build_from_path(Path("/path/to/directory"))

# 打印文件树（排除 .git 和 node_modules，最大深度 4）
tree.print_tree(exclude_names=[".git", "node_modules"], max_depth=4)

# 保存到 JSON 缓存
tree.save()

# 从缓存加载
tree = FileTree.load("/path/to/directory")

# 增量更新（目录变化时重建）
updated = tree.update()
if updated:
    print("文件树已更新")

# 排除特定扩展名
tree.print_tree(exclude_exts=[".pyc", ".log"])
```

- 关联: 使用 `file_node.FileNode` 和 `file_node.DirNode` 构建节点树；被 `file_diff.compare_trees` 用于目录对比；使用 `inst_units.HumanBytes` 和 `HumanTimestamp` 表示文件属性；使用 `celestialflow.TaskExecutor` 多线程扫描文件。
