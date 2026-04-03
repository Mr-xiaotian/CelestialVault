# instances/inst_sub.py

## 源文件
- `src/celestialvault/instances/inst_sub.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- `import regex as re`
- `from html import unescape`
- `from pathlib import Path`
- `from urllib.parse import unquote`
- `from ..tools.FileOperations import handle_dir_files`
- `from ..tools.TextTools import pro_slash, safe_open_txt`

## 模块常量
- 无

## 顶层函数
- 无

## 类
### `Suber`
- 继承: `object`
- 说明: 无模块级文档字符串。
- 方法:
  - `def __init__(self)`
  - `def clear_book_dir(self, dir_path: Path | str, execution_mode: str = 'thread')`
  - `def clear_book(self, book_path: Path, new_path: Path)`
  - `def clear_text(self, text)`
  - `def sub_name(self, name: str, max_len: int = 100) -> str`
