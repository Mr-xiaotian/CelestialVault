# `celestialvault.tools.VideoProcessing`

## 源文件

[src/celestialvault/tools/VideoProcessing.py](../../src/celestialvault/tools/VideoProcessing.py)

## 模块说明

视频处理工具模块，提供视频压缩、视频拼接标注、GIF 转视频、视频旋转、视频编码格式检测、视频信息获取、容器宽高比校正等功能。

## 导入依赖

```python
import re
import subprocess
from collections import defaultdict
from pathlib import Path

import ffmpeg
from celestialflow import TaskExecutor
```

## 顶层函数

### `compress_video`

- 签名: `def compress_video(old_video_path: Path | str, new_video_path: Path | str)`
- 说明: 使用 ffmpeg 压缩视频（libx264 编码，CRF 22，AAC 音频）
- 参数:
  - `old_video_path` (Path | str): 原始视频文件路径
  - `new_video_path` (Path | str): 压缩后视频文件路径
- 返回值: 无
- 用法示例:
  ```python
  from celestialvault.tools.VideoProcessing import compress_video

  compress_video("input.mp4", "output_compressed.mp4")
  ```
- 关联: `celestialvault.tools.FileOperations.compress_dir`

### `join_and_label_videos`

- 签名: `def join_and_label_videos(video_path1: Path | str, video_path2: Path | str, output_path: str, duration: int = 10, label1: str = None, label2: str = None)`
- 说明: 将两个视频拼接，并在左上角添加文本标签
- 参数:
  - `video_path1` (Path | str): 第一个视频文件路径
  - `video_path2` (Path | str): 第二个视频文件路径
  - `output_path` (str): 输出视频文件路径
  - `duration` (int): 视频时长（秒）
  - `label1` (str): 第一个视频的标签（默认文件名）
  - `label2` (str): 第二个视频的标签（默认文件名）
- 返回值: 无
- 用法示例:
  ```python
  from celestialvault.tools.VideoProcessing import join_and_label_videos

  join_and_label_videos(
      "original.mp4", "compressed.mp4", "comparison.mp4",
      duration=15, label1="Original", label2="Compressed"
  )
  ```
- 关联: 无

### `transfer_gif_to_video`

- 签名: `def transfer_gif_to_video(gif_path, output_path)`
- 说明: 将 GIF 文件转换为 MP4 视频文件
- 参数:
  - `gif_path`: GIF 文件路径
  - `output_path`: 输出 MP4 文件路径
- 返回值: 无
- 用法示例:
  ```python
  from celestialvault.tools.VideoProcessing import transfer_gif_to_video

  transfer_gif_to_video("animation.gif", "animation.mp4")
  ```
- 关联: `transfer_gif_dir`

### `transfer_gif_dir`

- 签名: `def transfer_gif_dir(dir_path: str | Path) -> list[tuple[Path, Exception]]`
- 说明: 将文件夹中的所有 GIF 文件转换为 MP4 视频文件
- 参数:
  - `dir_path` (str | Path): 文件夹路径
- 返回值: 转换结果列表
- 用法示例:
  ```python
  from celestialvault.tools.VideoProcessing import transfer_gif_dir

  errors = transfer_gif_dir("gifs/")
  ```
- 关联: `transfer_gif_to_video`, `celestialvault.tools.FileOperations.handle_dir_files`

### `rotate_video`

- 签名: `def rotate_video(video_path: str | Path, output_path, angle: int) -> Path`
- 说明: 旋转视频文件
- 参数:
  - `video_path` (str | Path): 视频路径
  - `output_path`: 输出文件路径
  - `angle` (int): 旋转角度（仅支持 0, 90, 180, 270）
- 返回值: 输出文件路径（Path 对象）
- 用法示例:
  ```python
  from celestialvault.tools.VideoProcessing import rotate_video

  rotate_video("portrait.mp4", "landscape.mp4", 90)
  ```
- 关联: `rotate_video_dir`

