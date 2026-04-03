# instances/inst_error.py

## 源文件
- `src/celestialvault/instances/inst_error.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- 无

## 模块常量
- 无

## 顶层函数
- 无

## 类
### `DownloadError`
- 继承: `Exception`
- 说明: Raised when the download process fails.
- 方法: 无

### `FFmpegError`
- 继承: `DownloadError`
- 说明: Raised when FFmpeg execution fails.
- 方法:
  - `def __init__(self, message, stderr = None)`
