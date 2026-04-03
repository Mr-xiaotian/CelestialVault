# tools/VideoProcessing.py

## 源文件
- `src/celestialvault/tools/VideoProcessing.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- `import re`
- `import subprocess`
- `from collections import defaultdict`
- `from pathlib import Path`
- `import ffmpeg`
- `from moviepy.editor import CompositeVideoClip, TextClip, VideoFileClip, clips_array`
- `from celestialflow import TaskExecutor`

## 模块常量
- 无

## 顶层函数
### `compress_video`
- 签名: `def compress_video(old_video_path: Path | str, new_video_path: Path | str)`
- 说明: 使用ffmpeg压缩视频

:param old_video_path: 原始视频文件路径
:param new_video_path: 压缩后视频文件路径

### `join_and_label_videos`
- 签名: `def join_and_label_videos(video_path1: Path | str, video_path2: Path | str, output_path: str, duration: int = 10, label1: str = None, label2: str = None)`
- 说明: 将两个视频拼接，并在左上角添加文本标签

:param video_path1: 第一个视频文件路径
:param video_path2: 第二个视频文件路径
:param output_path: 输出视频文件路径
:param duration: 视频时长（秒）
:param label1: 第一个视频的标签（默认文件名）
:param label2: 第二个视频的标签（默认文件名）

### `transfer_gif_to_video`
- 签名: `def transfer_gif_to_video(gif_path, output_path)`
- 说明: 将GIF文件转换为MP4视频文件

:param gif_path: GIF文件路径
:param  output_path: 输出MP4文件路径

### `transfer_gif_dir`
- 签名: `def transfer_gif_dir(dir_path: str | Path) -> list[tuple[Path, Exception]]`
- 说明: 将文件夹中的所有GIF文件转换为MP4视频文件

:param dir_path: 文件夹路径
:return: 转换结果列表，每个元素是一个元组，包含输出文件路径和可能的异常

### `rotate_video`
- 签名: `def rotate_video(video_path: str | Path, output_path, angle: int) -> Path`
- 说明: 旋转视频文件。

:param video_path: 视频路径（str 或 Path 对象）
:param output_path: 输出文件路径（str 或 Path 对象）
:param angle: 旋转角度（仅支持 0, 90, 180, 270）
:return: 输出文件路径（Path 对象）

### `rotate_video_dir`
- 签名: `def rotate_video_dir(dir_path: str | Path, angle: int) -> list[tuple[Path, Exception]]`
- 说明: 旋转文件夹中的所有视频文件。

:param dir_path: 文件夹路径（str 或 Path 对象）
:param angle: 旋转角度（仅支持 0, 90, 180, 270）
:return: 转换结果列表，每个元素是一个元组，包含输出文件路径和可能的异常

### `get_video_codec`
- 签名: `def get_video_codec(video_path: Path) -> str`
- 说明: 获取视频文件的编码格式。

:param video_path: 视频文件路径
:return: 编码格式

### `get_videos_codec`
- 签名: `def get_videos_codec(dir_path: Path, exclude_codecs: list[str] = ['h264']) -> dict[str, list[Path]]`
- 说明: 获取文件夹中所有视频文件的编码格式。

:param dir_path: 文件夹路径
:param exclude_codecs: 需要排除的编码格式列表
:return: 编码格式字典

### `get_video_info`
- 签名: `def get_video_info(video_path: str)`
- 说明: 获取视频的分辨率和显示宽高比（容器宽高比）。

:param video_path: 视频文件的路径。
:return: 一个字典，包含分辨率（width, height）和显示宽高比（DAR）。

### `is_container_ratio_matching_resolution`
- 签名: `def is_container_ratio_matching_resolution(video_path)`
- 说明: 检查视频容器的宽高比是否与分辨率比例一致。

:param video_info: 包含视频信息的字典，需包含 width, height, display_aspect_ratio。
:return: 布尔值，表示是否一致。

### `set_container_ratio_to_resolution`
- 签名: `def set_container_ratio_to_resolution(video_path, output_path)`
- 说明: 修改视频容器宽高比，使其与分辨率比例一致。

:param video_path: 输入视频文件路径。
:param output_path: 输出视频文件路径。

## 类
### `GetCodecExecutor`
- 继承: `TaskExecutor`
- 说明: 视频编码格式扫描执行器，批量获取视频编码并按编码类型分组。
- 方法:
  - `def process_result_dict(self)`
