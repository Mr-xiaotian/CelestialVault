import subprocess, os
import cv2
import ffmpeg
from pathlib import Path
from typing import Tuple, List
from collections import defaultdict
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, clips_array
from moviepy.config import change_settings
from instances.inst_task import ExampleTaskManager


class GetCodecManager(ExampleTaskManager):
    def process_result_dict(self):
        codec_dict = defaultdict(list)
        for path, codec in self.result_dict.items():
            codec_dict[codec].append(path)

        return codec_dict

def compress_video(old_video_path: Path|str, new_video_path: Path|str):
    """
    使用ffmpeg压缩视频
    
    :param old_video_path: 原始视频文件路径
    :param new_video_path: 压缩后视频文件路径
    """
    command = [
        'ffmpeg', 
        '-i', str(old_video_path), 
        '-vcodec', 'libx264', 
        '-crf', '22',  # 降低 CRF 值来提高视频质量
        '-preset', 'medium',  # 使用 medium 预设来平衡速度和质量
        '-acodec', 'aac',  # 添加 AAC 音频编码
        str(new_video_path)
    ]

    # command = [
    #     'ffmpeg', 
    #     '-i', str(old_video_path), 
    #     '-vcodec', 'libx265', 
    #     '-crf', '23', 
    #     '-preset', 'medium',
    #     '-acodec', 'aac',
    #     str(new_video_path)
    # ]

    subprocess.run(command, check=True)

def join_and_label_videos(video_path1: str, video_path2: str, output_path: str):
    """
    将两个视频拼接，并在左上角添加文本标签

    :param video_path1: 第一个视频文件路径
    :param video_path2: 第二个视频文件路径
    :param output_path: 输出视频文件路径
    """
    change_settings({"IMAGEMAGICK_BINARY": r"G:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

    # 加载视频，设置持续时间为10秒
    clip1 = VideoFileClip(video_path1).subclip(0, 10)
    clip2 = VideoFileClip(video_path2).subclip(0, 10)

    # 在视频左上角添加文本标签
    video_name1 = os.path.basename(video_path1)
    video_name2 = os.path.basename(video_path2)

    txt_clip1 = TextClip(video_name1, fontsize=24, color='white')
    txt_clip1 = txt_clip1.set_position(('left', 'top')).set_duration(10)
    
    txt_clip2 = TextClip(video_name2, fontsize=24, color='white')
    txt_clip2 = txt_clip2.set_position(('left', 'top')).set_duration(10)

    # 将文本标签与视频组合
    video_with_label1 = CompositeVideoClip([clip1, txt_clip1])
    video_with_label2 = CompositeVideoClip([clip2, txt_clip2])

    # 将两个视频左右拼接
    final_video = clips_array([[video_with_label1, video_with_label2]])

    # 保存结果
    final_video.write_videofile(output_path, fps=24)

def transfer_gif_to_video(gif_path, output_path):
    """
    将GIF文件转换为MP4视频文件

    :param gif_path: GIF文件路径
    :param  output_path: 输出MP4文件路径
    """
    # 将路径转换为字符串
    gif_path = str(gif_path)
    output_path = str(output_path)
    
    # 使用FFmpeg命令进行转换
    command = [
        'ffmpeg', '-y', '-i', gif_path,
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-movflags', 'faststart', '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',
        output_path
    ]
    
    subprocess.run(command, check=True)

def transfer_gif_folder(folder_path: str | Path) -> List[Tuple[Path, Exception]]:
    """
    将文件夹中的所有GIF文件转换为MP4视频文件

    :param folder_path: 文件夹路径
    :return: 转换结果列表，每个元素是一个元组，包含输出文件路径和可能的异常
    """
    def rename_mp4(file_path: Path) -> Path:
        name = file_path.stem.replace("_compressed", "")
        parent = file_path.parent
        return parent / Path(name + '_compressed.mp4')
    
    from tools.FileOperations import handle_folder

    rules = {'.gif': (transfer_gif_to_video, rename_mp4)}
    return handle_folder(folder_path, rules)

def rotate_video(video_path: str | Path, angle: int) -> Path:
    """
    旋转视频文件。
    
    :param video_path: 视频路径（str 或 Path 对象）
    :param angle: 旋转角度（仅支持 0, 90, 180, 270）
    :return: 输出文件路径（Path 对象）
    """
    # 确保 video_path 是 Path 对象
    video_path = Path(video_path)

    # 检查角度是否有效
    if angle not in {0, 90, 180, 270}:
        raise ValueError(f"不支持的旋转角度: {angle}，仅支持 0, 90, 180, 270")

    # 构造输出路径
    output_path = video_path.with_name(f"{video_path.stem}_rotated({angle}).mp4")

    # 构造 FFmpeg 命令
    if angle == 90:
        transpose = 1
    elif angle == 180:
        transpose = "2,transpose=2"
    elif angle == 270:
        transpose = 2
    
    command = [
        "ffmpeg",
        "-i", str(video_path),
        "-vf", f"transpose={transpose}",
        "-c:a", "copy",  # 复制音频，无需重新编码
        str(output_path)
    ]

    # 执行命令
    try:
        subprocess.run(command, check=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg 执行失败: {e}")
        raise
    
    return output_path

def get_video_codec(video_path: Path) -> str:
    """
    获取视频文件的编码格式。

    :param video_path: 视频文件路径
    :return: 编码格式
    """
    probe = ffmpeg.probe(video_path, v='error', select_streams='v:0', show_entries='stream=codec_name')
    codec_name = probe['streams'][0]['codec_name']
    return codec_name

def get_videos_codec(folder_path: Path, exclude_codecs: list[str]=['h264']) -> dict[str, list[Path]]:
    """
    获取文件夹中所有视频文件的编码格式。

    :param folder_path: 文件夹路径
    :param exclude_codecs: 需要排除的编码格式列表
    :return: 编码格式字典
    """
    # 确保传入的是一个文件夹路径
    folder_path = Path(folder_path)
    if not folder_path.is_dir():
        raise ValueError(f"{folder_path} 不是有效的文件夹路径")
    
    get_codec_manager = GetCodecManager(get_video_codec, execution_mode='thread', progress_desc="Getting video codec", show_progress=True)

    file_path_iter = (file_path for file_path in folder_path.rglob("*.mp4") if file_path.is_file()) # 使用glob('**/*')遍历目录中的文件和子目录
    get_codec_manager.start(file_path_iter)
    codec_dict = get_codec_manager.process_result_dict()
    codec_dict = {codec: path_list for codec, path_list in codec_dict.items() if codec not in exclude_codecs}
    
    return codec_dict