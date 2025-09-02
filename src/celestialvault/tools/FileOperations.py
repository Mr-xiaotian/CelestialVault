import hashlib
import os
import re
import shutil
import tarfile
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import py7zr
import rarfile
from tqdm import tqdm
from wcwidth import wcswidth
from celestialflow import TaskManager

from ..constants import FILE_ICONS, IMG_SUFFIXES, VIDEO_SUFFIXES
from .TextTools import format_table
from .Utilities import bytes_to_human_readable


class HandleFileManager(TaskManager):
    def __init__(
        self,
        func: Callable,
        folder_path: Path,
        new_folder_path: Path,
        rules: Dict[str, Tuple[Callable, Callable]],
        execution_mode: str,
        progress_desc: str,
    ):
        super().__init__(
            func=func,
            execution_mode=execution_mode,
            worker_limit=6,
            max_info=100,
            enable_result_cache=True,
            progress_desc=progress_desc,
            show_progress=True,
        )
        self.folder_path = folder_path
        self.new_folder_path = new_folder_path
        self.rules = rules

    def get_args(self, file_path: Path):
        rel_path = file_path.relative_to(self.folder_path)
        new_file_path = self.new_folder_path / rel_path

        file_suffix = file_path.suffix.lower()
        action_func, rename_func, args_extra = self.rules.get(
            file_suffix, (shutil.copy2, lambda x: x, {})
        )

        final_path = rename_func(new_file_path)
        return (file_path, final_path, action_func, args_extra)

    def process_result(self, file_path: Path, result):
        return

    def handle_error_dict(self):
        error_path_dict = defaultdict(list)

        for file_path, error in self.get_error_dict().items():
            rel_path = file_path.relative_to(self.folder_path)
            new_file_path = self.new_folder_path / rel_path
            shutil.copy(file_path, new_file_path)
            error_path_dict[(type(error).__name__, str(error))].append(new_file_path)
        return dict(error_path_dict)
    

class HandleSubFolderManager(HandleFileManager):
    def get_args(self, sub_folder_path: Path):
        rel_path = sub_folder_path.relative_to(self.folder_path)
        new_sub_folder_path = self.new_folder_path / rel_path

        action_func, rename_func, args_extra = self.rules.get(
            'folder', (shutil.copy, lambda x: x, {})
        )

        final_path = rename_func(new_sub_folder_path)
        return (sub_folder_path, final_path, action_func, args_extra)


class ScanSizeManager(TaskManager):
    def process_result_dict(self):
        size_dict = defaultdict(list)

        for path, size in self.get_success_dict().items():
            size_dict[size].append(path)

        size_dict = {k: v for k, v in size_dict.items() if len(v) > 1}
        file_size_iter = (
            (file_path, size)
            for size, files in size_dict.items()
            for file_path in files
        )
        return file_size_iter


class ScanHashManager(TaskManager):
    def get_args(self, task):
        return (task[0],)

    def process_result_dict(self):
        identical_dict = defaultdict(list)

        for (path, size), hash_value in self.get_success_dict().items():
            identical_dict[(hash_value, size)].append(path)

        identical_dict = {k: v for k, v in identical_dict.items() if len(v) > 1}
        return identical_dict


class DeleteManager(TaskManager):
    def __init__(self, func, parent_dir: Path):
        super().__init__(func, progress_desc="Delete files/folders", show_progress=True)
        self.parent_dir = parent_dir

    def get_args(self, rel_path):
        target = self.parent_dir / rel_path
        return (target,)


class CopyManager(TaskManager):
    def __init__(self, func, main_dir: Path, minor_dir: Path, copy_mode: str):
        super().__init__(
            func, progress_desc=f"Copy files/folders[{copy_mode}]", show_progress=True
        )
        self.main_dir = main_dir
        self.minor_dir = minor_dir

    def get_args(self, rel_path: Path):
        source = self.main_dir / rel_path
        target = self.minor_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        return (source, target)


class DeleteReturnSizeManager(TaskManager):
    def process_result_dict(self):
        delete_size = 0
        for size in self.get_success_dict().values():
            delete_size += size
        return delete_size


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


