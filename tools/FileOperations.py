import shutil, re
import logging
import hashlib
import zipfile, rarfile, tarfile, py7zr
from pathlib import Path
from tqdm import tqdm
from typing import Callable, Tuple, Dict, List
from collections import defaultdict
from instances.inst_task import TaskManager, ExampleTaskManager

class HandleFileManager(TaskManager):
    def __init__(self, func, folder_path: Path, new_folder_path: Path, rules: Dict[str, Tuple[Callable, Callable]], 
                 execution_mode='serial', worker_limit=50, max_retries=3, max_info=50, progress_desc="Processing", show_progress=False):
        super().__init__(func, execution_mode, worker_limit, max_retries, max_info, progress_desc, show_progress)
        self.folder_path = folder_path
        self.new_folder_path = new_folder_path
        self.rules = rules

    def get_args(self, file_path: Path):
        rel_path = file_path.relative_to(self.folder_path)
        new_file_path = self.new_folder_path / rel_path

        file_suffix = file_path.suffix.lower().lstrip('.')
        action_func, rename_func = self.rules.get(file_suffix, (shutil.copy, lambda x: x))

        final_path = rename_func(new_file_path)
        return (file_path, final_path, action_func)
    
    def process_result(self, file_path: Path, result):
        return
    
    def handle_error_dict(self):
        error_path_dict = defaultdict(list)

        for file_path, error in self.get_error_dict().items():
            rel_path = file_path.relative_to(self.folder_path)
            new_file_path = self.new_folder_path / rel_path
            shutil.copy(file_path, new_file_path)
            error_path_dict[(type(error).__name__, str(error))].append(new_file_path)
        return error_path_dict
    

class DetectIdenticalManager(TaskManager):
    def get_args(self, task):
        return (task[0], )
    
    def process_result(self, task: Path, result):
        return result
    
    def process_result_dict(self):
        result_path_dict = defaultdict(list)

        for (path, size), hash_vault in self.get_result_dict().items():
            result_path_dict[(hash_vault, size)].append(path)
        return result_path_dict
    

class ScanFileManager(ExampleTaskManager):
    def process_result_dict(self):
        size_dict = defaultdict(list)

        for path, size in self.get_result_dict().items():
            size_dict[size].append(path)
        return size_dict


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

def handle_file(source: Path, destination: Path, action: Callable[[Path, Path], None]):
    """
    处理文件，如果目标文件不存在则执行指定的操作。
    
    :param source: 源文件路径。
    :param destination: 目标文件路径。
    :param action: 处理文件的函数或方法。
    """
    if destination.exists():
        return
    
    # 判断 destination 是文件还是文件夹
    if destination.suffix:
        destination.parent.mkdir(parents=True, exist_ok=True)
    else:
        destination.mkdir(parents=True, exist_ok=True)
    action(source, destination)

def handle_folder(folder_path: str | Path, rules: Dict[str, Tuple[Callable[[Path, Path], None], Callable[[Path], Path]]], 
                  execution_mode: str = 'serial', progress_desc: str = "Processing files") -> Dict[Exception, List[Path]]:
    """
    遍历指定文件夹，根据文件后缀名对文件进行处理，并将处理后的文件存储到新的目录中。
    不属于指定后缀的文件将被直接复制到新目录中。处理后的文件会保持原始的目录结构。
    如果目标文件已存在，则会跳过处理。处理过程中遇到的任何错误都会被记录并返回。

    :param folder_path: 要处理的文件夹的路径，可以是相对路径或绝对路径。
    :param rules: 一个字典，键为文件后缀，值为处理该类型文件的函数和重命名函数的元组。
    :param execution_mode: 执行模式，可以是 'serial' 或 'thread' 'process'。默认为 'serial'。
    :param progress_desc: 进度条描述。
    :return: 包含因错误未能正确处理的文件及其对应错误信息的列表。每个元素是一个元组，包括文件路径和错误对象。
    """
    folder_path = Path(folder_path)
    new_folder_path = folder_path.parent / (folder_path.name + "_re")

    handlefile_manager = HandleFileManager(handle_file, folder_path, new_folder_path, rules,
                                           execution_mode=execution_mode, worker_limit=6, 
                                           progress_desc=progress_desc, show_progress=True)

    file_path_list = [file_path for file_path in folder_path.glob('**/*') if file_path.is_file()]
    handlefile_manager.start(file_path_list)

    error_path_dict = handlefile_manager.handle_error_dict()
    return error_path_dict

