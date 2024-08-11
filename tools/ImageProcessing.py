import re, io, base64, math
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path
from tqdm import tqdm
from itertools import product
from pillow_heif import register_heif_opener
from colorsys import hsv_to_rgb


def compress_img(old_img_path: str | Path, new_img_path: str | Path):
    register_heif_opener()
    Image.LOAD_TRUNCATED_IMAGES = True
    Image.MAX_IMAGE_PIXELS = None

    # 打开图片并压缩
    img = Image.open(old_img_path)
    img.save(new_img_path, optimize=True, quality=50)

def combine_imgs_to_pdf(image_path: str | Path, pdf_path: str | Path):
    """
    将指定文件夹中的JPEG图片组合成单个PDF文件。

    :param image_path: 包含JPEG图片的文件夹路径。
    :param pdf_path: 输出的PDF文件路径。
    :return: None
    """
    from constants import IMG_SUFFIXES
    
    def extract_number(file_name: Path) -> int:
        """
        从文件名中提取数字，用于排序。
        """
        match = re.search(r'\d+', file_name.name)
        return int(match.group()) if match else 0

    # 转换路径为 Path 对象
    image_path = Path(image_path)
    pdf_path = Path(pdf_path)
    
    if not image_path.is_dir():
        raise ValueError(f"The provided image path {image_path} is not a directory.")
    
    # 收集所有图片路径
    image_paths = []
    valid_suffixes = IMG_SUFFIXES.copy()

    for ext in valid_suffixes:
        image_paths += list(image_path.glob(f'*.{ext}'))

    image_paths = [p for p in image_paths if p.is_file()]
    image_paths = list(set(image_paths))  # 去重
    image_paths = sorted(image_paths, key=extract_number)  # 按文件名中的数字排序

    if not image_paths:
        raise ValueError(f"No images found in {image_path} with suffixes: {valid_suffixes}")

    # 打开所有图片并转换为 RGB 模式
    try:
        images = [Image.open(img_path).convert('RGB') for img_path in image_paths]
    except Exception as e:
        raise ValueError(f"Error loading images: {e}")

    # 将图片保存为单个PDF
    try:
        images[0].save(pdf_path, save_all=True, append_images=images[1:])
    except Exception as e:
        raise ValueError(f"Error saving PDF: {e}")

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
    from tools.ImageProcessing import binary_to_img
    # 将Base64文本解码回二进制数据
    binary_data = base64.b64decode(base64_str)

    # 将二进制数据转换为Image对象
    img = binary_to_img(binary_data)

    return img
    
def img_to_base64(img: Image.Image) -> str:
    from tools.ImageProcessing import img_to_binary
    # 将Image数据转换为二进制数据
    binary_data = img_to_binary(img)

    # 将二进制数据编码成Base64文本
    encoded_text = base64.b64encode(binary_data).decode('utf-8')

    return encoded_text

def generate_palette_random(n=256, random_seed=0, style=None):
    """
    生成调色板，默认为Morandi 色系，并确保颜色唯一。

    :param n: 要生成的颜色数量
    :param random_seed: 随机种子，确保颜色生成的可重复性
    :param style: 调色板风格，可选 'morandi' 或 'grey'，默认为 'morandi'
    """
    if not style or style == 'morandi':
        hue_range = (0, 1)
        saturation_range=(0.1, 0.3)
        value_range=(0.7, 0.9)
    elif style == 'grey':
        hue_range = (0, 0)
        saturation_range=(0, 0)
        value_range=(0.5, 0.8)
    else:
        raise ValueError("Unsupported style")

    np.random.seed(random_seed)
    colors = set()

    while len(colors) < n:
        h = np.random.uniform(*hue_range)  # 随机色调
        s = np.random.uniform(*saturation_range)  # 低饱和度
        v = np.random.uniform(*value_range)  # 较高亮度
        
        r, g, b = hsv_to_rgb(h, s, v)
        color = (int(r*255), int(g*255), int(b*255))
        colors.add(color) # 尝试将颜色添加到集合中，确保唯一性

    # 将颜色集转换为列表形式，并展开为单个数值列表
    return [value for color in colors for value in color]

def display_palette(palette, block_size=1):
    """
    展示调色板。

    :param palette: 一个包含 RGB 颜色的平铺列表或元组，形如 [r, g, b, r, g, b, ...]
    :param block_size: 每个颜色块的大小，默认为1
    """
    total_colors = len(palette) // 3  # 计算颜色的数量
    
    n_cols = math.ceil(math.sqrt(total_colors))
    n_rows = math.ceil(total_colors / n_cols)
    
    # 调整图像大小以适应颜色块
    fig, ax = plt.subplots(figsize=(n_cols * block_size, n_rows * block_size))
    
    # 设置坐标轴的范围与颜色块的数量完全匹配
    ax.set_xlim(0, n_cols)
    ax.set_ylim(0, n_rows)
    
    # 关闭坐标轴
    ax.axis('off')
    
    for i in range(total_colors):
        r, g, b = palette[3 * i], palette[3 * i + 1], palette[3 * i + 2]
        hex_color = '#%02x%02x%02x' % (r, g, b)
        ax.add_patch(plt.Rectangle(
            (i % n_cols, n_rows - 1 - i // n_cols), 
            block_size, block_size, 
            color=hex_color,
            linewidth=0
        ))
    
    plt.show()

def expand_image(image: Image.Image, n: int=50) -> Image.Image:
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
    if image.mode == 'P':
        image = image.convert('RGB')

    width, height = image.size

    # 准备保存GIF的帧列表
    frames = []
    progress_bar = tqdm(total=height * width, desc='Extract Pixels:')

    # 提取每个像素点并生成每帧图像
    for y, x in product(range(height), range(width)):
        pixel = image.getpixel((x, y))
        frame = Image.new(image.mode, (frame_size, frame_size), color=pixel)
        frames.append(frame)
        progress_bar.update(1)
    
    progress_bar.close()

    # 将帧保存到一个BytesIO对象中
    gif_io = io.BytesIO()
    frames[0].save(gif_io, format='GIF', save_all=True, append_images=frames[1:], duration=duration, loop=loop)

    gif_io.seek(0)
    return gif_io