# `celestialvault.instances.inst_file.file_util`

## 源文件 - `src/celestialvault/instances/inst_file/file_util.py`

## 模块说明

提供文件树节点的字符串格式化工具函数。

## 导入依赖

- `celestialvault.tools.FileOperations.align_width` - 宽度对齐工具

## 顶层函数

### `to_string(indent, icon, prefix, name, suffix, max_name_len=0)`
- 签名: `to_string(indent: str, icon: str, prefix: str, name: str, suffix: str, max_name_len: int = 0) -> str`
- 说明: 将节点格式化为带缩进、图标、前缀和后缀的字符串表示。输出格式: `"{indent}{icon} {prefix}{aligned_name}\t{suffix}"`。
- 参数:
  - `indent` (`str`): 缩进字符串（如 `"    "` 表示一级缩进）。
  - `icon` (`str`): 节点图标字符串（如 `"📁"`、`"📄"`）。
  - `prefix` (`str`): 节点名称前的前缀。
  - `name` (`str`): 节点名称字符串。
  - `suffix` (`str`): 节点名称后的后缀（如大小信息 `"(1KB)"`）。
  - `max_name_len` (`int`): 最大名称长度，用于对齐，默认 `0`。
- 返回值: 格式化后的节点字符串。

- 用法示例:

```python
from celestialvault.instances.inst_file.file_util import to_string

line = to_string(
    indent="    ",
    icon="📄",
    prefix="",
    name="readme.txt",
    suffix="(1KB)",
    max_name_len=20,
)
print(line)  # "    📄 readme.txt          (1KB)"
```

- 关联: 被 `file_node.BaseNode.print` 调用进行格式化输出；依赖 `celestialvault.tools.FileOperations.align_width` 进行宽度对齐。