def handle_item(source: Path, destination: Path, action: Callable[[Path, Path, Any], Any], extra: dict):
    """
    处理文件，如果目标文件不存在则执行指定的操作。

    :param source: 源文件路径。
    :param destination: 目标文件路径。
    :param action: 处理文件的函数或方法。
    :return: 如果目标文件已存在，则返回 None；否则返回 action 的结果。
    """
    if destination.exists():
        return f"{destination} already exists."

    # 判断 destination 是文件还是文件夹
    if destination.suffix:
        destination.parent.mkdir(parents=True, exist_ok=True)
    else:
        destination.mkdir(parents=True, exist_ok=True)
    action_result = action(source, destination, **extra)
    return action_result


def handle_folder_files(
    folder_path: str | Path,
    rules: Dict[str, Tuple[Callable[[Path, Path, Dict], None], Callable[[Path], Path]]],
    execution_mode: str = "serial",
    progress_desc: str = "Processing files",
    folder_name_suffix: str = "_re",
) -> Dict[Tuple[str, str], List[Path]]:
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
    new_folder_path = folder_path.parent / (folder_path.name + folder_name_suffix)

    handlefile_manager = HandleFileManager(
        func=handle_item,
        folder_path=folder_path,
        new_folder_path=new_folder_path,
        rules=rules,
        execution_mode=execution_mode,
        progress_desc=progress_desc,
    )

    file_path_iter = (
        file_path for file_path in folder_path.glob("**/*") if file_path.is_file()
    )
    handlefile_manager.start(file_path_iter)

    error_path_dict = handlefile_manager.handle_error_dict()
    return error_path_dict

def handle_subfolders(
    folder_path: str | Path,
    rules: Dict[str, Tuple[Callable[[Path, Path, Dict], None], Callable[[Path], Path]]],
    execution_mode: str = "serial",
    progress_desc: str = "Processing folders",
    folder_name_suffix: str = "_re",
) -> Dict[Tuple[str, str], List[Path]]:
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
    new_folder_path = folder_path.parent / (folder_path.name + folder_name_suffix)

    handlefile_manager = HandleSubFolderManager(
        func=handle_item,
        folder_path=folder_path,
        new_folder_path=new_folder_path,
        rules=rules,
        execution_mode=execution_mode,
        progress_desc=progress_desc,
    )

    sub_folder_iter = (
        sub_folder for sub_folder in folder_path.iterdir() if sub_folder.is_dir()
        )
    handlefile_manager.start(sub_folder_iter)

    error_path_dict = handlefile_manager.handle_error_dict()
    return error_path_dict

def compress_folder(
    folder_path: str | Path, execution_mode: str = "thread"
) -> List[Tuple[Path, Exception]]:
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
        suffix = file_path.suffix.lstrip(".")
        new_name = f"{name}({suffix})_compressed.mp4"
        return file_path.with_name(new_name)

    def rename_pdf(file_path: Path) -> Path:
        name = file_path.stem.replace("_compressed", "")
        new_name = f"{name}_compressed.pdf"
        return file_path.with_name(new_name)

    from .ImageProcessing import compress_img
    from .VideoProcessing import compress_video
    # from .DocumentConversion import compress_pdf

    rules = {suffix: (compress_img, lambda x: x, {}) for suffix in IMG_SUFFIXES}
    rules.update({suffix: (compress_video, rename_mp4, {}) for suffix in VIDEO_SUFFIXES})
    # rules.update({'.pdf': (compress_pdf,rename_pdf, {})})

    return handle_folder_files(
        folder_path, rules, execution_mode, progress_desc="Compressing Folder"
    )


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
        with py7zr.SevenZipFile(seven_zip_file, mode="r") as seven_zip_file:
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
        suffix = file_path.suffix.lstrip(".")
        new_name = f"{name}({suffix})_unzip"
        return file_path.with_name(new_name)

    rules = {
        ".zip": (unzip_zip_file, rename_unzip, {}),
        ".rar": (unzip_rar_file, rename_unzip, {}), 
        ".tar": (unzip_tar_file, rename_unzip, {}), 
        ".7z": (unzip_7z_file, rename_unzip, {})
    }

    return handle_folder_files(folder_path, rules, progress_desc="Unziping folder")


