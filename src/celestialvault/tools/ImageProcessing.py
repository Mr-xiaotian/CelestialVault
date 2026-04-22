import base64
import io
import math
import random
from colorsys import hsv_to_rgb
from itertools import product
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from celestialflow import TaskExecutor
from PIL import Image, ImageFile, PngImagePlugin
from pillow_heif import register_heif_opener
from tqdm import tqdm

from ..constants import IMAGE_SUFFIX_TO_FORMAT

ImageFile.LOAD_TRUNCATED_IMAGES = True  # 允许加载截断的图片


class CompareSSIMExecutor(TaskExecutor):
    """SSIM 比较执行器，批量计算图像对的结构相似性并汇总结果。"""

    pass


def compress_img(old_img_path: str | Path, new_img_path: str | Path):
    """
    压缩图片，使用 optimize 和 quality=75 进行有损压缩。

    :param old_img_path: 原始图片文件路径。
    :param new_img_path: 压缩后图片文件路径。
    """
    register_heif_opener()
    Image.LOAD_TRUNCATED_IMAGES = True
    Image.MAX_IMAGE_PIXELS = None

    # 打开图片并压缩
    img = Image.open(old_img_path)
    img.save(new_img_path, optimize=True, quality=75)


def safe_open_image(path: Path) -> tuple[Image.Image | None, bool]:
    """
    安全地打开一张图片并返回Image对象，先验证再加载进内存。

    :param path: 图片文件路径。
    :return: 元组 (Image对象或None, 是否成功)。
    """
    try:
        # 第一次只验证，不保留句柄
        with Image.open(path) as img:
            img.verify()

        # 再打开一次时立即加载进内存，然后关闭底层文件句柄
        img = Image.open(path)
        img.load()  # ✅ 读取进内存后不再依赖文件句柄
        return img, True
    except Exception:
        return None, False


def combine_imgs_to_pdf(
    root_path: str | Path, pdf_path: str | Path = None, special_keywords: dict = None
):
    """
    将指定文件夹中的JPEG图片组合成单个PDF文件。

    :param root_path: 包含JPEG图片的文件夹路径。
    :param pdf_path: 输出的PDF文件路径。
    :param special_keywords: 特殊关键词，用于排序图片。eg: {'番外': 1, '特典': 1, '原画': 2}
    """
    from ..constants import IMG_SUFFIXES
    from .FileOperations import dir_to_file_path, sort_by_number

    # 转换路径为 Path 对象
    root_path = Path(root_path)
    pdf_path = (
        dir_to_file_path(root_path, "pdf") if pdf_path is None else Path(pdf_path)
    )
    special_keywords = special_keywords or {}

    if not root_path.is_dir():
        raise ValueError(f"The provided image path {root_path} is not a directory.")

    # 使用 rglob 查找所有图片路径
    image_paths = [p for p in root_path.glob("*") if p.suffix.lower() in IMG_SUFFIXES]
    image_paths = sorted(
        image_paths, key=lambda path: sort_by_number(path, special_keywords)
    )  # 按文件名中的数字排序

    # 安全打开图片，过滤掉损坏的
    valid_images: list[Image.Image] = []
    damage_images: list[Path] = []
    for p in image_paths:
        img, ok = safe_open_image(p)
        if ok:
            valid_images.append(img)
        else:
            damage_images.append(p)

    if not valid_images:
        raise ValueError(f"No valid images could be opened in {root_path}.")

    # 找到最大宽度
    max_width = max(img.size[0] for img in valid_images)

    def generate_resized_images():
        for img in valid_images:
            img = img.convert("RGB")
            width, height = img.size
            if width != max_width:
                new_height = int(max_width * height / width)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            yield img

    resized_images = generate_resized_images()
    first_image = next(resized_images)

    # 保存PDF
    first_image.save(pdf_path, save_all=True, append_images=list(resized_images))

    if damage_images:
        raise ValueError(f"Some images are damaged: {damage_images}")


