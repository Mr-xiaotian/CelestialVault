import os
import shutil
from PIL import Image
from tqdm import tqdm
from pillow_heif import register_heif_opener

def creat_folder(path: str) -> str:
    """
    判断系统是否存在该路径，没有则创建。
    """
    while True:
        try:
            if not os.path.exists(path):
                os.makedirs(path)
            break
        except FileNotFoundError as e:
            print(e, path)
            path = path[:-1]
            continue
    return path

def get_all_file_paths(directory):
    """
    获取给定目录下所有文件的绝对路径。
    
    :param directory: 要遍历的目录路径。
    :return: 所有文件的绝对路径列表。
    """
    file_paths = []  # 存储文件路径的列表
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)  # 构建文件的绝对路径
            file_paths.append(file_path)  # 添加到列表中

    return file_paths

def compress_fold(folder_path):
    register_heif_opener()
    Image.LOAD_TRUNCATED_IMAGES = True
    Image.MAX_IMAGE_PIXELS = None
    
    # 创建新文件夹
    new_folder_path = os.path.join(os.path.dirname(folder_path), os.path.basename(folder_path) + "_re")
    os.makedirs(new_folder_path, exist_ok=True)
    error_list = []
    img_snuffix = ["jpg", "png", "jpeg", 'heic', 'webp', "JPG", "PNG", "JPEG", "HEIC", "WEBP"] # 'heic', "HEIC"
    video_snuffix = ["mp4", "avi", "mov", "mkv", 'divx', "mpg", "flv", "rm", "rmvb", "mpeg", "wmv", "3gp", "vob", "ogm", "ogv", "asf", 'ts', 'webm',
                     "MP4", "AVI", "MOV", "MKV", 'DIVX', "MPG", "FLV", "RM", "RMVB", "MPEG", "WMV", "3GP", "VOB", "OGM", "OGV", "ASF", "TS", 'WEBM']

    # 遍历文件夹
    for root, dirs, files in tqdm(os.walk(folder_path)):
        for filename in files:
            # 如果是图片
            if filename.split('.')[-1] in img_snuffix:
                old_img_path = os.path.join(root, filename)
                new_img_path = os.path.join(new_folder_path, 
                                            os.path.relpath(old_img_path, folder_path))
                
                # 如果已经存在，则跳过
                if os.path.exists(new_img_path):
                    continue
                os.makedirs(os.path.dirname(new_img_path), exist_ok=True)
                
                try:
                    # 打开图片并压缩
                    img = Image.open(old_img_path)
                    img.save(new_img_path, optimize=True, quality=50)
                except OSError as e:
                    error_list.append((old_img_path,e))
                    shutil.copy(old_img_path, new_img_path)
                    continue
            # 如果是视频
            elif filename.split('.')[-1] in video_snuffix:
                old_video_path = os.path.join(root, filename)
                new_video_path = os.path.join(new_folder_path, 
                                              '_'.join(os.path.relpath(old_video_path, folder_path).split('.')[:-1])).replace('_compressed', '')
                new_video_path += '_compressed.mp4'
                os.makedirs(os.path.dirname(new_video_path), exist_ok=True)
                
                # 如果已经存在，则跳过
                if os.path.exists(new_video_path):
#                     print(new_video_path)
                    continue
                # 如果已经是压缩后的视频，则复制过去
                elif '_compressed.mp4' in filename:
                    shutil.copy(old_video_path, new_video_path)
                    continue
                    
                # 使用ffmpeg压缩视频
                os.system(f'ffmpeg -i "{old_video_path}" -vcodec libx264 -crf 24 "{new_video_path}"')
            # 如果是其他文件，则直接复制
            else:
                old_file_path = os.path.join(root, filename)
                new_file_path = os.path.join(new_folder_path, os.path.relpath(old_file_path, folder_path))
                
                # 如果已经存在，则跳过
                if os.path.exists(new_file_path):
                    continue
                    
                os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
                shutil.copy(old_file_path, new_file_path)

    return error_list
