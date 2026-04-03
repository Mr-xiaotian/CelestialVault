# instances/inst_save.py

## 源文件
- `src/celestialvault/instances/inst_save.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- `import json`
- `import pickle`
- `import subprocess`
- `from pathlib import Path`
- `import pandas as pd`
- `from celestialflow import TaskChain, TaskStage`
- `from .inst_error import FFmpegError`
- `from .inst_fetch import Fetcher`

## 模块常量
- 无

## 顶层函数
- 无

## 类
### `FetchStage`
- 继承: `TaskStage`
- 说明: 抓取阶段，从 URL 获取内容并将结果与文件名、后缀组合传递给下一阶段。
- 方法:
  - `def get_args(self, task: object)`
  - `def process_result(self, task, result)`

### `SaveStage`
- 继承: `TaskStage`
- 说明: 保存阶段，将上一阶段传入的内容保存到文件。
- 方法: 无

### `Saver`
- 继承: `object`
- 说明: 文件保存器，支持文本、二进制、DataFrame、JSON、Pickle 等多种格式的保存和下载。
- 方法:
  - `def __init__(self, base_path = '.', overwrite = False)`
  - `def set_base_path(self, base_path)`
  - `def set_add_path(self, add_path)`
  - `def get_path(self, file_name, file_suffix)`
  - `def can_overwrite(self, path)`
  - `def save_text(self, text, file_name, encoding = 'utf-8', file_suffix = None)`
  - `def add_text(self, text, file_name, encoding = 'utf-8', file_suffix = None)`
  - `def save_content(self, content, file_name, file_suffix = None)`
  - `def save_dataframe(self, dataframe: pd.DataFrame, file_name: str, file_suffix = None)`
  - `def save_pickle(self, obj, file_name, file_suffix = None)`
  - `def save_json(self, data, file_name, file_suffix = None, encoding = None)`
  - `def download_url(self, url, file_name, file_suffix = None)`
  - `def download_urls(self, task_list: list[tuple[str, str, str]], chain_mode = 'serial', show_progress = False)`
  - `async def download_urls_async(self, task_list: list[tuple[str, str, str]])`
  - `def download_m3u8(self, m3u8_url, file_name, file_suffix = None, timeout = 3600)`
