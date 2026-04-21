# `celestialvault.tools.AudioProcessing`

## 源文件

[src/celestialvault/tools/AudioProcessing.py](../../src/celestialvault/tools/AudioProcessing.py)

## 模块说明

音频处理工具模块，提供 MP3 到 WAV 的格式转换功能，支持单文件转换和批量目录转换。

## 导入依赖

```python
from pathlib import Path
from pydub import AudioSegment
```

## 顶层函数

### `convert_mp3_to_wav`

- 签名: `def convert_mp3_to_wav(mp3_path: Path, wav_path: Path)`
- 说明: 将指定的 mp3 文件转换为 wav 文件
- 参数:
  - `mp3_path` (Path): mp3 文件的路径
  - `wav_path` (Path): wav 文件的路径
- 返回值: 无
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.AudioProcessing import convert_mp3_to_wav

  convert_mp3_to_wav(Path("audio/song.mp3"), Path("output/song.wav"))
  ```
- 关联: `convert_mp3_dir`

### `convert_mp3_dir`

- 签名: `def convert_mp3_dir(dir_path: Path) -> dict[tuple[str, str], list[Path]]`
- 说明: 将指定目录下的所有 mp3 文件转换为 wav 文件
- 参数:
  - `dir_path` (Path): mp3 文件所在的目录
- 返回值: 处理结果，包含成功和失败的文件路径信息
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.AudioProcessing import convert_mp3_dir

  errors = convert_mp3_dir(Path("audio/mp3_files"))
  if errors:
      print("转换失败的文件:", errors)
  ```
- 关联: `convert_mp3_to_wav`, `celestialvault.tools.FileOperations.handle_dir_files`
