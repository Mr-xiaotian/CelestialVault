# `celestialvault.instances.inst_save`

> 📅 最后更新日期: 2026/04/17

## 源文件 - `src/celestialvault/instances/inst_save.py`

## 模块说明

提供文件保存和下载功能，包含任务链阶段类 `FetchStage`、`SaveStage` 和核心保存器类 `Saver`。`Saver` 支持文本、二进制、图像、DataFrame、JSON、Pickle 等多种格式的保存和从 URL 下载。

## 导入依赖

- `io` - 字符串流
- `json` - JSON 序列化
- `pickle` - 对象序列化
- `subprocess` - 外部命令执行（ffmpeg）
- `pathlib.Path` - 路径操作
- `pandas` - DataFrame 操作
- `celestialflow.TaskChain` - 任务链
- `celestialflow.TaskStage` - 任务阶段
- `celestialvault.instances.inst_error.FFmpegError` - FFmpeg 错误
- `celestialvault.instances.inst_fetch.Fetcher` - HTTP 请求
- `celestialvault.tools.ImageProcessing.binary_to_img` - 二进制转图像
- `celestialvault.tools.ImageProcessing.convert_img_format` - 图像格式转换

## 类

### `FetchStage`

- 继承: `TaskStage` (from `celestialflow`)
- 说明: 抓取阶段，从 URL 获取内容并将结果与文件名、后缀组合传递给下一阶段。

- 方法:

  #### `get_args(self, task)`
  - 签名: `get_args(self, task: object) -> tuple`
  - 说明: 从任务元组中提取 URL 作为抓取参数。
  - 参数: `task` - `(URL, 文件名, 文件后缀)` 元组。
  - 返回值: 仅包含 URL 的元组 `(task[0],)`。

  #### `process_result(self, task, result)`
  - 签名: `process_result(self, task, result) -> tuple`
  - 说明: 将抓取结果与任务中的文件名和后缀组合为下一阶段的输入。
  - 返回值: `(响应内容, 文件名, 文件后缀)` 元组。

- 关联: 被 `Saver.download_urls` 使用。

---

### `SaveStage`

- 继承: `TaskStage` (from `celestialflow`)
- 说明: 保存阶段，将上一阶段传入的内容保存到文件。无额外方法，直接使用 `TaskStage` 的默认行为。

- 关联: 被 `Saver.download_urls` 使用。

---

### `Saver`

- 继承: `object`
- 说明: 文件保存器，支持文本、二进制、DataFrame、JSON、Pickle 等多种格式的保存和下载。支持覆盖保护和路径自动创建。

- 构造函数: `__init__(self, base_path='.', overwrite=False)`
  - 参数:
    - `base_path` (`str`): 文件保存的基础路径，默认 `'.'`。
    - `overwrite` (`bool`): 是否允许覆盖已存在文件，默认 `False`。