def print_directory_structure(
    folder_path: str = ".",
    exclude_dirs: list = None,
    exclude_exts: list = None,
    max_depth: int = 3,
):
    """
    打印指定文件夹的目录结构。

    :param folder_path: 起始文件夹的路径，默认为当前目录。
    :param exclude_dirs: 要排除的目录列表，例如["log"], 默认为空列表。
    :param exclude_exts: 要排除的文件扩展名列表，例如[".db"], 默认为空列表。
    :param max_depth: 最大递归深度，默认为3。
    """
    folder_path: Path = Path(folder_path)

    if exclude_dirs is None:
        exclude_dirs = []
    if exclude_exts is None:
        exclude_exts = []

    def get_structure_list(folder_path: Path, indent, max_depth):
        if max_depth < 1:
            return [], get_folder_size(folder_path)
        if not any(folder_path.iterdir()):
            return [], 0

        # 计算文件名的最大长度，如果没有文件，设置默认长度
        files = [item for item in folder_path.iterdir() if item.is_file()]
        max_name_len = max((wcswidth(str(item.name)) for item in files), default=0)

        folder_structure_list = []
        file_structure_list = []
        folder_size = 0

        exclude_dirs_size = 0
        exclude_file_size = 0

        exclude_dirs_num = 0
        exclude_file_num = 0

        for item in folder_path.iterdir():
            if item.is_dir():
                # 排除指定的目录
                if item.name in exclude_dirs:
                    subfolder_size = get_folder_size(item)
                    folder_size += subfolder_size
                    exclude_dirs_size += subfolder_size
                    exclude_dirs_num += 1
                    continue

                subfolder_structure_list, subfolder_size = get_structure_list(
                    item, indent + "    ", max_depth - 1
                )
                folder_size += subfolder_size

                reable_subfolder_size = bytes_to_human_readable(subfolder_size)
                folder_structure_list.append(
                    f"{indent}📁 {item.name}/    ({reable_subfolder_size})"
                )
                folder_structure_list.extend(subfolder_structure_list)
            else:
                # 排除指定的文件类型
                if any(item.suffix == ext for ext in exclude_exts):
                    file_size = item.stat().st_size
                    folder_size += file_size
                    exclude_file_size += file_size
                    exclude_file_num += 1
                    continue

                file_size = item.stat().st_size
                folder_size += file_size

                icon = FILE_ICONS.get(item.suffix, FILE_ICONS["default"])
                reable_file_size = bytes_to_human_readable(file_size)
                file_structure_list.append(
                    f"{indent}{icon} {item.name:<{max_name_len - (wcswidth(item.name)-len(item.name))}}\t({reable_file_size})"
                )

        if exclude_dirs_num > 0:
            reable_exclude_dirs_size = bytes_to_human_readable(exclude_dirs_size)
            folder_structure_list.append(
                f"{indent}📁 [{exclude_dirs_num}项排除的目录]    ({reable_exclude_dirs_size})"
            )
        if exclude_file_num > 0:
            reable_exclude_file_size = bytes_to_human_readable(exclude_file_size)
            file_structure_list.append(
                f"{indent}📄 [{exclude_file_num}项排除的文件]    ({reable_exclude_file_size})"
            )

        structure_list = folder_structure_list + file_structure_list
        return structure_list, folder_size

    structure_list, folder_size = get_structure_list(folder_path, "    ", max_depth)
    reable_folder_size = bytes_to_human_readable(folder_size)

    structure_list = [
        f"📁 {folder_path.name}/    ({reable_folder_size})"
    ] + structure_list
    print("\n".join(structure_list))


