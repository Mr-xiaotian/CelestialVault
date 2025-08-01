import base64
import io
import math
from colorsys import hsv_to_rgb
from itertools import product
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from pillow_heif import register_heif_opener
from skimage.metrics import structural_similarity as compare_ssim
from tqdm import tqdm


def compress_img(old_img_path: str | Path, new_img_path: str | Path):
    register_heif_opener()
    Image.LOAD_TRUNCATED_IMAGES = True
    Image.MAX_IMAGE_PIXELS = None

    # 打开图片并压缩
    img = Image.open(old_img_path)
    img.save(new_img_path, optimize=True, quality=75)


def combine_imgs_to_pdf(
    root_path: str | Path, pdf_path: str | Path = None, special_keywords: dict = None
):
    """
    将指定文件夹中的JPEG图片组合成单个PDF文件。

    :param root_path: 包含JPEG图片的文件夹路径。
    :param pdf_path: 输出的PDF文件路径。
    :return: None
    """
    from ..constants import IMG_SUFFIXES
    from .FileOperations import folder_to_file_path, sort_by_number

    # 转换路径为 Path 对象
    root_path = Path(root_path)
    pdf_path = (
        folder_to_file_path(root_path, "pdf") if pdf_path is None else Path(pdf_path)
    )
    special_keywords = special_keywords or {}

    if not root_path.is_dir():
        raise ValueError(f"The provided image path {root_path} is not a directory.")

    # 使用 rglob 查找所有图片路径
    image_paths = [p for p in root_path.rglob("*") if p.suffix in IMG_SUFFIXES]
    image_paths = sorted(
        image_paths, key=lambda path: sort_by_number(path, special_keywords)
    )  # 按文件名中的数字排序

    if not image_paths:
        raise ValueError(
            f"No images found in {root_path} with suffixes: \n{IMG_SUFFIXES}"
        )

    # 找到最大宽度的图片
    max_width = max(img.size[0] for img in (Image.open(p) for p in image_paths))

    # 生成器函数：逐步处理图片，调整宽度
    def generate_resized_images():
        for img_path in tqdm(image_paths, desc=f"Combining '{root_path.name}'"):
            img = Image.open(img_path).convert("RGB")
            width, height = img.size
            if width != max_width:
                new_height = int(max_width * height / width)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            yield img

    # 保存第一张图片，并附加后续图片到 PDF
    resized_images = generate_resized_images()  # 生成其余的图片
    first_image = next(resized_images)  # 获取第一张图片

    first_image.save(pdf_path, save_all=True, append_images=resized_images)


def combine_imgs_folder(folder_path: Path, special_keywords: dict = None):
    """
    将指定文件夹中的JPEG图片组合成单个PDF文件。

    :param folder_path: 包含JPEG图片的文件夹路径。
    :param special_keywords: 特殊关键词，用于排序图片。eg: {'番外': 1, '特典': 1, '原画': 2}
    :return: None
    """
    from .FileOperations import folder_to_file_path

    folder_path = Path(folder_path)
    subfolders = [f for f in sorted(folder_path.iterdir()) if f.is_dir()]

    new_folder_path = folder_path.parent / (folder_path.name + "_img2pdf")
    new_folder_path.mkdir(exist_ok=True)

    for subfolder in subfolders:
        pdf_path = folder_to_file_path(subfolder, "pdf", parent_dir=new_folder_path)
        if pdf_path.exists():
            print(f"PDF already exists for {subfolder.name}. Skipping...")
            continue
        combine_imgs_to_pdf(subfolder, pdf_path, special_keywords)


def img_to_binary(img: Image.Image) -> bytes:
    """
    将Image对象转换为二进制数据。
    """
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    binary_img = buffered.getvalue()
    return binary_img


def binary_to_img(binary_img: bytes) -> Image.Image:
    """
    将二进制数据转换为Image对象
    """
    img = Image.open(io.BytesIO(binary_img))
    return img


def base64_to_img(base64_str: str) -> Image.Image:
    # 将Base64文本解码回二进制数据
    binary_data = base64.b64decode(base64_str)

    # 将二进制数据转换为Image对象
    img = binary_to_img(binary_data)

    return img


def img_to_base64(img: Image.Image) -> str:
    # 将Image数据转换为二进制数据
    binary_data = img_to_binary(img)

    # 将二进制数据编码成Base64文本
    encoded_text = base64.b64encode(binary_data).decode("utf-8")

    return encoded_text


