# `celestialvault.instances.inst_sub`

## 源文件 - `src/celestialvault/instances/inst_sub.py`

## 模块说明

提供文本清理和文件名净化工具类 `Suber`，包含多种预定义的正则替换规则，用于清理特殊字符、处理换行符、替换 HTML/Markdown 标签等。

## 导入依赖

- `regex` (as `re`) - 正则表达式（使用 `regex` 库代替标准 `re`，支持更高级的正则语法）
- `html.unescape` - HTML 实体解码
- `pathlib.Path` - 路径操作
- `urllib.parse.unquote` - URL 解码
- `celestialvault.tools.FileOperations.handle_dir_files` - 批量文件处理
- `celestialvault.tools.TextTools.pro_slash` - 斜杠处理
- `celestialvault.tools.TextTools.safe_open_txt` - 安全打开文本文件（自动检测编码）

## 类

### `Suber`

- 继承: 无
- 说明: 文本清理和文件名净化工具。内置多组正则替换规则，可对文本执行特殊字符移除、换行符规范化、HTML/Markdown 标签处理等操作，也可清理文件名中的非法字符。

- 构造函数: `__init__(self)` - 无参数。
  - 初始化以下替换规则列表:
    - `self.both_check_chars` (`str`): 需要前后检查的特殊字符模式。
    - `self.lookahead_only_chars` (`str`): 仅需前向检查的字符模式。
    - `self.lookbehind_only_chars` (`str`): 仅需后向检查的字符模式。
    - `self.regex_remove_unwanted_newlines` (`list`): 基于前后环视移除不需要的换行符。
    - `self.special_character_removal` (`list`): 移除制表符、回车符、换页符、全角空格等特殊字符。
    - `self.newline_handling` (`list`): 将单独换行符补为双换行，限制连续换行不超过两个。
    - `self.html_md_handling` (`list`): 将 `<br>`、`<p>`、`<code>` 等 HTML 标签替换为 Markdown 格式。
    - `self.sub_text_list` (`list`): 文本替换规则合集（`special_character_removal` + `regex_remove_unwanted_newlines` + `newline_handling`）。
    - `self.sub_name_list` (`list`): 文件名替换规则列表（替换冒号、斜杠、星号等非法字符）。

- 方法:

  #### `clear_book_dir(self, dir_path, execution_mode='thread')`
  - 签名: `clear_book_dir(self, dir_path: Path | str, execution_mode: str = 'thread') -> dict`
  - 说明: 批量清理文件夹中所有 txt 文件的文本内容。
  - 参数:
    - `dir_path` (`Path | str`): 目标文件夹路径。
    - `execution_mode` (`str`): 执行模式，如 `'thread'` 或 `'serial'`。
  - 返回值: 批量处理的结果。

  #### `clear_book(self, book_path, new_path)`
  - 签名: `clear_book(self, book_path: Path, new_path: Path) -> None`
  - 说明: 读取并清理单个 txt 文件的文本内容，保存到新路径。使用 `safe_open_txt` 自动检测编码读取文件。
  - 参数:
    - `book_path` (`Path`): 原始文件路径。
    - `new_path` (`Path`): 清理后保存的目标路径。
  - 异常: `ValueError` - 无法使用检测到的编码解码文件时抛出。

  #### `clear_text(self, text)`
  - 签名: `clear_text(self, text) -> str`
  - 说明: 对文本执行所有预定义的替换规则（`sub_text_list`），并先进行斜杠处理和 HTML/URL 解码，返回清理后的文本。
  - 参数:
    - `text` (`str`): 待清理的原始文本。
  - 返回值: 清理后的文本字符串（已 strip）。

  #### `sub_name(self, name, max_len=100)`
  - 签名: `sub_name(self, name: str, max_len: int = 100) -> str`
  - 说明: 清理文件名中的非法字符，并在超长时进行截断。超过 `max_len` 时取前 2/4 和后 1/4 拼接，中间插入 `(省略)`。
  - 参数:
    - `name` (`str`): 原始文件名。
    - `max_len` (`int`): 文件名最大长度限制，默认 `100`。
  - 返回值: 清理后的文件名。

- 用法示例:

```python
from celestialvault.instances.inst_sub import Suber

suber = Suber()

# 清理文本
raw_text = "Hello\t\tWorld\n\n\n\n这是一段<br>测试文本"
clean_text = suber.clear_text(raw_text)
print(clean_text)

# 清理文件名
raw_name = '文件名：包含/非法*字符?.txt'
safe_name = suber.sub_name(raw_name)
print(safe_name)  # "文件名_包含_非法_字符_txt"

# 批量清理文件夹中的所有 txt 文件
suber.clear_book_dir("./books", execution_mode="thread")
```

- 关联: 依赖 `celestialvault.tools.TextTools` 的 `pro_slash` 和 `safe_open_txt` 函数；依赖 `celestialvault.tools.FileOperations` 的 `handle_dir_files` 批量文件处理函数。
