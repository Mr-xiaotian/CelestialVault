# tools/AudioProcessing.py

## 源文件
- `src/celestialvault/tools/AudioProcessing.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- `from pathlib import Path`
- `from pydub import AudioSegment`

## 模块常量
- 无

## 顶层函数
### `convert_mp3_to_wav`
- 签名: `def convert_mp3_to_wav(mp3_path: Path, wav_path: Path)`
- 说明: 将指定的 mp3 文件转换为 wav 文件

:param mp3_path: mp3 文件的路径
:param wav_path: wav 文件的路径

### `convert_mp3_dir`
- 签名: `def convert_mp3_dir(dir_path: Path) -> dict[tuple[str, str], list[Path]]`
- 说明: 将指定目录下的所有 mp3 文件转换为 wav 文件

:param dir_path: mp3 文件所在的目录

## 类
- 无