def generate_palette(color_num: int=256, style: str="morandi", mode: str="random", random_seed: int=0) -> List[int]:
    """
    生成调色板，支持均匀和螺旋两种模式，并确保颜色唯一或规律分布。

    :param color_num: 要生成的颜色数量
    :param style: 调色板风格，可选 'morandi', 'grey', 'hawaiian', 'deepsea', 'twilight', 'sunrise', 'cyberpunk', 'autumn'，默认为 'morandi'
    :param mode: 颜色生成模式，可选 'random' 'uniform', 'spiral'
    :param random_seed: 随机种子，用于生成可重复的随机颜色
    :return: 返回生成的颜色列表
    """

    def select_random_range(range_tuple):
        """
        根据输入的范围元组返回一个随机选择的范围。
        如果元组的长度为2的倍数，随机选择其中的一个二元区间。

        :param range_tuple: 任意长度为2的倍数的元组。
        :return: 返回选中的二元元组。
        """
        # 确保元组长度为2的倍数
        if len(range_tuple) % 2 != 0:
            raise ValueError("Input tuple length must be a multiple of 2.")

        # 将元组分解为多个二元组
        ranges = [
            (range_tuple[i], range_tuple[i + 1]) for i in range(0, len(range_tuple), 2)
        ]

        # 随机选择一个二元组并返回
        selected_range = ranges[np.random.randint(0, len(ranges))]
        return selected_range

    def random_mode(hue_range, saturation_range, value_range, index):
        # 实现随机模式
        while True:
            h = np.random.uniform(*hue_range)
            s = np.random.uniform(*saturation_range)
            v = np.random.uniform(*value_range)
            if (h, s, v) not in used_hsv:
                used_hsv.add((h, s, v))
                return h, s, v

    def uniform_mode(hue_range, saturation_range, value_range, index):
        # 实现均匀模式
        h = hue_range[0] + (hue_range[1] - hue_range[0]) * (index / color_num)
        s = np.mean(saturation_range)  # 使用饱和度的平均值
        v = np.mean(value_range)  # 使用亮度的平均值
        return h, s, v

    def spiral_mode(hue_range, saturation_range, value_range, index):
        # 实现螺旋模式
        h = hue_range[0] + (hue_range[1] - hue_range[0]) * (index / color_num)
        s = saturation_range[0] + (saturation_range[1] - saturation_range[0]) * (
            np.sin(index / color_num * 2 * np.pi) / 2 + 0.5
        )
        v = value_range[0] + (value_range[1] - value_range[0]) * (
            np.cos(index / color_num * 2 * np.pi) / 2 + 0.5
        )
        return h, s, v

    from ..constants import style_params

    if style not in style_params:
        raise ValueError("Unsupported style")
    if mode not in ["random", "uniform", "spiral"]:
        raise ValueError("Unsupported mode")

    params = style_params[style]
    np.random.seed(random_seed)

    get_hsv = None
    mode_dict = {"random": random_mode, "uniform": uniform_mode, "spiral": spiral_mode}
    get_hsv = mode_dict[mode]

    colors = []
    used_hsv = set()
    for i in range(color_num):
        hue_range = select_random_range(params["hue_range"])
        saturation_range = select_random_range(params["saturation_range"])
        value_range = select_random_range(params["value_range"])

        h, s, v = get_hsv(hue_range, saturation_range, value_range, i)
        r, g, b = hsv_to_rgb(h, s, v)
        color = (int(r * 255), int(g * 255), int(b * 255))
        colors.append(color)

    return [value for color in colors for value in color]