def compare_structure(
    dir1: str|Path,
    dir2: str|Path,
    exclude_dirs: list = None,
    exclude_exts: list = None,
    compare_common_file=False,
):
    """
    比较两个文件夹的结构，并打印出仅在一个文件夹中存在的文件或文件夹。

    :param dir1: 第一个文件夹路径
    :param dir2: 第二个文件夹路径
    :param exclude_dirs: 要排除的目录列表，默认为空列表
    :param exclude_exts: 要排除的文件扩展名列表，默认为空列表
    :param compare_common_file: 是否比较两个文件夹中相同文件的大小
    """
    def _collect_structure_diff(d1, d2, indent):
        try:
            d1_files = set(os.listdir(d1))
            d2_files = set(os.listdir(d2))
        except (FileNotFoundError, PermissionError) as e:
            return [f"{indent}📁 [{d1}] 或 [{d2}] 无法访问: {e}"]

        only_in_d1 = sorted(d1_files - d2_files)
        only_in_d2 = sorted(d2_files - d1_files)
        common_files = sorted(d1_files & d2_files)

        d1_folder_list, d1_file_list = _process_unique_items(d1, only_in_d1, indent, origin="dir1")
        d2_folder_list, d2_file_list = _process_unique_items(d2, only_in_d2, indent, origin="dir2")

        common_folder_list, common_file_list = _compare_common_items(d1, d2, common_files, indent)

        return d1_folder_list + d2_folder_list + common_folder_list + d1_file_list + d2_file_list + common_file_list
    
    def _process_unique_items(base_dir, items, indent, origin):
        folder_list = []
        file_list = []
        for item in items:
            path: Path = base_dir / item
            if path.is_dir():
                if item in exclude_dirs:
                    continue
                size = get_folder_size(path)
                folder_list.append(f"{indent}📁 [{base_dir}] {item} ({bytes_to_human_readable(size)})")
            elif path.is_file():
                if path.suffix.lower() in exclude_exts:
                    continue
                size = get_file_size(path)
                icon = FILE_ICONS.get(path.suffix.lower(), FILE_ICONS["default"])
                file_list.append(f"{indent}{icon} [{base_dir}] {item} ({bytes_to_human_readable(size)})")
            else:
                continue
            diff_size[origin] += size
            diff_dir_key = "only_in_dir1" if origin == "dir1" else "only_in_dir2"
            diff_dir[diff_dir_key].append(path.relative_to(base_dir))
        return folder_list, file_list

    def _compare_common_items(d1, d2, common_files, indent):
        folder_list = []
        file_list = []
        for item in common_files:
            item_path1, item_path2 = d1 / item, d2 / item

            # 打印文件夹与文件夹的比较结果
            if item_path1.is_dir() and item_path2.is_dir():
                if item in exclude_dirs:
                    continue
                subfolder_list = _collect_structure_diff(
                    item_path1, item_path2, indent + "    "
                )
                if subfolder_list:
                    folder_list.append(f"{indent}📁 {item}/")
                    folder_list.extend(subfolder_list)

            # 打印文件夹与文件的混合情况
            elif (item_path1.is_file() and item_path2.is_dir()) or (
                item_path1.is_dir() and item_path2.is_file()
            ):
                file_list.append(
                    f"{indent}{item} (one is a file, the other is a folder)"
                )
                diff_dir["different_files"].append(item_path1.relative_to(dir1))

            # 打印文件与文件的比较结果
            elif compare_common_file and item_path1.is_file() and item_path2.is_file():
                if (
                    item_path1.suffix.lower() in exclude_exts
                    or item_path2.suffix.lower() in exclude_exts
                ):
                    continue
                item_path1_size = get_file_size(item_path1)
                item_path2_size = get_file_size(item_path2)
                if item_path1_size != item_path2_size:
                    icon = FILE_ICONS.get(item_path1.suffix.lower(), FILE_ICONS["default"])
                    file_list.append(
                        f"{indent}{icon} [{dir1}] {item} ({bytes_to_human_readable(item_path1_size)})"
                    )
                    file_list.append(
                        f"{indent}{icon} [{dir2}] {item} ({bytes_to_human_readable(item_path2_size)})"
                    )

                    diff_size["dir1"] += item_path1_size
                    diff_size["dir2"] += item_path2_size
                    diff_dir["different_files"].append(item_path1.relative_to(dir1))
        return folder_list, file_list


    dir1 = Path(dir1)
    dir2 = Path(dir2)
    exclude_dirs = exclude_dirs or []
    exclude_exts = exclude_exts or []

    if not dir1.is_dir() or not dir2.is_dir():
        raise ValueError(f"输入路径必须是有效的文件夹: {dir1} 或 {dir2}")

    diff_size = {"dir1": 0, "dir2": 0}
    diff_dir = {"only_in_dir1": [], "only_in_dir2": [], "different_files": []}

    structure_list = _collect_structure_diff(dir1, dir2, "")

    print("\n".join(structure_list))
    print("\n" + format_table(
        [[dir1, bytes_to_human_readable(diff_size['dir1'])],
         [dir2, bytes_to_human_readable(diff_size['dir2'])]],
        column_names=["Directory", "Diff Size"]
    ))

    return diff_dir