def compress_folder(folder_path: str | Path, execution_mode: str = 'thread') -> List[Tuple[Path, Exception]]:
    """
    遍历指定文件夹，根据文件后缀名对文件进行压缩处理，并将处理后的文件存储到新的目录中。
    支持的文件类型包括图片、视频和PDF。不属于这三种类型的文件将被直接复制到新目录中。
    压缩后的文件会保持原始的目录结构。如果目标文件已存在，则会跳过处理。处理过程中遇到的任何错误都会被记录并返回。

    :param folder_path: 要处理的文件夹的路径，可以是相对路径或绝对路径。
    :param execution_mode: 执行模式，可以是 'serial' 或 'thread' 'process'。默认为 'thread'。
    :return: 包含因错误未能正确处理的文件及其对应错误信息的列表。每个元素是一个元组，包括文件路径和错误对象。
    """
    def rename_mp4(file_path: Path) -> Path:
        name = file_path.stem.replace("_compressed", "")
        suffix = file_path.suffix.lstrip('.')
        new_name = f"{name}({suffix})_compressed.mp4"
        return file_path.with_name(new_name)
    
    def rename_pdf(file_path: Path) -> Path:
        name = file_path.stem.replace("_compressed", "")
        new_name = f"{name}_compressed.pdf"
        return file_path.with_name(new_name)

    from tools.ImageProcessing import compress_img
    from tools.VideoProcessing import compress_video
    from tools.DocumentConversion import compress_pdf
    from constants import IMG_SUFFIXES, VIDEO_SUFFIXES

    rules = {suffix: (compress_img, lambda x: x) for suffix in IMG_SUFFIXES}
    rules.update({suffix: (compress_video,rename_mp4) for suffix in VIDEO_SUFFIXES})
    rules.update({suffix: (compress_pdf,rename_pdf) for suffix in ['pdf', 'PDF']})

    return handle_folder(folder_path, rules, execution_mode, progress_desc='Compressing folder')

def unzip_zip_file(zip_file: Path, destination: Path):
    """
    解压缩指定的 zip 文件。
    
    :param zip_file: 要解压缩的 zip 文件路径。
    :raises ValueError: 如果文件不是有效的 zip 文件或发生其他错误。
    """
    try:
        with zipfile.ZipFile(zip_file) as zip_file:
            zip_file.extractall(destination)
    except zipfile.BadZipFile:
        raise ValueError(f"{zip_file} 不是一个有效的 zip 文件")
    except zipfile.LargeZipFile:
        raise ValueError(f"{zip_file} 太大了，无法解压缩")
    except RuntimeError:
        raise ValueError("{zip_file} 受密码保护，无法解压缩")

def unzip_rar_file(rar_file: Path, destination: Path):
    """
    解压缩指定的 rar 文件。
    
    :param rar_file: 要解压缩的 rar 文件路径。
    """
    try:
        with rarfile.RarFile(rar_file) as rar_file:
            rar_file.extractall(destination)
    except rarfile.BadRarFile:
        raise ValueError(f"{rar_file} 不是一个有效的 rar 文件")
    except rarfile.LargeRarFile:
        raise ValueError(f"{rar_file} 太大了，无法解压缩")
    except rarfile.PasswordRequired:
        raise ValueError(f"{rar_file} 受密码保护，无法解压缩")

def unzip_tar_file(tar_file: Path, destination: Path):
    """
    解压缩指定的 tar 文件。
    
    :param tar_file: 要解压缩的 tar 文件路径。
    :param destination: 解压缩的目标路径。
    :raises ValueError: 如果文件不是有效的 tar 文件或发生其他错误。
    """
    # 检查是否为有效的 tar 文件
    if not tarfile.is_tarfile(tar_file):
        raise ValueError(f"{tar_file} 不是一个有效的 tar 文件")
    try:
        # 打开 tar 文件
        with tarfile.open(tar_file) as tar:
            # 提取所有内容到目标路径
            tar.extractall(path=destination)
    except tarfile.ReadError:
        raise ValueError(f"{tar_file} 读取错误，可能不是一个有效的 tar 文件")
    except Exception as e:
        raise ValueError(f"解压 {tar_file} 时发生错误: {e}")

