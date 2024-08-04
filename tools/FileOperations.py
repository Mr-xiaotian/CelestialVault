import shutil
import logging
import hashlib
import zipfile, rarfile, py7zr
from pathlib import Path
from tqdm import tqdm
from typing import Callable, Dict, Tuple, List
from collections import defaultdict


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
    if destination.exists():
        return
    
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
    from .VideoProcessing import compress_video, gif_to_video
    from .DocumentConversion import compress_pdf
    from constants import IMG_SUFFIXES, VIDEO_SUFFIXES

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
            elif file_suffix in ['pdf', 'PDF'] :
                name = new_file_path.stem.replace("_compressed", "")
                parent = new_file_path.parent
                new_pdf_path = parent / Path(name + '_compressed.pdf')
                handle_file(file_path, new_pdf_path, compress_pdf)
            elif file_suffix in ['gif', 'GIF']:
                name = new_file_path.stem.replace("_compressed", "")
                parent = new_file_path.parent
                new_video_path = parent / Path(name + '_compressed.mp4')
                handle_file(file_path, new_video_path, gif_to_video)
            else:
                handle_file(file_path, new_file_path, shutil.copy)
        except OSError as e:
            error_list.append((file_path, e))
            try:
                shutil.copy(file_path, new_file_path)
            except OSError as e:
                error_list.append((file_path, e))

    return error_list

def unzip_zip_file(zip_file: Path) -> bool:
    """
    解压缩指定的 zip 文件。
    
    :param zip_file: 要解压缩的 zip 文件路径。
    """
    try:
        with zipfile.ZipFile(zip_file) as zip_file:
            zip_file.extractall(zip_file.parent)
        logging.info(f"{zip_file} 解压缩成功")
        return True
    except zipfile.BadZipFile:
        logging.error(f"{zip_file} 不是一个有效的 zip 文件")
    except zipfile.LargeZipFile:
        logging.error(f"{zip_file} 太大了，无法解压缩")
    except RuntimeError:
        logging.error("{zip_file} 受密码保护，无法解压缩")
    return False

def unzip_rar_file(rar_file: Path) -> bool:
    """
    解压缩指定的 rar 文件。
    
    :param rar_file: 要解压缩的 rar 文件路径。
    """
    try:
        with rarfile.RarFile(rar_file) as rar_file:
            rar_file.extractall(rar_file.parent)
        logging.info(f"{rar_file} 解压缩成功")
        return True
    except rarfile.BadRarFile:
        logging.error(f"{rar_file} 不是一个有效的 rar 文件")
    except rarfile.LargeRarFile:
        logging.error(f"{rar_file} 太大了，无法解压缩")
    except rarfile.PasswordRequired:
        logging.error(f"{rar_file} 受密码保护，无法解压缩")
    return False

def unzip_7z_file(seven_zip_file: Path) -> bool:
    """
    解压缩指定的 7z 文件。
    
    :param seven_zip_file: 要解压缩的 7z 文件路径。
    """
    try:
        with py7zr.SevenZipFile(seven_zip_file, mode='r') as seven_zip_file:
            seven_zip_file.extractall(seven_zip_file.parent)
        logging.info(f"{seven_zip_file} 解压缩成功")
        return True
    except py7zr.Bad7zFile:
        logging.error(f"{seven_zip_file} 不是一个有效的 7z 文件")
    except py7zr.Large7zFile:
        logging.error(f"{seven_zip_file} 太大了，无法解压缩")
    except py7zr.PasswordRequired:
        logging.error(f"{seven_zip_file} 受密码保护，无法解压缩")
    return False
    
def unzip_files(folder_path: str | Path):
    """
    遍历指定文件夹，解压缩所有支持的压缩文件。支持的文件类型包括 zip 和 rar。
    
    :param folder_path: 要处理的文件夹的路径，可以是相对路径或绝对路径。
    """
    folder_path = Path(folder_path)
    logging.info(f'开始解压:{folder_path}')
    successful_list = []
    unsuccessful_list = []

    # 遍历文件夹
    for file_path in tqdm(list(folder_path.glob('**/*'))):
        if not file_path.is_file():
            continue

        file_suffix = file_path.suffix.lower()[1:]

        if file_suffix == 'zip':
            if unzip_zip_file(file_path):
                successful_list.append(file_path)
            else:
                unsuccessful_list.append(file_path)
        elif file_suffix == 'rar':
            if unzip_rar_file(file_path):
                successful_list.append(file_path)
            else:
                unsuccessful_list.append(file_path)
        elif file_suffix == '7z':
            if unzip_7z_file(file_path):
                successful_list.append(file_path)
            else:
                unsuccessful_list.append(file_path)
            
    logging.info(f'解压完成:{folder_path}')
    logging.info(f'成功解压文件: {successful_list}')
    logging.info(f'解压失败文件: {unsuccessful_list}')
    
    return successful_list, unsuccessful_list

def delete_files(file_path: str | Path):
    """
    删除指定文件夹中的所有文件和文件夹。
    
    :param file_path: 要处理的文件夹的路径，可以是相对路径或绝对路径。
    """
    file_path = Path(file_path)
    logging.info(f'开始删除:{file_path}')
    
    for file in tqdm(list(file_path.iterdir())):
        if file.is_file():
            file.unlink()
        elif file.is_dir():
            shutil.rmtree(file)
            
    logging.info(f'删除完成:{file_path}')