### `rotate_video_dir`

- 签名: `def rotate_video_dir(dir_path: str | Path, angle: int) -> list[tuple[Path, Exception]]`
- 说明: 旋转文件夹中的所有视频文件
- 参数:
  - `dir_path` (str | Path): 文件夹路径
  - `angle` (int): 旋转角度（仅支持 90, 180, 270）
- 返回值: 转换结果列表
- 用法示例:
  ```python
  from celestialvault.tools.VideoProcessing import rotate_video_dir

  errors = rotate_video_dir("videos/", 90)
  ```
- 关联: `rotate_video`, `celestialvault.tools.FileOperations.handle_dir_files`

### `get_video_codec`

- 签名: `def get_video_codec(video_path: Path) -> str`
- 说明: 获取视频文件的编码格式
- 参数:
  - `video_path` (Path): 视频文件路径
- 返回值: 编码格式字符串
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.VideoProcessing import get_video_codec

  codec = get_video_codec(Path("video.mp4"))
  print(codec)  # "h264"
  ```
- 关联: `get_videos_codec`

### `get_videos_codec`

- 签名: `def get_videos_codec(dir_path: Path, exclude_codecs: list[str] = ["h264"]) -> dict[str, list[Path]]`
- 说明: 获取文件夹中所有视频文件的编码格式
- 参数:
  - `dir_path` (Path): 文件夹路径
  - `exclude_codecs` (list[str]): 需要排除的编码格式列表
- 返回值: 编码格式字典，键为编码名，值为文件路径列表
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.VideoProcessing import get_videos_codec

  codecs = get_videos_codec(Path("videos/"), exclude_codecs=["h264"])
  for codec, files in codecs.items():
      print(f"{codec}: {len(files)} 个文件")
  ```
- 关联: `get_video_codec`, `GetCodecExecutor`

### `get_video_info`

- 签名: `def get_video_info(video_path: str)`
- 说明: 获取视频的分辨率和显示宽高比（容器宽高比）
- 参数:
  - `video_path` (str): 视频文件的路径
- 返回值: 一个字典，包含分辨率（width, height）和显示宽高比（DAR）
- 用法示例:
  ```python
  from celestialvault.tools.VideoProcessing import get_video_info

  info = get_video_info("video.mp4")
  print(info)  # {'width': 1920, 'height': 1080, 'display_aspect_ratio': '16:9'}
  ```
- 关联: `is_container_ratio_matching_resolution`, `set_container_ratio_to_resolution`

### `is_container_ratio_matching_resolution`

- 签名: `def is_container_ratio_matching_resolution(video_path)`
- 说明: 检查视频容器的宽高比是否与分辨率比例一致
- 参数:
  - `video_path`: 视频文件路径
- 返回值: 布尔值，表示是否一致
- 用法示例:
  ```python
  from celestialvault.tools.VideoProcessing import is_container_ratio_matching_resolution

  matches = is_container_ratio_matching_resolution("video.mp4")
  print(f"宽高比匹配: {matches}")
  ```
- 关联: `get_video_info`, `set_container_ratio_to_resolution`

### `set_container_ratio_to_resolution`

- 签名: `def set_container_ratio_to_resolution(video_path, output_path)`
- 说明: 修改视频容器宽高比，使其与分辨率比例一致
- 参数:
  - `video_path`: 输入视频文件路径
  - `output_path`: 输出视频文件路径
- 返回值: 无
- 用法示例:
  ```python
  from celestialvault.tools.VideoProcessing import set_container_ratio_to_resolution

  set_container_ratio_to_resolution("input.mp4", "fixed.mp4")
  ```
- 关联: `get_video_info`, `is_container_ratio_matching_resolution`

## 类

### `GetCodecExecutor`

- 继承: `TaskExecutor` (from celestialflow)
- 说明: 视频编码格式扫描执行器，批量获取视频编码并按编码类型分组
- 关联: `get_videos_codec`