def unzip_7z_file(seven_zip_file: Path, destination: Path):
    """
    解压缩指定的 7z 文件。
    
    :param seven_zip_file: 要解压缩的 7z 文件路径。
    :raises ValueError: 如果文件不是有效的 7z 文件或发生其他错误。
    """
    try:
        with py7zr.SevenZipFile(seven_zip_file, mode='r') as seven_zip_file:
            seven_zip_file.extractall(destination)
    except py7zr.Bad7zFile:
        raise ValueError(f"{seven_zip_file} 不是一个有效的 7z 文件")
    except py7zr.Large7zFile:
        raise ValueError(f"{seven_zip_file} 太大了，无法解压缩")
    except py7zr.PasswordRequired:
        raise ValueError(f"{seven_zip_file} 受密码保护，无法解压缩")

def unzip_folder(folder_path: str | Path):
    """
    遍历指定文件夹，解压缩所有支持的压缩文件。支持的文件类型包括 zip 和 rar。
    
    :param folder_path: 要处理的文件夹的路径，可以是相对路径或绝对路径。
    """
    def rename_unzip(file_path: Path) -> Path:
        name = file_path.stem
        suffix = file_path.suffix.lstrip('.')
        new_name = f"{name}({suffix})_unzip"
        return file_path.with_name(new_name)
    
    rules = {'zip': (unzip_zip_file, rename_unzip)}
    rules.update({'rar': (unzip_rar_file, rename_unzip)})
    rules.update({'tar': (unzip_tar_file, rename_unzip)})
    rules.update({'7z': (unzip_7z_file, rename_unzip)})

    return handle_folder(folder_path, rules, progress_desc="Unziping folder")

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

    # 计算文件名的最大长度，如果没有文件，设置默认长度
    files = [item for item in folder_path.iterdir() if item.is_file()]
    max_name_len = max((len(str(item.name)) for item in files), default=0)
    
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

def get_file_hash(file_path: Path) -> str:
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

def detect_identical_files(folder_path: str | Path, execution_mode: str ='thread') -> Dict[Tuple[str, int], List[Path]]:
    """
    检测文件夹中是否存在相同内容的文件，并在文件名后添加文件大小。

    :param folder_path: 要检测的文件夹路径。
    :return: 相同文件的字典，键为文件大小和哈希值，值为文件路径列表。
    """
    folder_path = Path(folder_path)
    
    # 根据文件大小进行初步筛选
    scan_file_manager = ScanFileManager(lambda x: x.stat().st_size, execution_mode, 
                                        progress_desc='Scanning files', show_progress=True)

    file_path_list = [path for path in folder_path.rglob('*') if path.is_file()]
    scan_file_manager.start(file_path_list)

    size_dict = scan_file_manager.process_result_dict()
    size_dict = {k: v for k, v in size_dict.items() if len(v) > 1}
    
    # 对于相同大小的文件，进一步计算哈希值
    detect_identical_manager = DetectIdenticalManager(get_file_hash, execution_mode, 
                                                      progress_desc='Calculating file hashes', show_progress=True)

    file_task_list = [(file_path, size) for size, files in size_dict.items() for file_path in files]
    detect_identical_manager.start(file_task_list)

    # 找出哈希值相同的文件
    hash_dict = detect_identical_manager.process_result_dict()
    identical_dict = {k: v for k, v in hash_dict.items() if len(v) > 1}
    
    return identical_dict