def sync_folders(diff: Dict[str, List[Path]], dir1: str, dir2: str, mode: str = "->"):
    """
    根据差异字典同步两个文件夹。

    :param diff: 差异字典
    :param dir1: 第一个文件夹路径
    :param dir2: 第二个文件夹路径
    :param mode: 同步模式，
                 '->' 表示以第一个文件夹为主，
                 '<-' 表示以第二个文件夹为主，
                 '<->' 表示双向同步
    """

    def append_hash_to_filename(file_path: Path):
        """在文件名中添加哈希值标识"""
        hash_value = get_file_hash(file_path)
        name, ext = file_path.stem, file_path.suffix
        new_file_path = file_path.with_name(f"{name}({hash_value}){ext}")
        file_path.rename(new_file_path)
        return new_file_path.name

    dir1 = Path(dir1)
    dir2 = Path(dir2)

    if mode in ["->", "<-"]:
        # 确定主目录和次目录
        is_mode_a = mode == "->"
        main_dir, minor_dir = (dir1, dir2) if is_mode_a else (dir2, dir1)

        # 预计算 diff 访问键
        main_dir_key = "only_in_" + ("dir1" if is_mode_a else "dir2")
        minor_dir_key = "only_in_" + ("dir2" if is_mode_a else "dir1")

        # 差异分配
        main_dir_diff = diff[main_dir_key] + diff["different_files"]
        minor_dir_diff = diff[minor_dir_key]

        delete_manager = DeleteManager(delete_file_or_folder, minor_dir)
        copy_manager = CopyManager(
            copy_file_or_folder, main_dir, minor_dir, copy_mode=mode
        )

        delete_manager.start(minor_dir_diff)
        copy_manager.start(main_dir_diff)

    elif mode == "<->":
        copy_a_to_b_manager = CopyManager(
            copy_file_or_folder, dir1, dir2, copy_mode="->"
        )
        copy_b_to_a_manager = CopyManager(
            copy_file_or_folder, dir2, dir1, copy_mode="<-"
        )

        diff_file_in_dir1 = []
        diff_file_in_dir2 = []
        for rel_path in diff["different_files"]:
            file1 = dir1 / rel_path
            file2 = dir2 / rel_path

            new_file1_name = append_hash_to_filename(file1)
            new_file2_name = append_hash_to_filename(file2)

            diff_file_in_dir1.append(new_file1_name)
            diff_file_in_dir2.append(new_file2_name)

        copy_a_to_b_manager.start(diff["only_in_dir1"] + diff_file_in_dir1)
        copy_b_to_a_manager.start(diff["only_in_dir2"] + diff_file_in_dir2)

    else:
        raise ValueError("无效的模式，必须为 '->', '<-' 或 '<->'")


def delete_file_or_folder(path: Path) -> None:
    """
    删除文件或文件夹。

    :param path: 文件或文件夹路径。
    """
    if path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def copy_file_or_folder(source: Path, target: Path) -> None:
    """
    复制文件或文件夹。

    :param source: 源文件或文件夹路径。
    :param target: 目标文件或文件夹路径。
    """
    if source.is_file():
        shutil.copy2(source, target)
    elif source.is_dir():
        shutil.copytree(source, target, dirs_exist_ok=True)


def get_file_size(file_path: Path) -> int:
    """
    获取文件大小。

    :param file_path: 文件路径。
    :return: 文件大小（字节）。
    """
    return file_path.stat().st_size


def get_folder_size(folder_path: Path | str) -> int:
    """
    计算文件夹的大小（以字节为单位）。
    遍历指定文件夹中的所有文件和子目录，并计算它们的大小总和。

    :param folder_path: 文件夹的路径。
    :return: 文件夹的总大小（以字节为单位）。
    """
    total_size = 0
    folder = Path(folder_path)
    for file in folder.rglob("*"):  # rglob('*') 遍历所有文件和子目录
        if file.is_file():
            total_size += file.stat().st_size  # 获取文件大小
    return total_size