- 方法:

  #### `set_base_path(self, base_path)`
  - 签名: `set_base_path(self, base_path) -> None`
  - 说明: 设置文件保存的基础路径。

  #### `set_add_path(self, add_path)`
  - 签名: `set_add_path(self, add_path) -> None`
  - 说明: 设置附加子路径，与基础路径拼接形成最终保存目录。

  #### `get_path(self, file_name, file_suffix)`
  - 签名: `get_path(self, file_name, file_suffix) -> Path`
  - 说明: 根据基础路径、附加路径、文件名和后缀生成完整文件路径，并确保目录存在。
  - 参数:
    - `file_name`: 文件名。
    - `file_suffix`: 文件后缀（如 `'.txt'`）；为 `None` 则不添加后缀。
  - 返回值: 完整的文件路径。

  #### `_get_writable_path(self, file_name, file_suffix)`
  - 签名: `_get_writable_path(self, file_name, file_suffix) -> tuple[Path, bool]`
  - 说明: 检查是否允许写入指定路径。
  - 返回值: `(路径, 是否可写)` 元组。若禁止覆盖且文件已存在则返回 `(path, False)`。

  #### 核心方法（不执行覆盖检查）

  | 方法 | 签名 | 说明 |
  |------|------|------|
  | `_text_core` | `_text_core(self, text, file_name, encoding='utf-8', file_suffix=None) -> Path` | 将文本写入文件 |
  | `_content_core` | `_content_core(self, content, file_name, file_suffix=None) -> Path` | 将二进制内容写入文件 |
  | `_image_core` | `_image_core(self, image, file_name, file_suffix=None) -> Path` | 将图像保存到文件（自动格式转换） |
  | `_dataframe_core` | `_dataframe_core(self, dataframe: pd.DataFrame, file_name: str, file_suffix=None) -> Path` | 将 DataFrame 写入 CSV |
  | `_pickle_core` | `_pickle_core(self, obj, file_name, file_suffix=None) -> Path` | 将对象序列化到文件 |
  | `_json_core` | `_json_core(self, data, file_name, file_suffix=None, encoding=None) -> Path` | 将数据写入 JSON 文件 |

  #### 保存方法（带覆盖检查）

  | 方法 | 签名 | 说明 |
  |------|------|------|
  | `save_text` | `save_text(self, text, file_name, encoding='utf-8', file_suffix=None) -> Path` | 将文本内容保存到文件 |
  | `add_text` | `add_text(self, text, file_name, encoding='utf-8', file_suffix=None) -> Path` | 将文本内容追加到文件末尾 |
  | `save_content` | `save_content(self, content, file_name, file_suffix=None) -> Path` | 将二进制内容保存到文件 |
  | `save_image` | `save_image(self, image, file_name, file_suffix=None) -> Path` | 将图像保存为文件 |
  | `save_dataframe` | `save_dataframe(self, dataframe, file_name, file_suffix=None) -> Path` | 将 DataFrame 保存为 CSV 文件 |
  | `save_pickle` | `save_pickle(self, obj, file_name, file_suffix=None) -> Path` | 将 Python 对象序列化为 pickle 文件 |
  | `save_json` | `save_json(self, data, file_name, file_suffix=None, encoding=None) -> Path` | 将数据保存为格式化的 JSON 文件 |

  #### `delete_file(self, file_name, file_suffix=None)`
  - 签名: `delete_file(self, file_name, file_suffix=None) -> tuple[Path, bool]`
  - 说明: 删除指定文件。
  - 返回值: `(文件路径, 是否成功删除)` 元组。

  #### 下载方法

  | 方法 | 签名 | 说明 |
  |------|------|------|
  | `download_text` | `download_text(self, url, file_name, encoding='utf-8', file_suffix=None) -> Path` | 从 URL 下载文本并保存 |
  | `download_content` | `download_content(self, url, file_name, file_suffix=None) -> Path` | 从 URL 下载内容并保存 |
  | `download_image` | `download_image(self, url, file_name, file_suffix=None) -> Path` | 从 URL 下载图片并保存（带覆盖检查） |
  | `download_dataframe` | `download_dataframe(self, url, file_name, file_suffix=None, read_kwargs=None) -> Path` | 从 URL 下载表格并解析为 DataFrame 后保存 |
  | `download_pickle` | `download_pickle(self, url, file_name, file_suffix=None) -> Path` | 从 URL 下载 pickle 并反序列化后保存 |
  | `download_json` | `download_json(self, url, file_name, file_suffix=None, encoding=None) -> Path` | 从 URL 下载 JSON 并保存 |

  #### `download_urls(self, task_list, chain_mode='serial', show_progress=False)`
  - 签名: `download_urls(self, task_list: list[tuple[str, str, str]], chain_mode='serial', show_progress=False) -> None`
  - 说明: 批量下载 URL 列表，使用 `TaskChain` 管理 `FetchStage`（thread 模式）和 `SaveStage`（serial 模式）两个阶段。
  - 参数:
    - `task_list`: 每个元组包含 `(URL, 文件名, 文件后缀)`。
    - `chain_mode` (`str`): `'serial'` 或 `'process'`。
    - `show_progress` (`bool`): 是否显示进度。

  #### `download_urls_async(self, task_list)`
  - 签名: `async download_urls_async(self, task_list: list[tuple[str, str, str]]) -> None`
  - 说明: 异步批量下载 URL 列表（尚未实现）。

  #### `download_m3u8(self, m3u8_url, file_name, file_suffix=None, timeout=3600)`
  - 签名: `download_m3u8(self, m3u8_url, file_name, file_suffix=None, timeout=3600) -> Path`
  - 说明: 使用 ffmpeg 下载 m3u8 流媒体并保存为文件。支持覆盖检查。
  - 参数:
    - `m3u8_url` (`str`): m3u8 流媒体的 URL 地址。
    - `file_name` (`str`): 保存的文件名。
    - `file_suffix` (`str | None`): 文件后缀。
    - `timeout` (`int`): 下载超时时间（秒），默认 `3600`。
  - 返回值: 保存的文件路径。
  - 异常: `TimeoutError` - 下载超时；`FFmpegError` - ffmpeg 执行失败。

- 用法示例:

```python
from celestialvault.instances.inst_save import Saver

saver = Saver(base_path="./output", overwrite=False)

# 保存文本
saver.save_text("Hello, World!", "hello", file_suffix=".txt")

# 保存 JSON
saver.save_json({"key": "value"}, "config", file_suffix=".json")

# 从 URL 下载图片
saver.download_image("https://example.com/img.png", "example_img", file_suffix=".png")

# 批量下载
tasks = [
    ("https://example.com/a.jpg", "img_a", ".jpg"),
    ("https://example.com/b.jpg", "img_b", ".jpg"),
]
saver.download_urls(tasks, chain_mode="serial", show_progress=True)

# 下载 m3u8 视频
saver.download_m3u8("https://example.com/stream.m3u8", "video", file_suffix=".mp4")

# 使用附加路径
saver.set_add_path("images/2025")
saver.save_content(b"\x89PNG...", "photo", file_suffix=".png")
```

- 关联: 使用 `inst_fetch.Fetcher` 进行 HTTP 请求；使用 `inst_error.FFmpegError` 处理 ffmpeg 错误；使用 `celestialflow.TaskChain` 和 `TaskStage` 管理批量下载；使用 `celestialvault.tools.ImageProcessing` 进行图像转换。
