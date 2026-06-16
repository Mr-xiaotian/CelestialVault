import re
import subprocess
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path
from typing import Any

import ffmpeg
from celestialflow import TaskExecutor, TaskProgress


def compress_video(old_video_path: Path | str, new_video_path: Path | str) -> None:
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

    subprocess.run(
        command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )


def join_and_label_videos(
    video_path1: Path | str,
    video_path2: Path | str,
    output_path: str,
    duration: int = 10,
    label1: str | None = None,
    label2: str | None = None,
) -> None:
    """
    将两个视频拼接，并在左上角添加文本标签

    :param video_path1: 第一个视频文件路径
    :param video_path2: 第二个视频文件路径
    :param output_path: 输出视频文件路径
    :param duration: 视频时长（秒）
    :param label1: 第一个视频的标签（默认文件名）
    :param label2: 第二个视频的标签（默认文件名）
    """
    from moviepy.editor import CompositeVideoClip, TextClip, VideoFileClip, clips_array  # type: ignore[import-untyped,reportUnknownVariableType]  # fmt: skip  # noqa: I001

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
    clip1: Any = VideoFileClip(str(video_path1))  # type: ignore[reportUnknownVariableType]
    clip2: Any = VideoFileClip(str(video_path2))  # type: ignore[reportUnknownVariableType]

    # 确定最短视频长度
    min_duration: float = min(clip1.duration, clip2.duration, duration)  # type: ignore[reportUnknownMemberType,reportUnknownArgumentType]
    clip1 = clip1.subclip(0, min_duration)  # type: ignore[reportUnknownMemberType,reportUnknownVariableType]
    clip2 = clip2.subclip(0, min_duration)  # type: ignore[reportUnknownMemberType,reportUnknownVariableType]

    # 调整分辨率
    target_height: int = min(clip1.size[1], clip2.size[1])  # type: ignore[reportUnknownMemberType,reportUnknownArgumentType]
    clip1 = clip1.resize(  # type: ignore[reportUnknownMemberType,reportUnknownVariableType]
        height=target_height,
        width=int(clip1.size[0] * (target_height / clip1.size[1])),  # type: ignore[reportUnknownMemberType]
    )
    clip2 = clip2.resize(  # type: ignore[reportUnknownMemberType,reportUnknownVariableType]
        height=target_height,
        width=int(clip2.size[0] * (target_height / clip2.size[1])),  # type: ignore[reportUnknownMemberType]
    )

    # 获取分辨率和帧率
    width1: int
    height1: int
    width1, height1 = clip1.size  # type: ignore[reportUnknownMemberType,reportUnknownVariableType]
    fps: int = int(clip1.fps)  # type: ignore[reportUnknownMemberType]

    # 动态设置标签
    label1 = label1 or video_path1.stem
    label2 = label2 or video_path2.stem
    fontsize: int = max(min(width1 // 20, 50), 12)  # type: ignore[reportUnknownArgumentType]  # 根据分辨率调整字体大小

    # 添加文本标签
    txt_clip1: Any = TextClip(  # type: ignore[reportUnknownVariableType]
        label1,
        fontsize=fontsize,
        color="white",
        bg_color="black",
        size=(width1 // 2, height1 // 10),
    )
    txt_clip1 = txt_clip1.set_position(("left", "top")).set_duration(min_duration)  # type: ignore[reportUnknownMemberType,reportUnknownVariableType]
    txt_clip2: Any = TextClip(  # type: ignore[reportUnknownVariableType]
        label2,
        fontsize=fontsize,
        color="white",
        bg_color="black",
        size=(width1 // 2, height1 // 10),
    )
    txt_clip2 = txt_clip2.set_position(("left", "top")).set_duration(min_duration)  # type: ignore[reportUnknownMemberType,reportUnknownVariableType]

    # 组合视频和标签
    video_with_label1: Any = CompositeVideoClip([clip1, txt_clip1])  # type: ignore[reportUnknownVariableType]
    video_with_label2: Any = CompositeVideoClip([clip2, txt_clip2])  # type: ignore[reportUnknownVariableType]

    # 拼接视频
    final_video: Any = clips_array([[video_with_label1, video_with_label2]])  # type: ignore[reportUnknownVariableType]

    # 保存结果
    final_video.write_videofile(  # type: ignore[reportUnknownMemberType]
        output_path, fps=fps, codec="libx264", preset="medium", threads=4
    )


def transfer_gif_to_video(gif_path: str | Path, output_path: str | Path) -> None:
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

    subprocess.run(
        command,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )


def transfer_gif_dir(dir_path: str | Path) -> list[tuple[Path, Exception]]:
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

    rules: dict[str, tuple[Callable[..., Any], Callable[..., Any], dict[str, Any]]] = {
        ".gif": (transfer_gif_to_video, rename_mp4, {})
    }
    return handle_dir_files(dir_path, rules)


def rotate_video(video_path: str | Path, output_path: str | Path, angle: int) -> Path:
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
    valid_transpose: dict[int, int | str] = {90: 1, 180: "2,transpose=2", 270: 2}
    if angle not in valid_transpose and angle != 0:
        raise ValueError(f"不支持的旋转角度: {angle}，仅支持 0, 90, 180, 270")

    transpose: int | str | None = valid_transpose.get(angle)
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
        subprocess.run(
            command,
            check=True,
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg 执行失败: {e}")
        raise

    return output_path


def rotate_video_dir(dir_path: str | Path, angle: int) -> list[tuple[Path, Exception]]:
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

        def _rotate_video_wrapper(
            video_path: str | Path, output_path: str | Path
        ) -> Path:
            return rotate_video(video_path, output_path, angle)

        def _rename_mp4_wrapper(file_path: Path) -> Path:
            return rename_mp4(file_path, angle)

        rules: dict[
            str, tuple[Callable[..., Any], Callable[..., Any], dict[str, Any]]
        ] = {".mp4": (_rotate_video_wrapper, _rename_mp4_wrapper, {})}
    else:
        raise ValueError(f"不支持的旋转角度: {angle}，仅支持 0, 90, 180, 270")

    return handle_dir_files(
        dir_path,
        rules,
        "thread",
        name=f"Rotating videos by {angle} degrees",
    )


def get_video_codec(video_path: Path) -> str:
    """
    获取视频文件的编码格式。

    :param video_path: 视频文件路径
    :return: 编码格式
    """
    probe: Any = ffmpeg.probe(  # type: ignore[reportUnknownMemberType]
        video_path, v="error", select_streams="v:0", show_entries="stream=codec_name"
    )
    codec_name: str = probe["streams"][0]["codec_name"]
    return codec_name


def get_videos_codec(
    dir_path: Path, exclude_codecs: list[str] | None = None
) -> dict[str, list[Path]]:
    """
    获取文件夹中所有视频文件的编码格式。

    :param dir_path: 文件夹路径
    :param exclude_codecs: 需要排除的编码格式列表
    :return: 编码格式字典
    """
    # 确保传入的是一个文件夹路径
    dir_path = Path(dir_path)
    if exclude_codecs is None:
        exclude_codecs = ["h264"]
    if not dir_path.is_dir():
        raise ValueError(f"{dir_path} 不是有效的文件夹路径")

    get_codec_executor = TaskExecutor(
        "Getting video codec",
        get_video_codec,
        execution_mode="thread",
    )
    get_codec_executor.add_observer(TaskProgress())

    file_path_iter = (
        file_path for file_path in dir_path.rglob("*.mp4") if file_path.is_file()
    )  # 使用glob('**/*')遍历目录中的文件和子目录
    get_codec_executor.start(file_path_iter)

    codec_dict: defaultdict[str, list[Path]] = defaultdict(list)
    for path, codec in get_codec_executor.get_success_pairs():
        if codec in exclude_codecs:
            continue
        codec_dict[codec].append(path)

    return codec_dict


def get_video_info(video_path: str | Path) -> dict[str, int | str | None]:
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
        stderr=subprocess.DEVNULL,
        text=True,
    )

    # 提取结果
    output: str = result.stdout

    # 使用正则解析结果
    width: re.Match[str] | None = re.search(r"width=(\d+)", output)
    height: re.Match[str] | None = re.search(r"height=(\d+)", output)
    dar: re.Match[str] | None = re.search(r"display_aspect_ratio=(\S+)", output)

    # 格式化输出
    video_info: dict[str, int | str | None] = {
        "width": int(width.group(1)) if width else None,
        "height": int(height.group(1)) if height else None,
        "display_aspect_ratio": dar.group(1) if dar else None,
    }

    return video_info


def is_container_ratio_matching_resolution(video_path: str | Path) -> bool:
    """
    检查视频容器的宽高比是否与分辨率比例一致。

    :param video_path: 视频文件路径。
    :return: 布尔值，表示是否一致。
    """
    video_info = get_video_info(video_path)
    width: int | None = video_info["width"]  # type: ignore[assignment]
    height: int | None = video_info["height"]  # type: ignore[assignment]
    dar: str | None = video_info["display_aspect_ratio"]  # type: ignore[assignment]

    if not width or not height or not dar or dar == "N/A":
        return False

    # 计算分辨率的比例
    resolution_ratio = width / height

    # 解析 DAR
    dar_width, dar_height = map(int, dar.split(":"))
    container_ratio = dar_width / dar_height

    # 比较两者
    return abs(resolution_ratio - container_ratio) < 1e-6  # 允许微小误差


def set_container_ratio_to_resolution(
    video_path: str | Path, output_path: str | Path
) -> None:
    """
    修改视频容器宽高比，使其与分辨率比例一致。

    :param video_path: 输入视频文件路径。
    :param output_path: 输出视频文件路径。
    """
    video_info = get_video_info(video_path)
    if not video_info or not video_info["width"] or not video_info["height"]:
        raise ValueError("无法获取视频分辨率信息。")

    # 获取分辨率的宽高比
    width: int | None = video_info["width"]  # type: ignore[assignment]
    height: int | None = video_info["height"]  # type: ignore[assignment]
    resolution_ratio: str = f"{width}:{height}"

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
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
