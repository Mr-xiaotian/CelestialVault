import hashlib
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
from celestialflow import TaskExecutor

from ..constants import IMG_SUFFIXES, VIDEO_SUFFIXES
from ..instances.inst_units import HumanBytes, HumanTimestamp
from .TextTools import format_table


class HandleFileExecutor(TaskExecutor):
    def __init__(
        self,
        func: Callable,
        dir_path: Path,
        new_dir_path: Path,
        rules: Dict[str, Tuple[Callable, Callable]],
        execution_mode: str,
        progress_desc: str,
    ):
        super().__init__(
            func=func,
            execution_mode=execution_mode,
            max_workers=6,
            max_info=100,
            enable_error_cache=True,
            progress_desc=progress_desc,
            show_progress=True,
        )
        self.dir_path = dir_path
        self.new_dir_path = new_dir_path
        self.rules = rules

    def get_args(self, file_path: Path):
        rel_path = file_path.relative_to(self.dir_path)
        new_file_path = self.new_dir_path / rel_path

        file_suffix = file_path.suffix.lower()
        action_func, rename_func, args_extra = self.rules.get(
            file_suffix, (shutil.copy2, lambda x: x, {})
        )

        final_path = rename_func(new_file_path)
        return (file_path, final_path, action_func, args_extra)

    def handle_error_dict(self):
        error_path_dict = defaultdict(list)

        for file_path, error in self.get_error_dict().items():
            rel_path = file_path.relative_to(self.dir_path)
            new_file_path = self.new_dir_path / rel_path
            shutil.copy(file_path, new_file_path)
            error_path_dict[(type(error).__name__, str(error))].append(new_file_path)
        return dict(error_path_dict)


class HandleSubFolderExecutor(HandleFileExecutor):
    def get_args(self, sub_dir_path: Path):
        rel_path = sub_dir_path.relative_to(self.dir_path)
        new_sub_dir_path = self.new_dir_path / rel_path

        action_func, rename_func, args_extra = self.rules.get(
            "dir", (shutil.copy, lambda x: x, {})
        )

        final_path = rename_func(new_sub_dir_path)
        return (sub_dir_path, final_path, action_func, args_extra)

    def handle_error_dict(self):
        error_path_dict = defaultdict(list)

        for file_path, error in self.get_error_dict().items():
            rel_path = file_path.relative_to(self.dir_path)
            new_file_path = self.new_dir_path / rel_path
            # shutil.copy(file_path, new_file_path)
            error_path_dict[(type(error).__name__, str(error))].append(new_file_path)
        return dict(error_path_dict)


class ScanSizeExecutor(TaskExecutor):
    def process_result_dict(self):
        size_dict = defaultdict(list)

        for path, size in self.get_success_dict().items():
            size_dict[size].append(path)

        size_dict = {k: v for k, v in size_dict.items() if len(v) > 1}
        size_iter = (
            (path, size)
            for size, files in size_dict.items()
            for path in files
        )
        return size_iter


class ScanHashExecutor(TaskExecutor):
    def get_args(self, task):
        return (task[0],)

    def process_result_dict(self):
        identical_dict = defaultdict(list)

        for (path, size), hash_value in self.get_success_dict().items():
            identical_dict[(hash_value, size)].append(path)

        identical_dict = {k: v for k, v in identical_dict.items() if len(v) > 1}
        return identical_dict


class DeleteReturnSizeExecutor(TaskExecutor):
    def process_result_dict(self):
        delete_size = 0
        for size in self.get_success_dict().values():
            delete_size += size
        return HumanBytes(delete_size)


def create_dir(path: str | Path) -> Path:
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


def handle_item(
    source: Path,
    destination: Path,
    action: Callable[[Path, Path, Any], Any],
    extra: dict,
):
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