def display_palette(palette: List[int], block_size: int=1):
    """
    展示调色板。

    :param palette: 一个包含 RGB 颜色的平铺列表或元组，形如 [r, g, b, r, g, b, ...]
    :param block_size: 每个颜色块的大小，默认为1
    """

    def rgb_to_hex(r, g, b):
        return "#%02x%02x%02x" % (r, g, b)

    total_colors = len(palette) // 3  # 计算颜色的数量

    n_cols = math.ceil(math.sqrt(total_colors))
    n_rows = math.ceil(total_colors / n_cols)

    # 调整图像大小以适应颜色块
    fig, ax = plt.subplots(figsize=(n_cols * block_size, n_rows * block_size))

    # 设置坐标轴的范围与颜色块的数量完全匹配
    ax.set_xlim(0, n_cols)
    ax.set_ylim(0, n_rows)

    # 关闭坐标轴
    ax.axis("off")

    for i in range(total_colors):
        r, g, b = palette[3 * i], palette[3 * i + 1], palette[3 * i + 2]
        hex_color = rgb_to_hex(r, g, b)
        ax.add_patch(
            plt.Rectangle(
                (i % n_cols, n_rows - 1 - i // n_cols),
                block_size,
                block_size,
                color=hex_color,
                linewidth=0,
            )
        )

    plt.show()


def expand_image(image: Image.Image, n: int = 50) -> Image.Image:
    """
    将图像中的每个像素点扩大为n x n的块
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")

    new_width = image.width * n
    new_height = image.height * n

    # 直接使用resize方法来扩展图像
    expanded_image = image.resize((new_width, new_height), Image.NEAREST)

    return expanded_image


def restore_expanded_image(expanded_image: Image.Image, n: int) -> Image.Image:
    """
    将扩展后的图像恢复为原始大小
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")

    width = expanded_image.width // n
    height = expanded_image.height // n

    # 使用resize方法还原图像
    restored_image = expanded_image.resize((width, height), Image.NEAREST)

    return restored_image


def extract_pixels_as_gif(image: Image.Image, frame_size=200, duration=100, loop=0):
    """
    将每个像素点提取出来作为GIF中的一帧。

    :param image: 要处理的图像。如果是调色板图像（P模式），将其转换为RGB模式。
    :param frame_size: 每帧图像的大小。
    :param duration: 每帧显示的持续时间（毫秒）。
    :param loop: GIF循环的次数，0表示无限循环。
    """
    # 如果图像是P模式（调色板图像），转换为RGB模式
    if image.mode == "P":
        image = image.convert("RGB")

    width, height = image.size

    # 准备保存GIF的帧列表
    frames = []
    progress_bar = tqdm(total=height * width, desc="Extract Pixels:")

    # 提取每个像素点并生成每帧图像
    for y, x in product(range(height), range(width)):
        pixel = image.getpixel((x, y))
        frame = Image.new(image.mode, (frame_size, frame_size), color=pixel)
        frames.append(frame)
        progress_bar.update(1)

    progress_bar.close()

    # 将帧保存到一个BytesIO对象中
    gif_io = io.BytesIO()
    frames[0].save(
        gif_io,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=loop,
    )

    gif_io.seek(0)
    return gif_io


def compare_images_by_ssim(folder1: Path | str, folder2: Path | str) -> pd.DataFrame:
    """
    比较两个文件夹中的图像，计算它们的 SSIM 值，并返回一个包含文件名和 SSIM 值的 DataFrame。

    :param folder1: 第一个文件夹的路径。
    :param folder2: 第二个文件夹的路径。
    :return: 包含文件名和 SSIM 值的 DataFrame。
    """
    data = []
    folder1 = Path(folder1)
    folder2 = Path(folder2)

    file_path_list = [
        file_path
        for file_path in folder1.glob("**/*")
        if file_path.is_file() and file_path.suffix.lower() in [".jpg", ".jpeg", ".png"]
    ]

    # 遍历 folder1 文件夹中的所有文件
    for file1 in tqdm(file_path_list, desc="Comparing Images:"):
        file2 = folder2 / file1.name  # 获取对应文件夹中的同名文件
        if not file2.exists() or not file2.is_file():  # 如果文件存在且是文件
            continue

        img1 = Image.open(file1)
        img2 = Image.open(file2)

        # 将图像大小调整为 256x256
        img1 = img1.resize((256, 256))
        img2 = img2.resize((256, 256))

        # 如果是灰度图像，将其转换为 RGB 图像
        if img1.mode != "RGB":
            img1 = img1.convert("RGB")
        if img2.mode != "RGB":
            img2 = img2.convert("RGB")

        img1 = np.array(img1)
        img2 = np.array(img2)

        # 计算 SSIM 值
        ssim = compare_ssim(img1, img2, multichannel=True, win_size=21, channel_axis=2)

        # 将文件名和 SSIM 值添加到数据列表中
        data.append([file1.name, ssim])

    # 返回包含图像名称和 SSIM 值的 DataFrame
    df = pd.DataFrame(data, columns=["Image Name", "SSIM"])
    return df
