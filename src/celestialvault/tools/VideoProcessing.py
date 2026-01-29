import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import List, Tuple

import ffmpeg
from moviepy.editor import CompositeVideoClip, TextClip, VideoFileClip, clips_array

from celestialflow import TaskExecutor


class GetCodecExecutor(TaskExecutor):
    def process_result_dict(self):
        codec_dict = defaultdict(list)
        for path, codec in self.get_success_dict().items():
            codec_dict[codec].append(path)

        return codec_dict


def compress_video(old_video_path: Path | str, new_video_path: Path | str):
    """
    使用ffmpeg压缩视频

    :param old_video_path: 原始视频文件路径
    :param new_video_path: 压缩后视频文件路径
    """
    command = [
        "ffmpeg",
        "-i",
        str(old_video_path),
        "-vcodec",
        "libx264",
        "-crf",
        "22",  # 降低 CRF 值来提高视频质量
        "-preset",
        "medium",  # 使用 medium 预设来平衡速度和质量
        "-acodec",
        "aac",  # 添加 AAC 音频编码
        str(new_video_path),
    ]

    subprocess.run(command, check=True)


def join_and_label_videos(
    video_path1: Path | str,
    video_path2: Path | str,
    output_path: str,
    duration: int = 10,
    label1: str = None,
    label2: str = None,
):
    """
    将两个视频拼接，并在左上角添加文本标签

    :param video_path1: 第一个视频文件路径
    :param video_path2: 第二个视频文件路径
    :param output_path: 输出视频文件路径
    :param duration: 视频时长（秒）
    :param label1: 第一个视频的标签（默认文件名）
    :param label2: 第二个视频的标签（默认文件名）
    """
    # 检查输入文件
    video_path1 = Path(video_path1)
    video_path2 = Path(video_path2)
    if not video_path1.is_file():
        raise FileNotFoundError(f"视频文件不存在: {video_path1}")
    if not video_path2.is_file():
        raise FileNotFoundError(f"视频文件不存在: {video_path2}")

    # 检查输出目录
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # 加载视频
    clip1 = VideoFileClip(str(video_path1))
    clip2 = VideoFileClip(str(video_path2))

    # 确定最短视频长度
    min_duration = min(clip1.duration, clip2.duration, duration)
    clip1 = clip1.subclip(0, min_duration)
    clip2 = clip2.subclip(0, min_duration)

    # 调整分辨率
    target_height = min(clip1.size[1], clip2.size[1])
    clip1 = clip1.resize(
        height=target_height, width=int(clip1.size[0] * (target_height / clip1.size[1]))
    )
    clip2 = clip2.resize(
        height=target_height, width=int(clip2.size[0] * (target_height / clip2.size[1]))
    )

    # 获取分辨率和帧率
    width1, height1 = clip1.size
    fps = int(clip1.fps)

    # 动态设置标签
    label1 = label1 or video_path1.stem
    label2 = label2 or video_path2.stem
    fontsize = max(min(width1 // 20, 50), 12)  # 根据分辨率调整字体大小

    # 添加文本标签
    txt_clip1 = TextClip(
        label1,
        fontsize=fontsize,
        color="white",
        bg_color="black",
        size=(width1 // 2, height1 // 10),
    )
    txt_clip1 = txt_clip1.set_position(("left", "top")).set_duration(min_duration)
    txt_clip2 = TextClip(
        label2,
        fontsize=fontsize,
        color="white",
        bg_color="black",
        size=(width1 // 2, height1 // 10),
    )
    txt_clip2 = txt_clip2.set_position(("left", "top")).set_duration(min_duration)

    # 组合视频和标签
    video_with_label1 = CompositeVideoClip([clip1, txt_clip1])
    video_with_label2 = CompositeVideoClip([clip2, txt_clip2])

    # 拼接视频
    final_video = clips_array([[video_with_label1, video_with_label2]])

    # 保存结果
    final_video.write_videofile(
        output_path, fps=fps, codec="libx264", preset="medium", threads=4
    )


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
        "ffmpeg",
        "-y",
        "-i",
        gif_path,
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "faststart",
        "-vf",
        "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        output_path,
    ]

    subprocess.run(command, check=True)


def transfer_gif_dir(dir_path: str | Path) -> List[Tuple[Path, Exception]]:
    """
    将文件夹中的所有GIF文件转换为MP4视频文件

    :param dir_path: 文件夹路径
    :return: 转换结果列表，每个元素是一个元组，包含输出文件路径和可能的异常
    """

    def rename_mp4(file_path: Path) -> Path:
        name = file_path.stem.replace("_compressed", "")
        parent = file_path.parent
        return parent / Path(name + "_compressed.mp4")

    from .FileOperations import handle_dir_files

    rules = {".gif": (transfer_gif_to_video, rename_mp4, {})}
    return handle_dir_files(dir_path, rules)


def rotate_video(video_path: str | Path, output_path, angle: int) -> Path:
    """
    旋转视频文件。

    :param video_path: 视频路径（str 或 Path 对象）
    :param output_path: 输出文件路径（str 或 Path 对象）
    :param angle: 旋转角度（仅支持 0, 90, 180, 270）
    :return: 输出文件路径（Path 对象）
    """
    # 确保 video_path 是 Path 对象
    video_path = Path(video_path)

    # 检查角度是否有效
    valid_transpose = {90: 1, 180: "2,transpose=2", 270: 2}
    if angle not in valid_transpose and angle != 0:
        raise ValueError(f"不支持的旋转角度: {angle}，仅支持 0, 90, 180, 270")

    transpose = valid_transpose.get(angle, None)
    command = [
        "ffmpeg",
        "-i",
        str(video_path),
        "-vf",
        f"transpose={transpose}" if transpose else "",
        "-c:a",
        "copy",  # 复制音频，无需重新编码
        str(output_path),
    ]

    # 执行命令
    try:
        subprocess.run(command, check=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg 执行失败: {e}")
        raise

    return output_path


def rotate_video_dir(dir_path: str | Path, angle: int) -> List[Tuple[Path, Exception]]:
    """
    旋转文件夹中的所有视频文件。

    :param dir_path: 文件夹路径（str 或 Path 对象）
    :param angle: 旋转角度（仅支持 0, 90, 180, 270）
    :return: 转换结果列表，每个元素是一个元组，包含输出文件路径和可能的异常
    """

    def rename_mp4(file_path: Path, angle: int) -> Path:
        name = file_path.stem
        parent = file_path.parent
        return parent / Path(name + f"_rotated({angle}).mp4")

    from .FileOperations import handle_dir_files

    if angle in [90, 180, 270]:
        rules = {
            ".mp4": (
                lambda video_path, output_path: rotate_video(
                    video_path, output_path, angle
                ),
                lambda file_path: rename_mp4(file_path, angle),
                {},
            )
        }
    else:
        raise ValueError(f"不支持的旋转角度: {angle}，仅支持 0, 90, 180, 270")

    return handle_dir_files(
        dir_path,
        rules,
        "thread",
        progress_desc=f"Rotating videos by {angle} degrees",
    )


def get_video_codec(video_path: Path) -> str:
    """
    获取视频文件的编码格式。

    :param video_path: 视频文件路径
    :return: 编码格式
    """
    probe = ffmpeg.probe(
        video_path, v="error", select_streams="v:0", show_entries="stream=codec_name"
    )
    codec_name = probe["streams"][0]["codec_name"]
    return codec_name


def get_videos_codec(
    dir_path: Path, exclude_codecs: list[str] = ["h264"]
) -> dict[str, list[Path]]:
    """
    获取文件夹中所有视频文件的编码格式。

    :param dir_path: 文件夹路径
    :param exclude_codecs: 需要排除的编码格式列表
    :return: 编码格式字典
    """
    # 确保传入的是一个文件夹路径
    dir_path = Path(dir_path)
    if not dir_path.is_dir():
        raise ValueError(f"{dir_path} 不是有效的文件夹路径")

    get_codec_executor = GetCodecExecutor(
        get_video_codec,
        execution_mode="thread",
        enable_success_cache=True,
        progress_desc="Getting video codec",
        show_progress=True,
    )

    file_path_iter = (
        file_path for file_path in dir_path.rglob("*.mp4") if file_path.is_file()
    )  # 使用glob('**/*')遍历目录中的文件和子目录
    get_codec_executor.start(file_path_iter)

    codec_dict = get_codec_executor.process_result_dict()
    codec_dict = {
        codec: path_list
        for codec, path_list in codec_dict.items()
        if codec not in exclude_codecs
    }

    return codec_dict


def get_video_info(video_path: str):
    """
    获取视频的分辨率和显示宽高比（容器宽高比）。

    :param video_path: 视频文件的路径。
    :return: 一个字典，包含分辨率（width, height）和显示宽高比（DAR）。
    """
    # 使用 ffprobe 获取视频信息
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,display_aspect_ratio",
            "-of",
            "default=noprint_wrappers=1",
            str(video_path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # 提取结果
    output = result.stdout

    # 使用正则解析结果
    width = re.search(r"width=(\d+)", output)
    height = re.search(r"height=(\d+)", output)
    dar = re.search(r"display_aspect_ratio=(\S+)", output)

    # 格式化输出
    video_info = {
        "width": int(width.group(1)) if width else None,
        "height": int(height.group(1)) if height else None,
        "display_aspect_ratio": dar.group(1) if dar else None,
    }

    return video_info


def is_container_ratio_matching_resolution(video_path):
    """
    检查视频容器的宽高比是否与分辨率比例一致。

    :param video_info: 包含视频信息的字典，需包含 width, height, display_aspect_ratio。
    :return: 布尔值，表示是否一致。
    """
    video_info = get_video_info(video_path)
    width = video_info["width"]
    height = video_info["height"]
    dar = video_info["display_aspect_ratio"]

    if not width or not height or not dar or dar == "N/A":
        return False

    # 计算分辨率的比例
    resolution_ratio = width / height

    # 解析 DAR
    dar_width, dar_height = map(int, dar.split(":"))
    container_ratio = dar_width / dar_height

    # 比较两者
    return abs(resolution_ratio - container_ratio) < 1e-6  # 允许微小误差


def set_container_ratio_to_resolution(video_path, output_path):
    """
    修改视频容器宽高比，使其与分辨率比例一致。

    :param video_path: 输入视频文件路径。
    :param output_path: 输出视频文件路径。
    """
    video_info = get_video_info(video_path)
    if not video_info or not video_info["width"] or not video_info["height"]:
        raise ValueError("无法获取视频分辨率信息。")

    # 获取分辨率的宽高比
    width = video_info["width"]
    height = video_info["height"]
    resolution_ratio = f"{width}:{height}"

    # 使用 ffmpeg 修改 DAR
    subprocess.run(
        [
            "ffmpeg",
            "-i",
            video_path,
            "-c",
            "copy",
            "-aspect",
            resolution_ratio,
            str(output_path),
        ]
    )