def get_file_hash(file_path: Path, chunk_size: int = 65536) -> str:
    """
    计算文件的哈希值。

    :param file_path: 文件路径。
    :param chunk_size: 读取文件块的大小。
    :return: 文件的哈希值。
    """
    hash_algo = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hash_algo.update(chunk)
    return hash_algo.hexdigest()


def detect_identical_files(
    folder_list: List[Path], execution_mode: str = "thread"
) -> Dict[Tuple[str, int], List[Path]]:
    """
    检测文件夹中是否存在相同内容的文件，并在文件名后添加文件大小。

    :param folder_list: 文件夹路径列表。
    :return: 相同文件的字典，键为文件大小和哈希值，值为文件路径列表。
    """
    scan_size_manager = ScanSizeManager(
        get_file_size,
        execution_mode,
        enable_result_cache=True,
        progress_desc="Scanning file size",
        show_progress=True,
    )
    scan_hash_manager = ScanHashManager(
        get_file_hash,
        execution_mode,
        enable_result_cache=True,
        progress_desc="Calculating file hashes",
        show_progress=True,
    )

    # 根据文件大小进行初步筛选
    file_path_iter = (
        path
        for folder_path in folder_list
        for path in Path(folder_path).rglob("*")
        if path.is_file()
    )
    scan_size_manager.start(file_path_iter)
    file_size_iter = scan_size_manager.process_result_dict()

    # 对于相同大小的文件，进一步计算哈希值, 找出哈希值相同的文件
    scan_hash_manager.start(file_size_iter)
    identical_dict = scan_hash_manager.process_result_dict()

    return identical_dict


def duplicate_files_report(identical_dict: Dict[Tuple[str, int], List[Path]]):
    """
    生成一个详细报告，列出所有重复的文件及其位置。

    :param identical_dict: 相同文件的字典，由 detect_identical_files 函数返回。
    """
    if not identical_dict:
        print("\nNo identical files found.")
        return

    report = []
    total_size = 0
    total_file_num = 0
    max_file_num = 0
    index = 0
    sort_identical_dict = dict(
        sorted(
            identical_dict.items(),
            key=lambda item: item[0][1] * len(item[1]),
            reverse=True,
        )
    )

    report.append("\nIdentical files found:\n")
    for (hash_value, file_size), file_list in sort_identical_dict.items():
        file_num = len(file_list)
        total_size += file_size * file_num
        total_file_num += file_num

        if file_num > max_file_num:
            max_file_num = file_num
            max_file_key = (hash_value, file_size)

        file_readable_size = bytes_to_human_readable(file_size)
        files_readable_size = bytes_to_human_readable(file_size * file_num)
        data = [(str(file), file_readable_size) for file in file_list]
        table_text = format_table(data, column_names=["File", "Size"])

        report.append(f"{index}.Hash: {hash_value} (Size: {files_readable_size})")
        report.append(table_text + "\n")
        index += 1

    hash_value, file_size = max_file_key
    report.append(
        f"Total size of duplicate files: {bytes_to_human_readable(total_size)}"
    )
    report.append(f"Total number of duplicate files: {total_file_num}")
    report.append(
        f"File with the most duplicates: {hash_value}(hash) {bytes_to_human_readable(file_size)}(size) {max_file_num}(number)"
    )

    print("\n".join(report))


def delete_identical_files(identical_dict: Dict[Tuple[str, int], List[Path]]):
    """
    删除文件夹中相同内容的文件。

    :param identical_dict: 相同文件的字典，由 detect_identical_files 函数返回。
    :return: 删除的文件列表。
    """

    def delete_and_return_size(path: Path, size: int):
        path.unlink()
        return size

    delete_list = []
    for (hash_value, file_size), file_list in identical_dict.items():
        delete_list.extend([(file_path, file_size) for file_path in file_list])

    delete_return_size_manager = DeleteReturnSizeManager(
        delete_and_return_size, 
        unpack_task_args=True,
        enable_result_cache=True
    )
    delete_return_size_manager.start(delete_list)
    delete_size = delete_return_size_manager.process_result_dict()

    print(f"\nTotal size of deleted files: {bytes_to_human_readable(delete_size)}")