def handle_dir_files(
    dir_path: str | Path,
    rules: Dict[str, Tuple[Callable[[Path, Path, Dict], None], Callable[[Path], Path], Dict]],
    execution_mode: str = "serial",
    progress_desc: str = "Processing files",
    dir_name_suffix: str = "_re",
) -> Dict[Tuple[str, str], List[Path]]:
    """
    遍历指定文件夹，根据文件后缀名对文件进行处理，并将处理后的文件存储到新的目录中。
    不属于指定后缀的文件将被直接复制到新目录中。处理后的文件会保持原始的目录结构。
    如果目标文件已存在，则会跳过处理。处理过程中遇到的任何错误都会被记录并返回。

    :param dir_path: 要处理的文件夹的路径，可以是相对路径或绝对路径。
    :param rules: 一个字典，键为文件后缀，值为处理该类型文件的函数和重命名函数的元组。
    :param execution_mode: 执行模式，可以是 'serial' 或 'thread' 'process'。默认为 'serial'。
    :param progress_desc: 进度条描述。
    :return: 包含因错误未能正确处理的文件及其对应错误信息的列表。每个元素是一个元组，包括文件路径和错误对象。
    """
    dir_path = Path(dir_path)
    new_dir_path = dir_path.parent / (dir_path.name + dir_name_suffix)

    handlefile_executor = HandleFileExecutor(
        func=handle_item,
        dir_path=dir_path,
        new_dir_path=new_dir_path,
        rules=rules,
        execution_mode=execution_mode,
        progress_desc=progress_desc,
    )

    file_path_iter = (
        file_path for file_path in dir_path.glob("**/*") if file_path.is_file()
    )
    handlefile_executor.start(file_path_iter)

    error_path_dict = handlefile_executor.handle_error_dict()
    return error_path_dict


def handle_subdirs(
    dir_path: str | Path,
    rules: Dict[str, Tuple[Callable[[Path, Path, Dict], None], Callable[[Path], Path], Dict]],
    execution_mode: str = "serial",
    progress_desc: str = "Processing dirs",
    dir_name_suffix: str = "_re",
) -> Dict[Tuple[str, str], List[Path]]:
    """
    遍历指定文件夹，根据文件后缀名对文件进行处理，并将处理后的文件存储到新的目录中。
    不属于指定后缀的文件将被直接复制到新目录中。处理后的文件会保持原始的目录结构。
    如果目标文件已存在，则会跳过处理。处理过程中遇到的任何错误都会被记录并返回。

    :param dir_path: 要处理的文件夹的路径，可以是相对路径或绝对路径。
    :param rules: 一个字典，键为文件后缀，值为处理该类型文件的函数和重命名函数的元组。
    :param execution_mode: 执行模式，可以是 'serial' 或 'thread' 'process'。默认为 'serial'。
    :param progress_desc: 进度条描述。
    :return: 包含因错误未能正确处理的文件及其对应错误信息的列表。每个元素是一个元组，包括文件路径和错误对象。
    """
    dir_path = Path(dir_path)
    new_dir_path = dir_path.parent / (dir_path.name + dir_name_suffix)

    handlefile_executor = HandleSubFolderExecutor(
        func=handle_item,
        dir_path=dir_path,
        new_dir_path=new_dir_path,
        rules=rules,
        execution_mode=execution_mode,
        progress_desc=progress_desc,
    )

    sub_dir_list = find_pure_dirs(dir_path, True)
    handlefile_executor.start(sub_dir_list)

    error_path_dict = handlefile_executor.handle_error_dict()
    return error_path_dict


