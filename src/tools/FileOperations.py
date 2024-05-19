import shutil
import logging
from pathlib import Path
from tqdm import tqdm
from typing import Callable


def create_folder(path: str | Path) -> Path:
    """
    判断系统是否存在该路径,没有则创建。

    :param path: 要创建的文件夹路径。
    :return: 创建或存在的文件夹路径。
    """
    path = Path(path)  # 将输入路径转换为Path对象

    while True:
        try:
            if not path.exists():
                path.mkdir(parents=True)  # 创建目录,包括任何必要的父目录
            break
        except FileNotFoundError as e:
            print(e, path)
            path = path.parent  # 移除最后一个路径组件
            continue

    return path

def get_all_file_paths(folder_path: str | Path) -> list:
    """
    获取给定目录下所有文件的绝对路径。
    
    :param directory: 要遍历的目录路径。
    :return: 所有文件的绝对路径列表。
    """
    folder_path = Path(folder_path)
    file_paths = []  # 存储文件路径的列表

    # 遍历文件夹
    for file_path in list(folder_path.glob('**/*')):
        if not file_path.is_file():
            continue
        file_paths.append(file_path)

    return file_paths

def handle_file(source: Path, destination: Path, action: Callable[[Path, Path], None]):
    """
    处理文件，如果目标文件不存在则执行指定的操作。
    
    :param source: 源文件路径。
    :param destination: 目标文件路径。
    :param action: 处理文件的函数或方法。
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        action(source, destination)
    else:
        logging.warning(f"File {destination} already exists. Skipping...")

def compress_folder(folder_path: str | Path) -> list:
    """
    遍历指定文件夹，根据文件后缀名对文件进行压缩处理，并将处理后的文件存储到新的目录中。支持的文件类型包括图片、视频和PDF。不属于这三种类型的文件将被直接复制到新目录中。
    压缩后的文件会保持原始的目录结构。如果目标文件已存在，则会跳过处理。处理过程中遇到的任何错误都会被记录并返回。

    :param folder_path: 要处理的文件夹的路径，可以是相对路径或绝对路径。
    :return: 包含因错误未能正确处理的文件及其对应错误信息的列表。每个元素是一个元组，包括文件路径和错误对象。
    """
    from .ImageProcessing import compress_img
    from .VideoProcessing import compress_video
    from .DocumentConversion import compress_pdf
    from ..constants import IMG_SUFFIXES, VIDEO_SUFFIXES

    folder_path = Path(folder_path)
    new_folder_path = folder_path.parent / (folder_path.name + "_re")
    error_list = []

    # 遍历文件夹
    for file_path in tqdm(list(folder_path.glob('**/*'))):
        if not file_path.is_file():
            continue

        rel_path = file_path.relative_to(folder_path)
        new_file_path = new_folder_path / rel_path
        file_suffix = file_path.suffix.lower()[1:]
        try:
            if file_suffix in IMG_SUFFIXES:
                handle_file(file_path, new_file_path, compress_img)
            elif file_suffix in VIDEO_SUFFIXES:
                name = new_file_path.stem.replace("_compressed", "")
                parent = new_file_path.parent
                new_video_path = parent / Path(name + '_compressed.mp4')
                handle_file(file_path, new_video_path, compress_video)
            elif file_suffix == 'pdf':
                name = new_file_path.stem.replace("_compressed", "")
                parent = new_file_path.parent
                new_pdf_path = parent / Path(name + '_compressed.pdf')
                handle_file(file_path, new_pdf_path, compress_pdf)
            else:
                handle_file(file_path, new_file_path, shutil.copy)
        except OSError as e:
            error_list.append((file_path, e))
            try:
                shutil.copy(file_path, new_file_path)
            except OSError as e:
                error_list.append((file_path, e))

    return error_list
