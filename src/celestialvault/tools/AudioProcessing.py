from pathlib import Path
from pydub import AudioSegment
from typing import Dict, List, Tuple


def convert_mp3_to_wav(mp3_path: Path, wav_path: Path):
    """
    将指定的 mp3 文件转换为 wav 文件
    
    :param mp3_path: mp3 文件的路径
    :param wav_path: wav 文件的路径
    """
    wav_path.parent.mkdir(parents=True, exist_ok=True)

    # 读取 MP3 并导出为 WAV
    audio = AudioSegment.from_mp3(mp3_path)
    audio.export(
        wav_path,
        format="wav",
        parameters=["-ar", "22050", "-ac", "1", "-acodec", "pcm_s16le"]
    )


def convert_mp3_dir(dir_path: Path) -> Dict[Tuple[str, str], List[Path]]:
    """
    将指定目录下的所有 mp3 文件转换为 wav 文件

    :param dir_path: mp3 文件所在的目录
    """
    def rename_mp4(file_path: Path) -> Path:
        new_name = f"{file_path.stem}.wav"
        return file_path.with_name(new_name)

    from .FileOperations import handle_dir_files

    rules = {
        ".mp3": (
            convert_mp3_to_wav,
            rename_mp4,
            {},
        ),
    }

    return handle_dir_files(
        dir_path,
        rules,
        execution_mode="serial",
        progress_desc="Convert Audio Folders",
        dir_name_suffix="_mp3towav",
    )