def compress_dir(
    dir_path: str | Path, execution_mode: str = "thread"
) -> List[Tuple[Path, Exception]]:
    """
    遍历指定文件夹，根据文件后缀名对文件进行压缩处理，并将处理后的文件存储到新的目录中。
    支持的文件类型包括图片、视频和PDF。不属于这三种类型的文件将被直接复制到新目录中。
    压缩后的文件会保持原始的目录结构。如果目标文件已存在，则会跳过处理。处理过程中遇到的任何错误都会被记录并返回。

    :param dir_path: 要处理的文件夹的路径，可以是相对路径或绝对路径。
    :param execution_mode: 执行模式，可以是 'serial' 或 'thread' 'process'。默认为 'thread'。
    :return: 包含因错误未能正确处理的文件及其对应错误信息的列表。每个元素是一个元组，包括文件路径和错误对象。
    """

    def rename_mp4(file_path: Path) -> Path:
        name = file_path.stem.replace("_compressed", "")
        suffix = file_path.suffix.lstrip(".")
        new_name = f"{name}_compressed({suffix}).mp4"
        return file_path.with_name(new_name)

    def rename_pdf(file_path: Path) -> Path:
        name = file_path.stem.replace("_compressed", "")
        new_name = f"{name}_compressed.pdf"
        return file_path.with_name(new_name)

    from .ImageProcessing import compress_img
    from .VideoProcessing import compress_video

    # from .DocumentConversion import compress_pdf

    rules = {suffix: (compress_img, lambda x: x, {}) for suffix in IMG_SUFFIXES}
    rules.update(
        {suffix: (compress_video, rename_mp4, {}) for suffix in VIDEO_SUFFIXES}
    )
    # rules.update({'.pdf': (compress_pdf,rename_pdf, {})})

    return handle_dir_files(
        dir_path, rules, execution_mode, progress_desc="Compressing Folder"
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


def unzip_dir(dir_path: str | Path):
    """
    遍历指定文件夹，解压缩所有支持的压缩文件。支持的文件类型包括 zip 和 rar。

    :param dir_path: 要处理的文件夹的路径，可以是相对路径或绝对路径。
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
        ".7z": (unzip_7z_file, rename_unzip, {}),
    }

    return handle_dir_files(dir_path, rules, progress_desc="Unziping dir")


def delete_file_or_dir(path: Path) -> None:
    """
    删除文件或文件夹。

    :param path: 文件或文件夹路径。
    """
    if path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def copy_file_or_dir(source: Path, target: Path) -> None:
    """
    复制文件或文件夹。

    :param source: 源文件或文件夹路径。
    :param target: 目标文件或文件夹路径。
    """
    if source.is_file():
        shutil.copy2(source, target)
    elif source.is_dir():
        shutil.copytree(source, target, dirs_exist_ok=True)


def get_file_size(file_path: Path) -> HumanBytes:
    """
    获取文件大小。

    :param file_path: 文件路径。
    :return: 文件大小（HumanBytes）。
    """
    file_path = Path(file_path)
    return HumanBytes(file_path.stat().st_size)


def get_dir_size(dir_path: Path) -> HumanBytes:
    """
    计算文件夹的大小。
    遍历指定文件夹中的所有文件和子目录，并计算它们的大小总和。

    :param dir_path: 文件夹的路径。
    :return: 文件夹的总大小（HumanBytes）。
    """
    total_size = 0
    dir = Path(dir_path)
    for file in dir.rglob("*"):
        if file.is_file():
            total_size += file.stat().st_size  # 获取文件大小
    return HumanBytes(total_size)


def get_file_hash(
    file_path: Path, algo: str = "sha256", chunk_size: int = 65536
) -> str:
    """
    计算文件的哈希值。

    :param file_path: 文件路径。
    :param algo: 哈希算法名称（如 'md5', 'sha1', 'sha256', 'sha512', 'blake2b' 等）。
    :param chunk_size: 每次读取的文件块大小。
    :return: 文件哈希字符串（十六进制）
    """
    hash_algo = hashlib.new(algo)

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hash_algo.update(chunk)

    return hash_algo.hexdigest()


def get_dir_hash(
    dir_path: Path,
    exclude_dirs: list[str] | None = None,
    exclude_exts: list[str] | None = None,
    algo: str = "sha256",
) -> str:
    """
    计算整个文件夹的哈希值（递归包含子文件）。
    算法规则与 FileNode.hash 一致（目录哈希来自子节点哈希的组合）。

    :param dir_path: 文件夹路径。
    :param exclude_dirs: 要排除的目录名（不含路径）。
    :param exclude_exts: 要排除的文件扩展名（含点，例如 ".tmp"）。
    :param algo: 哈希算法名称，例如 'sha256', 'blake2b' 等。
    :return: 文件夹的哈希字符串。
    """
    exclude_dirs = set(exclude_dirs or [])
    exclude_exts = set(ext.lower() for ext in (exclude_exts or []))

    def _hash_bytes(data: bytes) -> str:
        return hashlib.new(algo, data).hexdigest()

    def _compute(path: Path) -> str:
        """递归计算目录或文件的哈希"""
        # --- 排除目录 ---
        if any(part in exclude_dirs for part in path.parts):
            return ""

        # --- 文件 ---
        if path.is_file():
            if path.suffix.lower() in exclude_exts:
                return ""
            return get_file_hash(path, algo=algo)

        # --- 非存在路径或空目录 ---
        if not path.exists():
            return _hash_bytes(b"[MISSING]")

        # --- 目录：递归计算子项哈希 ---
        child_hashes = []
        for child in sorted(path.iterdir(), key=lambda c: (not c.is_dir(), c.name)):
            h = _compute(child)
            if not h:
                continue
            tag = "D" if child.is_dir() else "F"
            entry = f"{tag}:{child.name}:{h}".encode("utf-8")
            child_hashes.append(entry)

        if not child_hashes:
            combined = b"[EMPTY]"
        else:
            combined = b"".join(child_hashes)

        return _hash_bytes(combined)

    return _compute(Path(dir_path))


def get_file_mtime(file_path: Path) -> HumanTimestamp:
    """
    获取文件的最后修改时间 (mtime)

    :param file_path: 文件路径
    :return: 文件的修改时间戳 (HumanTimestamp)
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return HumanTimestamp(0)
    return HumanTimestamp(file_path.stat().st_mtime)


def get_dir_mtime(dir_path: Path) -> HumanTimestamp:
    """
    获取整个目录及其子项的最大修改时间 (递归)
    即：取目录中所有文件与子目录的 mtime 最大值。

    :param dir_path: 目录路径
    :return: 目录内最新修改时间戳 (HumanTimestamp)
    """
    dir_path = Path(dir_path)
    if not dir_path.exists():
        return HumanTimestamp(0)

    max_mtime = dir_path.stat().st_mtime  # 目录本身的修改时间

    for subpath in dir_path.rglob("*"):
        try:
            stat = subpath.stat()
            if stat.st_mtime > max_mtime:
                max_mtime = stat.st_mtime
        except (PermissionError, FileNotFoundError):
            # 避免因权限或符号链接问题中断
            continue

    return HumanTimestamp(max_mtime)


def detect_identical_files(
    dir_list: List[Path], execution_mode: str = "thread"
) -> Dict[Tuple[str, int], List[Path]]:
    """
    检测文件夹中是否存在相同内容的文件，并在文件名后添加文件大小。

    :param dir_list: 文件夹路径列表。
    :return: 相同文件的字典，键为文件大小和哈希值，值为文件路径列表。
    """
    scan_size_executor = ScanSizeExecutor(
        get_file_size,
        execution_mode,
        enable_success_cache=True,
        progress_desc="Scanning files size",
        show_progress=True,
    )
    scan_hash_executor = ScanHashExecutor(
        get_file_hash,
        execution_mode,
        enable_success_cache=True,
        progress_desc="Calculating files hash",
        show_progress=True,
    )

    # 根据文件大小进行初步筛选
    file_path_iter = (
        path
        for dir_path in dir_list
        for path in Path(dir_path).rglob("*")
        if path.is_file()
    )
    scan_size_executor.start(file_path_iter)
    file_size_iter = scan_size_executor.process_result_dict()

    # 对于相同大小的文件，进一步计算哈希值, 找出哈希值相同的文件
    scan_hash_executor.start(file_size_iter)
    identical_dict = scan_hash_executor.process_result_dict()

    return identical_dict


def detect_identical_dirs(
    dir_list: list[Path], execution_mode: str = "thread"
) -> dict[tuple[str, int], list[Path]]:
    """
    检测文件夹中是否存在相同内容的文件，并在文件名后添加文件大小。

    :param dir_list: 文件夹路径列表。
    :return: 相同文件的字典，键为文件大小和哈希值，值为文件路径列表。
    """
    scan_size_executor = ScanSizeExecutor(
        get_dir_size,
        execution_mode,
        enable_success_cache=True,
        progress_desc="Scanning dirs size",
        show_progress=True,
    )
    scan_hash_executor = ScanHashExecutor(
        get_dir_hash,
        execution_mode,
        enable_success_cache=True,
        progress_desc="Calculating dirs hash",
        show_progress=True,
    )

    # 根据文件夹大小进行初步筛选
    dir_path_list = find_pure_dirs(dir_list)
    scan_size_executor.start(dir_path_list)
    dir_size_iter = scan_size_executor.process_result_dict()

    # 对于相同大小的文件夹，进一步计算哈希值, 找出哈希值相同的文件夹
    scan_hash_executor.start(dir_size_iter)
    identical_dict = scan_hash_executor.process_result_dict()

    return identical_dict


def duplicate_files_report(identical_dict: Dict[Tuple[str, HumanBytes], List[Path]]):
    """
    生成一个详细报告，列出所有重复的文件及其位置。

    :param identical_dict: 相同文件的字典，由 detect_identical_files 函数返回。
    """
    if not identical_dict:
        print("\nNo identical files found.")
        return

    report = []
    total_size = HumanBytes(0)
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

        files_size = file_size * file_num
        data = [(str(file), file_size) for file in file_list]
        table_text = format_table(data, column_names=["File", "Size"])

        report.append(f"{index}.Hash: {hash_value} (Size: {files_size})")
        report.append(table_text + "\n")
        index += 1

    hash_value, file_size = max_file_key
    report.append(f"Total size of duplicate files: {total_size}")
    report.append(f"Total number of duplicate files: {total_file_num}")
    report.append(
        f"File with the most duplicates: {hash_value}(hash) {file_size}(size) {max_file_num}(number)"
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

    delete_return_size_executor = DeleteReturnSizeExecutor(
        delete_and_return_size, unpack_task_args=True, enable_success_cache=True
    )
    delete_return_size_executor.start(delete_list)
    delete_size = delete_return_size_executor.process_result_dict()

    print(f"\nTotal size of deleted files: {delete_size}")


def move_identical_files(
    identical_dict: Dict[Tuple[str, int], List[Path]],
    target_dir: str | Path,
    size_threshold: int = None,
):
    """
    将相同内容的文件移动到指定的目标文件夹。

    :param identical_dict: 相同文件的字典，由 detect_identical_files 函数返回。
    :param target_dir: 目标文件夹路径。
    :param size_threshold: 文件大小阈值，只有大于此阈值的文件会被移动。如果为 None，则不限制文件大小。
    :return: 移动的文件列表。
    """
    target_dir = Path(target_dir)
    moved_files = {}
    report = []

    for (hash_value, file_size), file_list in tqdm(identical_dict.items()):
        target_subdir = target_dir / f"{hash_value}({file_size})"
        if not target_subdir.exists():
            target_subdir.mkdir(parents=True)

        moved_files[hash_value] = []

        for file in file_list:
            if size_threshold is not None and file_size <= size_threshold:
                continue
            target_path = target_subdir / file.name

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


def dir_to_file_path(
    dir_path: Path, file_extension: str, parent_dir: Path = None
) -> Path:
    """
    将文件夹路径转换为与文件夹同名的文件路径。
    例如，给定文件夹路径 '/home/user/dir1' 和文件扩展名 'txt'，函数会返回文件路径 '/home/user/dir1.txt'。

    :param dir_path: 文件夹的路径。
    :param file_extension: 文件扩展名。
    :param parent_dir: 文件夹的父目录路径，如果为 None，则使用文件夹的父目录。
    :return: 与文件夹同名的文件路径。
    """
    dir_path = Path(dir_path)
    if dir_path.is_file():
        raise ValueError("The provided path is a file, not a dir.")

    # 获取文件夹的父目录和文件夹名称
    dir_path = Path(dir_path)
    dir_name = dir_path.name  # 获取文件夹名称，不带路径
    parent_dir = parent_dir or dir_path.parent  # 获取文件夹的父目录路径

    # 生成与文件夹同名的文件路径
    file_name = f"{dir_name}.{file_extension}"
    file_path = parent_dir / file_name

    return file_path


def replace_filenames(dir_path: Path | str, pattern: str, replacement: str):
    """
    使用正则表达式替换文件夹中所有文件名中的匹配部分。
    遍历指定文件夹，将其中每个文件的文件名中的匹配内容替换为 `replacement`。

    :param dir_path: 文件夹的路径。
    :param pattern: 用于匹配文件名的正则表达式。
    :param replacement: 替换后的新内容。
    """
    dir_path = Path(dir_path)  # 将传入的路径转换为Path对象
    file_path_list = [
        file_path for file_path in dir_path.glob("**/*") if file_path.is_file()
    ]  # 使用glob('**/*')遍历目录中的文件和子目录

    for file in tqdm(file_path_list, desc="Replacing filenames"):
        new_filename = re.sub(pattern, replacement, file.name)
        if new_filename == file.name:
            continue

        new_file_path = file.with_name(new_filename)  # 使用with_name方法生成新文件路径
        if new_file_path.exists():
            continue

        file.rename(new_file_path)  # 重命名文件


def split_text_and_number(s: str, special_keywords: Dict[str, int]) -> Tuple:
    """
    将路径部分中的文本与数字交替提取，同时根据关键词设置优先级。
    例如，"a1bbb2ccc3" -> (keyword_priority, "a", 1, "bbb", 2, "ccc", 3)

    :param s: 要处理的字符串。
    :param special_keywords: 关键词与其优先级的字典。
    :return: 包含关键词优先级、文本和数字交替的元组。
    """
    # 提取文本和数字部分
    parts = re.findall(r'([a-zA-Z]+|\d+)', s)
    result = []
    
    # 提取关键字优先级
    keyword_priority = min(
        (special_keywords[keyword] for keyword in special_keywords if keyword in s),
        default=float('inf')  # 默认无关键词时优先级为无穷大
    )
    
    result.append(keyword_priority)
    
    # 将文本和数字交替放入结果列表
    for part in parts:
        if part.isdigit():
            result.append(int(part))  # 如果是数字部分，转换为整数
        else:
            result.append(part)  # 如果是文本部分，直接保留文本
    
    return tuple(result)


def sort_by_number(file_path: Path, special_keywords: Dict[str, int]) -> Tuple:
    """
    文件排序规则：
    1. 按路径中的每一层（包括文件名）进行文本与数字交替排序，同时考虑关键词优先级。
    2. 文件名中按关键字优先级和数字进行排序。

    :param file_path: 要排序的文件路径。
    :param special_keywords: 关键词与其优先级的字典。
    :return: 用于排序的元组。
    """
    # 处理路径中的每一层（包括文件名）
    path_parts = [split_text_and_number(part, special_keywords) for part in file_path.parts]
    
    # 处理文件名部分：最后一个部分是文件名
    file_name = file_path.name
    file_name_parts = split_text_and_number(file_name, special_keywords)
    
    return (*path_parts, *file_name_parts)


def move_files_with_keyword(
    source_dir: Path | str, target_dir: Path | str, keyword: str = None
):
    """
    将 source_dir 中所有文件名包含 keyword 的文件移动到 target_dir。

    :param source_dir: 源文件夹路径（str 或 Path）
    :param target_dir: 目标文件夹路径（str 或 Path）
    :param keyword: 需要匹配的关键词（str）
    """
    source = Path(source_dir).resolve()
    target = Path(target_dir).resolve()
    keyword = keyword or ""

    # 源路径检查
    if not source.exists() or not source.is_dir():
        raise ValueError(f"源目录不存在或不是文件夹: {source}")

    # 确保目标路径存在
    target.mkdir(parents=True, exist_ok=True)

    count_moved = 0
    count_skipped = 0

    for file in source.rglob("*"):
        if file.is_file() and (keyword in file.name):
            target_path = target / file.name  # ✅ 不要修改 target 本身
            if target_path == file:
                print(f"⚠️ 跳过自身移动: {file}")
                count_skipped += 1
                continue
            elif target_path.exists():
                print(f"⚠️ 跳过同名文件: {target_path.name}")
                count_skipped += 1
                continue
            try:
                shutil.move(str(file), str(target_path))
                print(f"✅ 移动: {file} -> {target_path}")
                count_moved += 1
            except Exception as e:
                print(f"❌ 移动失败 {file}: {e}")

    print(f"\n📦 完成：移动 {count_moved} 个文件，跳过 {count_skipped} 个同名文件。")


def extract_dir_numbers(dir_path: Path | str) -> set:
    """
    遍历给定文件夹，提取所有文件夹名称中匹配*(\d+)的数字部分，返回字典 {文件夹名: 数字(str)}。

    :param dir_path: 文件夹路径（str 或 Path）
    :return: 字典，包含文件夹名称和对应的数字部分。
    """
    num_set = set()
    pattern = re.compile("\((\d+)\)")

    path = Path(dir_path)
    path_list = list(path.iterdir())
    for item in tqdm(path_list, desc="extract_dir_numbers"):
        if item.is_dir():
            match = pattern.search(item.name)
            if match:
                num_set.add(match.group(1))

    return num_set


def extract_file_numbers(dir_path: Path | str, suffix: str) -> set:
    """
    遍历给定文件夹，提取所有文件名中匹配*(\d+)的数字部分，返回字典 {文件夹名: 数字(str)}。

    :param dir_path: 文件夹路径（str 或 Path）
    :param suffix: 文件后缀名
    :return: 字典，包含文件夹名称和对应的数字部分。
    """
    num_set = set()
    pattern = re.compile("\((\d+)\)")

    path = Path(dir_path)
    path_list = list(path.iterdir())
    for item in tqdm(path_list, desc="extract_txt_numbers"):
        if item.is_file() and item.suffix.lower() == suffix.lower():
            match = pattern.search(item.name)
            if match:
                num_set.add(match.group(1))

    return num_set


def find_pure_dirs(root: str | Path, only_nonempty: bool = False) -> list[Path]:
    """
    查找指定路径下所有的“纯粹文件夹”，即只包含文件而不包含子文件夹的文件夹。

    :param root: 根目录路径
    :param only_nonempty: 是否只返回至少包含一个文件的纯粹文件夹
    :return: 纯粹文件夹的 Path 列表
    """
    root = Path(root)
    pure_dirs = []

    for dir in root.rglob("*"):
        if dir.is_dir():
            subdirs = [p for p in dir.iterdir() if p.is_dir()]
            if not subdirs:  # 没有子文件夹
                files = [p for p in dir.iterdir() if p.is_file()]
                if only_nonempty:
                    if files:
                        pure_dirs.append(dir)
                else:
                    pure_dirs.append(dir)

    return pure_dirs


def align_width(s: str, max_len: int) -> str:
    """
    将字符串 s 左对齐到最大长度 max_len，如果需要则添加空格。

    :param s: 输入字符串
    :param max_len: 最大长度
    :return: 左对齐后的字符串
    """
    adjust = wcswidth(s) - len(s)
    width = max(max_len - adjust, 0)  # 确保非负
    return f"{s:<{width}}"


def append_hash_to_filename(file_path: Path) -> Path:
    """
    在文件名中添加哈希值标识

    :param file_path: 文件路径
    :return: 新文件路径
    """
    hash_value = get_file_hash(file_path)
    name, ext = file_path.stem, file_path.suffix
    new_file_path = file_path.with_name(f"{name}({hash_value}){ext}")
    file_path.rename(new_file_path)

    return new_file_path