def combine_imgs_dir(dir_path: Path, special_keywords: dict = None):
    """
    将指定文件夹中的JPEG图片组合成单个PDF文件。

    :param dir_path: 包含JPEG图片的文件夹路径。
    :param special_keywords: 特殊关键词，用于排序图片。eg: {'番外': 1, '特典': 1, '原画': 2}
    """

    def rename_pdf(file_path: Path) -> Path:
        return dir_to_file_path(file_path, "pdf")

    from .FileOperations import dir_to_file_path, handle_subdirs

    rules = {
        "dir": (
            combine_imgs_to_pdf,
            rename_pdf,
            {"special_keywords": special_keywords},
        ),
    }

    return handle_subdirs(
        dir_path,
        rules,
        execution_mode="serial",
        progress_desc="Combine Img Folders",
        dir_name_suffix="_img2pdf",
    )


def img_to_binary(img: Image.Image) -> bytes:
    """
    将Image对象转换为PNG格式的二进制数据。

    :param img: PIL Image 对象。
    :return: PNG格式的二进制数据。
    """
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    binary_img = buffered.getvalue()
    return binary_img


def binary_to_img(binary_img: bytes) -> Image.Image:
    """
    将二进制数据转换为Image对象。

    :param binary_img: 图片的二进制数据。
    :return: PIL Image 对象。
    """
    img = Image.open(io.BytesIO(binary_img))
    return img


def convert_img_format(img: Image.Image, img_format: str) -> Image.Image:
    """
    将 Image 对象转换为指定格式，并返回转换后的 Image 对象。

    :param img: PIL Image 对象。
    :param img_format: 目标图片格式或后缀，如 PNG、JPEG、WEBP、.jpg。
    :return: 转换格式后的 Image 对象。
    """
    img_format = img_format.strip()
    suffix = img_format.lower()
    suffix = suffix if suffix.startswith(".") else f".{suffix}"
    img_format = IMAGE_SUFFIX_TO_FORMAT.get(suffix, img_format.upper())

    save_img = img
    if img_format == "JPEG" and img.mode in {"RGBA", "LA", "P"}:
        save_img = img.convert("RGB")

    buffer = io.BytesIO()
    save_img.save(buffer, format=img_format)
    buffer.seek(0)

    converted_img = Image.open(buffer)
    converted_img.load()
    return converted_img


def base64_to_img(base64_str: str) -> Image.Image:
    """
    将 Base64 编码的字符串解码并转换为 PIL Image 对象。

    :param base64_str: Base64 编码的图片字符串。
    :return: 解码后的 PIL Image 对象。
    """
    # 将Base64文本解码回二进制数据
    binary_data = base64.b64decode(base64_str)

    # 将二进制数据转换为Image对象
    img = binary_to_img(binary_data)

    return img


def img_to_base64(img: Image.Image) -> str:
    """
    将 PIL Image 对象转换为 Base64 编码的字符串。

    :param img: PIL Image 对象。
    :return: Base64 编码的字符串。
    """
    # 将Image数据转换为二进制数据
    binary_data = img_to_binary(img)

    # 将二进制数据编码成Base64文本
    encoded_text = base64.b64encode(binary_data).decode("utf-8")

    return encoded_text