def print_directory_structure(folder_path: str='.', indent: str='', exclude_dirs: list=None, exclude_exts: list=None, max_depth: int=3):
    """
    打印指定文件夹的目录结构。
    
    :param folder_path: 起始文件夹的路径，默认为当前目录。
    :param indent: 缩进字符串，用于格式化输出。
    :param exclude_dirs: 要排除的目录列表，默认为空列表。
    :param exclude_exts: 要排除的文件扩展名列表，默认为空列表。
    :param max_depth: 最大递归深度，默认为3。
    """
    from constants import FILE_ICONS
    folder_path: Path = Path(folder_path)
    if exclude_dirs is None:
        exclude_dirs = []
    if exclude_exts is None:
        exclude_exts = []
    if max_depth < 1:
        return
    if not any(folder_path.iterdir()):
        return

    max_name_len = max(len(str(item.name)) for item in folder_path.iterdir() if item.is_file())
    
    for item in folder_path.iterdir():
        # 排除指定的目录
        if item.is_dir() and item.name in exclude_dirs:
            continue
        
        # 排除指定的文件类型
        if item.is_file() and any(item.suffix == ext for ext in exclude_exts):
            continue
        
        if item.is_dir():
            print(f"{indent}📁 {item.name}/")
            print_directory_structure(item, indent + '    ', exclude_dirs, exclude_exts, max_depth-1)
        else:
            icon = FILE_ICONS.get(item.suffix, FILE_ICONS['default'])
            print(f"{indent}{icon} {item.name:<{max_name_len}} \t({item.stat().st_size} bytes)")

def file_hash(file_path: Path) -> str:
    """
    计算文件的哈希值。

    :param file_path: 文件路径。
    :return: 文件的哈希值。
    """
    hash_algo = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_algo.update(chunk)
    return hash_algo.hexdigest()

def detect_identical_files(folder_path: str | Path) -> Dict[Tuple[str, int], List[Path]]:
    """
    检测文件夹中是否存在相同内容的文件，并在文件名后添加文件大小。

    :param folder_path: 要检测的文件夹路径。
    :return: 相同文件的字典，键为文件大小和哈希值，值为文件路径列表。
    """
    folder_path = Path(folder_path)
    
    # 根据文件大小进行初步筛选
    size_dict = defaultdict(list)
    for file_path in tqdm(list(folder_path.glob('**/*'))):
        if not file_path.is_file():
            continue
        file_size = file_path.stat().st_size
        size_dict[file_size].append(file_path)
    
    # 对于相同大小的文件，进一步计算哈希值
    hash_dict = defaultdict(list)
    for size, files in tqdm(size_dict.items()):
        if len(files) < 2:
            continue
        for file_path in files:
            file_hash_value = file_hash(file_path)
            hash_dict[(file_hash_value, size)].append(file_path)
    
    # 找出哈希值相同的文件
    identical_files = {k: v for k, v in hash_dict.items() if len(v) > 1}
    
    return identical_files

def duplicate_files_report(identical_files: Dict[Tuple[str, int], List[Path]]):
    """
    生成一个详细报告，列出所有重复的文件及其位置。

    :param identical_files: 相同文件的字典，由 detect_identical_files 函数返回。
    """
    report = []
    if identical_files:
        report.append("Identical files found:")
        for (hash_value,file_size), file_list in identical_files.items():
            report.append(f"Hash: {hash_value}")
            max_name_len = max(len(str(file)) for file in file_list)
            for file in file_list:
                report.append(f" - {str(file):<{max_name_len}} (Size: {file_size} bytes)")
    else:
        report.append("No identical files found.")
        
    print("\n".join(report))

def delete_identical_files(identical_files: Dict[Tuple[str, int], List[Path]]):
    """
    删除文件夹中所有相同内容的文件。

    :param identical_files: 相同文件的字典，由 detect_identical_files 函数返回。
    :return: 删除的文件列表。
    """
    delete_list = []
    for (hash_value,file_size), file_list in identical_files.items():
        for file in file_list:
            try:
                file.unlink()
                delete_list.append(file)
                print(f"Deleted: {file}")
            except Exception as e:
                print(f"Error deleting {file}: {e}")

    return delete_list

def move_identical_files(identical_files: Dict[Tuple[str, int], List[Path]], target_folder: str | Path, size_threshold: int = None):
    """
    将相同内容的文件移动到指定的目标文件夹。

    :param identical_files: 相同文件的字典，由 detect_identical_files 函数返回。
    :param target_folder: 目标文件夹路径。
    :param size_threshold: 文件大小阈值，只有大于此阈值的文件会被移动。如果为 None，则不限制文件大小。
    :return: 移动的文件列表。
    """
    target_folder = Path(target_folder)
    moved_files = []
    report = []

    for (hash_value, file_size), file_list in tqdm(identical_files.items()):
        for file in file_list:
            if size_threshold is not None and file_size <= size_threshold:
                continue
            target_subfolder = target_folder / hash_value
            if not target_subfolder.exists():
                target_subfolder.mkdir(parents=True)
            target_path = target_subfolder / file.name

            # 如果文件已经在目标路径，跳过
            if file.resolve() == target_path.resolve():
                report.append(f"File {file} is already in the target path.")
                continue
            
            # 仅保留一个相同名称的文件
            if target_path.exists():
                report.append(f"File {target_path} already exists. Skipping {file}.")
                file.unlink()  # 删除重复文件
                continue

            try:
                file.rename(target_path)
                moved_files.append((file, target_path))
                report.append(f"Moved: {file} -> {target_path}")
            except Exception as e:
                report.append(f"Error moving {file} to {target_path}: {e}")
    
    print("\n".join(report))

    return moved_files