def duplicate_files_report(identical_dict: Dict[Tuple[str, int], List[Path]]):
    """
    生成一个详细报告，列出所有重复的文件及其位置。

    :param identical_dict: 相同文件的字典，由 detect_identical_files 函数返回。
    """
    from tools.Utilities import bytes_to_human_readable
    if not identical_dict:
        print("\nNo identical files found.")
        return 

    report = []
    total_size = 0
    total_file_num = 0
    max_file_num = 0
    sort_identical_dict = dict(sorted(identical_dict.items(), key=lambda item: item[0][1], reverse=True))
    report.append("\nIdentical files found:\n")
    for (hash_value,file_size), file_list in sort_identical_dict.items():
        report.append(f"Hash: {hash_value} (Size: {file_size} bytes)")

        file_num = len(file_list)
        total_size += file_size * file_num
        total_file_num += file_num

        if file_num > max_file_num:
            max_file_num = file_num
            max_file_key = (hash_value,file_size)

        max_name_len = max(len(str(file)) for file in file_list)
        readable_size = bytes_to_human_readable(file_size)
        for file in file_list:
            report.append(f" - {str(file):<{max_name_len}} (Size: {readable_size})")

    report.append(f"\n\nTotal size of duplicate files: {bytes_to_human_readable(total_size)}")
    report.append(f"Total number of duplicate files: {total_file_num}")
    report.append(f"File with the most duplicates: {max_file_key}")
        
    print("\n".join(report))

def delete_identical_files(identical_dict: Dict[Tuple[str, int], List[Path]]):
    """
    删除文件夹中相同内容的文件。

    :param identical_dict: 相同文件的字典，由 detect_identical_files 函数返回。
    :return: 删除的文件列表。
    """
    from tools.Utilities import bytes_to_human_readable
    report = []
    delete_size = 0
    for (hash_value,file_size), file_list in identical_dict.items():
        for file in tqdm(file_list, desc='Deleting files'):
            try:
                file.unlink()
                delete_size += file_size
                report.append(f"Deleted: {file}")
            except Exception as e:
                report.append(f"Error deleting {file}: {e}")

    report.append(f"\nTotal size of deleted files: {bytes_to_human_readable(delete_size)}")
    print("\n".join(report))

def move_identical_files(identical_dict: Dict[Tuple[str, int], List[Path]], target_folder: str | Path, size_threshold: int = None):
    """
    将相同内容的文件移动到指定的目标文件夹。

    :param identical_dict: 相同文件的字典，由 detect_identical_files 函数返回。
    :param target_folder: 目标文件夹路径。
    :param size_threshold: 文件大小阈值，只有大于此阈值的文件会被移动。如果为 None，则不限制文件大小。
    :return: 移动的文件列表。
    """
    target_folder = Path(target_folder)
    moved_files = []
    report = []

    for (hash_value, file_size), file_list in tqdm(identical_dict.items()):
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

def folder_to_file_path(folder_path: Path, file_extension: str) -> Path:
    """
    将文件夹路径转换为与文件夹同名的文件路径。
    例如，给定文件夹路径 '/home/user/folder1' 和文件扩展名 'txt'，函数会返回文件路径 '/home/user/folder1.txt'。

    :param folder_path: 文件夹的路径。
    :param file_extension: 文件扩展名。
    :return: 与文件夹同名的文件路径。
    """
    # 获取文件夹的父目录和文件夹名称
    folder_name = folder_path.stem  # 获取文件夹名称，不带路径
    parent_dir = folder_path.parent  # 获取文件夹的父目录路径
    
    # 生成与文件夹同名的文件路径
    file_name = f"{folder_name}.{file_extension}"
    file_path = parent_dir / file_name
    
    return file_path

def replace_filenames(folder_path: Path | str, pattern: str, replacement: str):
    """
    使用正则表达式替换文件夹中所有文件名中的匹配部分。
    
    遍历指定文件夹，将其中每个文件的文件名中的匹配内容替换为 `replacement`。

    :param folder_path: 文件夹的路径。
    :param pattern: 用于匹配文件名的正则表达式。
    :param replacement: 替换后的新内容。
    """
    folder_path = Path(folder_path)  # 将传入的路径转换为Path对象
    for file in folder_path.glob('**/*'):  # 使用glob('**/*')遍历目录中的文件和子目录
        if not file.is_file():  # 检查是否为文件
            continue
        
        new_filename = re.sub(pattern, replacement, file.name)
        if new_filename == file.name:
            continue
        
        new_file_path = file.with_name(new_filename)  # 使用with_name方法生成新文件路径
        file.rename(new_file_path)  # 重命名文件