def generate_palette(
    color_num: int = 256,
    style: str = "morandi",
    mode: str = "random",
    random_seed: int = 0,
) -> list[int]:
    """
    生成调色板，支持随机 均匀和螺旋三种模式，并确保颜色唯一或规律分布。

    :param color_num: 要生成的颜色数量
    :param style: 调色板风格，可选 'morandi', 'grey', 'hawaiian', 'deepsea', 'twilight', 'sunrise', 'cyberpunk', 'autumn'等
    :param mode: 颜色生成模式，可选 'random' 'uniform', 'spiral'
    :param random_seed: 随机种子，用于生成可重复的随机颜色
    :return: 返回生成的颜色列表
    """

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

    mode_dict = {"random": random_mode, "uniform": uniform_mode, "spiral": spiral_mode}

    if style not in style_params:
        raise ValueError("Unsupported style")
    if mode not in ["random", "uniform", "spiral"]:
        raise ValueError("Unsupported mode")

    np.random.seed(random_seed)
    get_hsv = mode_dict[mode]

    regions = style_params[style]
    if not isinstance(regions, list):
        raise TypeError(f"Style '{style}' should be a list of color region dicts.")

    colors = []
    used_hsv = set()
    for i in range(color_num):
        # 随机选一个色域
        region = random.choices(regions, weights=[r.get("weight", 1) for r in regions])[
            0
        ]
        hue_range = region["hue_range"]
        sat_range = region["saturation_range"]
        val_range = region["value_range"]

        h, s, v = get_hsv(hue_range, sat_range, val_range, i)
        r, g, b = hsv_to_rgb(h, s, v)
        colors.append((int(r * 255), int(g * 255), int(b * 255)))

    return [value for color in colors for value in color]


def palette_to_image(palette, block_size=50):
    """
    根据颜色列表生成调色板图像。

    :param palette: 一个包含 RGB 颜色的平铺列表或元组，例如 [r, g, b, r, g, b, ...]
    :param block_size: 每个颜色块的像素大小，默认 50
    :return: 生成的调色板图像。
    """
    total_colors = len(palette) // 3  # 颜色数量

    n_cols = math.ceil(math.sqrt(total_colors))
    n_rows = math.ceil(total_colors / n_cols)

    # 创建图像
    logical_img = Image.new("RGB", (n_cols, n_rows))
    pixels = logical_img.load()

    for i in range(total_colors):
        r, g, b = palette[3 * i], palette[3 * i + 1], palette[3 * i + 2]
        col = i % n_cols
        row = i // n_cols

        pixels[col, row] = (r, g, b)

    return expand_image(logical_img, block_size)


def expand_image(image: Image.Image, expand_factor: int = 50) -> Image.Image:
    """
    将图像中的每个像素点扩大为n x n的块

    :param image: 要处理的图像。如果是调色板图像（P模式），将其转换为RGB模式。
    :param expand_factor: 扩展因子，默认 50。
    :return: 扩展后的图像。
    """
    if expand_factor <= 0:
        raise ValueError("n must be a positive integer")
    elif expand_factor == 1:
        return image

    new_width = image.width * expand_factor
    new_height = image.height * expand_factor

    # 直接使用resize方法来扩展图像
    expanded_image = image.resize((new_width, new_height), Image.NEAREST)

    return expanded_image


def restore_expanded_image(
    expanded_image: Image.Image, expand_factor: int = 50
) -> Image.Image:
    """
    将扩展后的图像恢复为原始大小

    :param expanded_image: 要恢复的扩展图像
    :param expand_factor: 扩展因子，默认为50
    :return: 恢复后的原始大小图像。
    """
    if expand_factor <= 0:
        raise ValueError("expand_factor must be a positive integer")
    elif expand_factor == 1:
        return expanded_image

    if (
        expanded_image.width % expand_factor != 0
        or expanded_image.height % expand_factor != 0
    ):
        raise ValueError("Expanded image dimensions must be divisible by n.")

    arr = np.array(expanded_image)
    h, w = arr.shape[:2]
    new_h, new_w = h // expand_factor, w // expand_factor

    if arr.ndim == 3:
        restored = np.zeros((new_h, new_w, arr.shape[2]), dtype=arr.dtype)
    else:
        restored = np.zeros((new_h, new_w), dtype=arr.dtype)

    for i in range(new_h):
        for j in range(new_w):
            block = arr[
                i * expand_factor : (i + 1) * expand_factor,
                j * expand_factor : (j + 1) * expand_factor,
            ]
            # 统计最多出现的颜色（即众数）
            flat_block = block.reshape(-1, block.shape[-1] if block.ndim == 3 else 1)
            pixels, counts = np.unique(flat_block, axis=0, return_counts=True)
            restored[i, j] = pixels[counts.argmax()]

    restored_image = Image.fromarray(restored.squeeze().astype(np.uint8))
    restored_image = restored_image.convert(expanded_image.mode)
    (
        restored_image.putpalette(expanded_image.getpalette())
        if expanded_image.mode == "P"
        else None
    )

    return restored_image


