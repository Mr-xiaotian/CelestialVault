import subprocess
from pathlib import Path
from moviepy.editor import *
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings


def compress_video(old_video_path: Path, new_video_path: Path):
    """
    使用ffmpeg压缩视频
    
    参数:
    old_video_path: 原始视频文件路径
    new_video_path: 压缩后视频文件路径
    """
    # command = [
    #     'ffmpeg', 
    #     '-i', str(old_video_path), 
    #     '-vcodec', 'libx264', 
    #     '-crf', '24', 
    #     str(new_video_path)
    # ]

    command = [
        'ffmpeg', 
        '-i', str(old_video_path), 
        '-vcodec', 'libx265', 
        '-crf', '28', 
        '-preset', 'medium',
        '-acodec', 'aac',
        str(new_video_path)
    ]

    subprocess.run(command, check=True)

def join_and_label_videos(video_path1: str, video_path2: str, output_path: str):
    """
    将两个视频拼接，并在左上角添加文本标签

    参数:
    video_path1: 第一个视频文件路径
    video_path2: 第二个视频文件路径
    output_path: 输出视频文件路径
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


def gif_to_video(gif_path, output_path):
    """
    将GIF文件转换为MP4视频文件

    参数:
    gif_path: GIF文件路径
    output_path: 输出MP4文件路径
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