def move_identical_files(
    identical_dict: Dict[Tuple[str, int], List[Path]],
    target_folder: str | Path,
    size_threshold: int = None,
):
    """
    将相同内容的文件移动到指定的目标文件夹。

    :param identical_dict: 相同文件的字典，由 detect_identical_files 函数返回。
    :param target_folder: 目标文件夹路径。
    :param size_threshold: 文件大小阈值，只有大于此阈值的文件会被移动。如果为 None，则不限制文件大小。
    :return: 移动的文件列表。
    """
    target_folder = Path(target_folder)
    moved_files = {}
    report = []

    for (hash_value, file_size), file_list in tqdm(identical_dict.items()):
        target_subfolder = target_folder / f"{hash_value}({file_size})"
        if not target_subfolder.exists():
            target_subfolder.mkdir(parents=True)

        moved_files[hash_value] = []

        for file in file_list:
            if size_threshold is not None and file_size <= size_threshold:
                continue
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
                moved_files[hash_value].append((file, target_path))
                report.append(f"Moved: {file} -> {target_path}")
            except Exception as e:
                report.append(f"Error moving {file} to {target_path}: {e}")

    print("\n".join(report))

    return moved_files


def folder_to_file_path(
    folder_path: Path, file_extension: str, parent_dir: Path = None
) -> Path:
    """
    将文件夹路径转换为与文件夹同名的文件路径。
    例如，给定文件夹路径 '/home/user/folder1' 和文件扩展名 'txt'，函数会返回文件路径 '/home/user/folder1.txt'。

    :param folder_path: 文件夹的路径。
    :param file_extension: 文件扩展名。
    :param parent_dir: 文件夹的父目录路径，如果为 None，则使用文件夹的父目录。
    :return: 与文件夹同名的文件路径。
    """
    folder_path = Path(folder_path)
    if folder_path.is_file():
        raise ValueError("The provided path is a file, not a folder.")

    # 获取文件夹的父目录和文件夹名称
    folder_path = Path(folder_path)
    folder_name = folder_path.name  # 获取文件夹名称，不带路径
    parent_dir = parent_dir or folder_path.parent  # 获取文件夹的父目录路径

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
    file_path_list = [
        file_path for file_path in folder_path.glob("**/*") if file_path.is_file()
    ]  # 使用glob('**/*')遍历目录中的文件和子目录

    for file in tqdm(file_path_list, desc="Replacing filenames"):
        new_filename = re.sub(pattern, replacement, file.name)
        if new_filename == file.name:
            continue

        new_file_path = file.with_name(new_filename)  # 使用with_name方法生成新文件路径
        if new_file_path.exists():
            continue

        file.rename(new_file_path)  # 重命名文件


def sort_by_number(file_path: Path, special_keywords: dict) -> tuple:
    """
    提取文件路径中的文件夹名称和文件名中的数字，作为排序依据。
    一级排序: 关键字优先级
    二级排序：文件名中的数字
    """
    file_name = file_path.name

    # 关键字优先级控制
    folder_priority = min(
        (
            special_keywords[keyword]
            for keyword in special_keywords
            if keyword in file_name
        ),
        default=0,
    )

    matches = re.findall(r"\d+", file_path.name)
    number = [int(num) for num in matches] if matches else [float("inf")]
    return (folder_priority, *number)


def move_files_with_keyword(
    source_folder: Path | str, keyword: str, target_folder: Path | str
):
    """
    将 source_folder 中所有文件名包含 keyword 的文件移动到 target_folder。

    :param source_folder: 源文件夹路径（str 或 Path）
    :param keyword: 需要匹配的关键词（str）
    :param target_folder: 目标文件夹路径（str 或 Path）
    """
    source = Path(source_folder)
    target = Path(target_folder)

    if not source.exists() or not source.is_dir():
        raise ValueError(f"源文件夹不存在: {source}")

    target.mkdir(parents=True, exist_ok=True)

    moved_count = 0
    for file in source.glob("**/*"):
        if file.is_file() and keyword in file.name:
            shutil.move(str(file), str(target / file.name))
            moved_count += 1

    print(f"已移动 {moved_count} 个文件到 {target}")