def extract_pixels_as_gif(image: Image.Image, frame_size=200, duration=100, loop=0):
    """
    将每个像素点提取出来作为GIF中的一帧。

    :param image: 要处理的图像。如果是调色板图像（P模式），将其转换为RGB模式。
    :param frame_size: 每帧图像的大小。
    :param duration: 每帧显示的持续时间（毫秒）。
    :param loop: GIF循环的次数，0表示无限循环。
    :return: 包含GIF数据的 BytesIO 对象。
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


def compare_ssim_by_path(path1: Path | str, path2: Path | str) -> float:
    """
    比较两张图像的结构相似性指数（SSIM）。

    :param path1: 第一张图像的路径。
    :param path2: 第二张图像的路径。
    :return: 两张图像的SSIM值，范围在-1到1之间，值越大表示越相似。
    """
    from skimage.metrics import structural_similarity as compare_ssim

    img1 = Image.open(path1)
    img2 = Image.open(path2)

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
    return ssim


def compare_images_by_ssim(dir1: Path | str, dir2: Path | str) -> pd.DataFrame:
    """
    比较两个文件夹中的图像，计算它们的 SSIM 值，并返回一个包含文件名和 SSIM 值的 DataFrame。

    :param dir1: 第一个文件夹的路径。
    :param dir2: 第二个文件夹的路径。
    :return: 包含文件名和 SSIM 值的 DataFrame。
    """
    data = []
    tasks = []
    dir1 = Path(dir1)
    dir2 = Path(dir2)

    file_path_list = [
        file_path
        for file_path in dir1.glob("**/*")
        if file_path.is_file() and file_path.suffix.lower() in [".jpg", ".jpeg", ".png"]
    ]

    # 遍历 dir1 文件夹中的所有文件
    for file1 in file_path_list:
        file2 = dir2 / file1.name  # 获取对应文件夹中的同名文件
        if not file2.exists() or not file2.is_file():  # 如果文件存在且是文件
            continue

        tasks.append((file1, file2))

    compare_executor = CompareSSIMExecutor(
        compare_ssim_by_path,
        execution_mode="thread",
        max_workers=8,
        progress_desc="Comparing Images",
        show_progress=True,
    )
    compare_executor.start(tasks)
    data = []
    for (file1, file2), ssim in compare_executor.get_success_pairs():
        # 将文件名和 SSIM 值添加到数据列表中
        data.append([file1.name, ssim])

    # 返回包含图像名称和 SSIM 值的 DataFrame
    df = pd.DataFrame(data, columns=["Image Name", "SSIM"])
    return df


def is_image_valid(data: str | Path | io.BytesIO) -> bool:
    """
    检测图片是否有效

    :param data: 图片的路径、文件对象或二进制数据
    :return: True 表示正常，False 表示损坏或格式不符
    """
    try:
        # 统一 Path -> str
        if isinstance(data, Path):
            data = str(data)

        # 第一次打开 + verify
        with Image.open(data) as img:
            img.verify()

        # 如果是文件流/BytesIO，重置指针
        if hasattr(data, "seek"):
            data.seek(0)

        # 第二次打开 + load，确保像素可解码
        with Image.open(data) as img:
            img.load()

        return True

    except Exception:
        return False


def is_image_bytes_valid(byte_data: bytes) -> bool:
    """
    检测二进制图片数据是否有效

    :param byte_data: 图片的二进制内容
    :return: True 表示正常，False 表示损坏或格式不符
    """
    return is_image_valid(io.BytesIO(byte_data))


def create_image_with_text_chunk(
    img: Image.Image, output_path: str, messages: dict[str, str]
):
    """
    将文本字典写入 PNG 文件的 tEXt chunk 中

    :param img: PIL.Image 对象
    :param output_path: 输出文件路径
    :param messages: 键值对形式的文本信息
    """
    meta = PngImagePlugin.PngInfo()
    for key, value in messages.items():
        meta.add_text(key, value)

    img.save(output_path, "PNG", pnginfo=meta)


def read_text_chunks(img_path: str) -> dict[str, str]:
    """
    从 PNG 文件中读取所有 tEXt chunk 信息

    :param img_path: PNG 文件路径
    :return: 包含所有文本块的字典
    """
    with Image.open(img_path) as img:
        info = img.text  # Pillow >= 9.2 推荐用 .text 获取
        # 兼容旧版本 Pillow，若没有 .text 就退回 .info
        if not info:
            info = img.info
        return dict(info)


def simulate_rectangle_damage(
    img: Image.Image, x0: int, y0: int, w: int, h: int
) -> Image.Image:
    """
    在图像上指定位置生成一个 w×h 的损坏矩形（置零）。

    :param img: 原始图像
    :param x0: 矩形左上角 x 坐标
    :param y0: 矩形左上角 y 坐标
    :param w: 矩形宽度
    :param h: 矩形高度
    :return: 损坏后的图像
    """
    damaged = img.copy()
    pixels = damaged.load()

    if img.mode == "RGBA":
        zero_val = (0, 0, 0, 0)
    elif img.mode == "RGB":
        zero_val = (0, 0, 0)
    elif img.mode == "L":
        zero_val = 0
    elif img.mode == "P":
        zero_val = 0
    else:
        raise ValueError(f"Unsupported mode: {img.mode}")

    for y in range(y0, min(y0 + h, img.height)):
        for x in range(x0, min(x0 + w, img.width)):
            pixels[x, y] = zero_val
    return damaged


def simulate_random_damage(img: Image.Image, damage_ratio: float) -> Image.Image:
    """
    随机损坏图像的一部分像素（置零）。

    :param img: 原始图像 (RGBA)
    :param damage_ratio: 损坏比例 (0~1)，表示要损坏的像素数占总像素的比例
    :return: 损坏后的图像
    """
    if not (0 <= damage_ratio <= 1):
        raise ValueError("damage_ratio 必须在 0 到 1 之间")

    damaged = img.copy()
    pixels = damaged.load()
    width, height = img.size
    total_pixels = width * height

    if img.mode == "RGBA":
        zero_val = (0, 0, 0, 0)
    elif img.mode == "RGB":
        zero_val = (0, 0, 0)
    elif img.mode == "L":
        zero_val = 0
    elif img.mode == "P":
        zero_val = 0
    else:
        raise ValueError(f"Unsupported mode: {img.mode}")

    # 需要损坏的像素数
    num_damaged = int(total_pixels * damage_ratio)

    # 随机选出像素坐标
    damaged_coords = random.sample(
        [(x, y) for y in range(height) for x in range(width)], num_damaged
    )

    # 把这些像素置零
    for x, y in damaged_coords:
        pixels[x, y] = zero_val

    return damaged


def ensure_capacity(
    ref_img: Image.Image,
    required_bytes: int,
    *,
    min_able: bool = True,
    min_size: int = 1,
) -> Image.Image:
    """
    自动调整图像尺寸，使其容量刚好匹配存储需求。
    - 当容量不足时放大；
    - 当容量过剩时缩小；
    - 保留视觉结构尽量不失真。

    :param ref_img: 参考图像 (RGBA)
    :param required_bytes: 需要存储的字节数
    :param min_able: 是否允许缩小图像，默认 True。为 False 时仅放大不缩小。
    :param min_size: 图像的最小宽高限制。
    :return: 调整后的图像 (RGBA)。
    """
    width, height = ref_img.size
    current_capacity = width * height

    # 避免 0 或负值
    required_bytes = max(1, required_bytes)
    if required_bytes == current_capacity:
        return ref_img
    elif not min_able and required_bytes < current_capacity:
        return ref_img

    # 计算缩放因子（平方根是因为容量 ~ 面积）
    scale_factor = math.sqrt(required_bytes / current_capacity)

    new_width = max(min_size, math.ceil(width * scale_factor))
    new_height = max(min_size, math.ceil(height * scale_factor))

    # 如果尺寸没有变化，直接返回原图
    if (new_width, new_height) == (width, height):
        return ref_img

    # 当放大时使用平滑插值，当缩小时使用高质量下采样
    resample_mode = Image.BICUBIC if scale_factor > 1 else Image.LANCZOS
    return ref_img.resize((new_width, new_height), resample_mode)


def compare_random_pixels(
    ref_img: Image.Image, enc_img: Image.Image, sample_num: int = 20
):
    """
    在随机点位比较两张图的像素差异。
    打印每个点位的 RGB(A) 值差异，以及整体平均差。

    :param ref_img: 参考原图。
    :param enc_img: 编码后的图像。
    :param sample_num: 随机抽样的像素数量，默认 20。
    """
    from .TextTools import format_table

    width, height = enc_img.size
    ref_img = ensure_capacity(ref_img, width * height)
    ref_img = ref_img.convert("RGBA")

    pixels_ref = ref_img.load()
    pixels_enc = enc_img.load()

    diffs = []
    data = []
    print(f"\n🎯 随机抽样 {sample_num} 个像素比较：\n")

    for _ in range(sample_num):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)

        p_ref = np.array(pixels_ref[x, y])
        p_enc = np.array(pixels_enc[x, y])
        diff = np.abs(p_enc - p_ref)

        diffs.append(diff)
        data.append([x, y, tuple(p_ref), tuple(p_enc), tuple(diff)])

    diffs = np.array(diffs)
    mean_diff = diffs.mean(axis=0)
    max_diff = diffs.max(axis=0)

    print(format_table(data, column_names=["X", "Y", "ref", "enc", "Δ"]))

    print("\n📊 平均差异 (每通道):", tuple(mean_diff.round(2)))
    print("📈 最大差异 (每通道):", tuple(max_diff))
    print(f"🌈 平均总差值 ≈ {mean_diff.mean():.3f} (在 0~255 范围内几乎不可见)")


def show_diff_heatmap(
    ref_img: Image.Image, enc_img: Image.Image, save_path: str = None, show: bool = True
):
    """
    生成两张图像的像素差异热力图。
    :param ref_img: 原图 (PIL.Image)
    :param enc_img: 编码图 (PIL.Image)
    :param save_path: 保存路径（可选）
    :param show: 是否显示结果
    :return: 差异强度矩阵，每像素的平均通道差异值。
    """
    width, height = enc_img.size
    ref_img = ensure_capacity(ref_img, width * height)

    # 转 RGBA 保证通道一致
    ref = np.array(ref_img.convert("RGBA"), dtype=np.int16)
    enc = np.array(enc_img.convert("RGBA"), dtype=np.int16)

    # 差异矩阵 (取绝对值)
    diff = np.abs(ref - enc)

    # 计算每像素的平均差异强度（0~255）
    diff_intensity = diff.mean(axis=2)

    # 归一化到 [0, 1]
    diff_norm = (
        diff_intensity / diff_intensity.max()
        if diff_intensity.max() > 0
        else diff_intensity
    )

    plt.figure(figsize=(8, 8))
    plt.title("Difference Heatmap")
    plt.imshow(diff_norm, cmap="inferno")  # inferno / hot / magma 都不错
    plt.axis("off")

    if save_path:
        plt.savefig(save_path, bbox_inches="tight", pad_inches=0)
        print(f"✅ 热力图已保存到: {save_path}")
    if show:
        plt.show()

    # 返回统计信息
    mean_diff = diff_intensity.mean()
    max_diff = diff_intensity.max()
    print(f"📊 平均像素差异: {mean_diff:.3f}")
    print(f"📈 最大像素差异: {max_diff:.1f}")
    print(
        f"🌈 改动比例约: {(diff_intensity > 0).sum() / diff_intensity.size * 100:.2f}% 像素点有变化"
    )

    return diff_intensity
