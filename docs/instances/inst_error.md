# `celestialvault.instances.inst_error`

> 📅 最后更新日期: 2026/04/22

## 源文件 - `src/celestialvault/instances/inst_error.py`

## 模块说明

定义项目中使用的自定义异常类，主要用于下载和 FFmpeg 相关的错误处理。

## 导入依赖

无外部依赖，仅使用 Python 内置 `Exception`。

## 类

### `DownloadError`

- 继承: `Exception`
- 说明: 下载过程失败时抛出的异常。
- 构造函数: 使用默认的 `Exception.__init__`。

- 用法示例:

```python
from celestialvault.instances.inst_error import DownloadError

try:
    raise DownloadError("文件下载失败: 404 Not Found")
except DownloadError as e:
    print(f"下载错误: {e}")
```

- 关联: 被 `FFmpegError` 继承；被 `inst_save.Saver.download_m3u8` 间接使用。

---

### `FFmpegError`

- 继承: `DownloadError`
- 说明: FFmpeg 执行失败时抛出的异常，附带 stderr 信息。

- 构造函数: `__init__(self, message, stderr=None)`
  - 参数:
    - `message` (`str`): 错误消息。
    - `stderr` (`str | None`): FFmpeg 的标准错误输出，默认 `None`。
  - 属性:
    - `self.stderr`: 存储 FFmpeg 的 stderr 输出。

- 用法示例:

```python
from celestialvault.instances.inst_error import FFmpegError

try:
    raise FFmpegError("FFmpeg 转码失败", stderr="Error: invalid codec")
except FFmpegError as e:
    print(f"错误: {e}, stderr: {e.stderr}")
```

- 关联: 被 `inst_save.Saver.download_m3u8` 使用，在 FFmpeg 命令执行失败时抛出。
