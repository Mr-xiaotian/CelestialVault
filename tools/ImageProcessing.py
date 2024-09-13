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
    img.save(new_img_path, optimize=True, quality=75)

def combine_imgs_to_pdf(image_path: str | Path, pdf_path: str | Path = None):
    """
    将指定文件夹中的JPEG图片组合成单个PDF文件。

    :param image_path: 包含JPEG图片的文件夹路径。
    :param pdf_path: 输出的PDF文件路径。
    :return: None
    """
    def extract_number(file_name: Path) -> int:
        """
        从文件名中提取数字，用于排序。
        """
        matches = re.findall(r'\d+', file_name.name)
        return int(''.join(matches)) if matches else float('inf')

    from tools.FileOperations import folder_to_file_path
    from constants import IMG_SUFFIXES
    # 转换路径为 Path 对象
    image_path = Path(image_path)
    pdf_path = folder_to_file_path(image_path, 'pdf') if pdf_path is None else Path(pdf_path)
    
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

    # 找到最大宽度的图片
    max_width = 0
    for img_path in image_paths:
        with Image.open(img_path) as img:
            max_width = max(max_width, img.size[0])
    
    # 生成器函数：逐步处理图片，调整宽度
    def generate_resized_images():
        for img_path in tqdm(image_paths, desc="Combining images"):
            img = Image.open(img_path).convert('RGB')
            width, height = img.size
            if width != max_width:
                new_height = int(max_width * height / width)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            yield img

    # 保存第一张图片，并附加后续图片到 PDF
    resized_images = generate_resized_images()  # 生成其余的图片
    first_image = next(resized_images)  # 获取第一张图片
    
    first_image.save(pdf_path, save_all=True, append_images=resized_images)

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
    encoded_text = base64.b64encode(binary_data).decode('utf-8')

    return encoded_text

def generate_palette(color_num=256, style='morandi', mode='random', random_seed=0):
    """
    生成调色板，支持均匀和螺旋两种模式，并确保颜色唯一或规律分布。

    :param color_num: 要生成的颜色数量
    :param style: 调色板风格，可选 'morandi', 'grey', 'hawaiian', 'deepsea', 'twilight', 'sunrise', 'cyberpunk', 'autumn'，默认为 'morandi'
    :param mode: 颜色生成模式，可选 'random' 'uniform', 'spiral'
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
        ranges = [(range_tuple[i], range_tuple[i+1]) for i in range(0, len(range_tuple), 2)]
        
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
        s = saturation_range[0] + (saturation_range[1] - saturation_range[0]) * (np.sin(index / color_num * 2 * np.pi) / 2 + 0.5)
        v = value_range[0] + (value_range[1] - value_range[0]) * (np.cos(index / color_num * 2 * np.pi) / 2 + 0.5)
        return h, s, v

    from constants import style_params

    if style not in style_params:
        raise ValueError("Unsupported style")
    if mode not in ['random', 'uniform', 'spiral']:
        raise ValueError("Unsupported mode")

    params = style_params[style]
    np.random.seed(random_seed)

    get_hsv = None
    mode_dict = {'random': random_mode, 'uniform': uniform_mode, 'spiral': spiral_mode}
    get_hsv = mode_dict[mode]

    colors = []
    used_hsv = set()
    for i in range(color_num):
        hue_range = select_random_range(params['hue_range'])
        saturation_range = select_random_range(params['saturation_range'])
        value_range = select_random_range(params['value_range'])

        h, s, v = get_hsv(hue_range, saturation_range, value_range, i)
        r, g, b = hsv_to_rgb(h, s, v)
        color = (int(r * 255), int(g * 255), int(b * 255))
        colors.append(color)
        
    return [value for color in colors for value in color]

def display_palette(palette, block_size=1):
    """
    展示调色板。

    :param palette: 一个包含 RGB 颜色的平铺列表或元组，形如 [r, g, b, r, g, b, ...]
    :param block_size: 每个颜色块的大小，默认为1
    """
    def rgb_to_hex(r, g, b):
        return '#%02x%02x%02x' % (r, g, b)
    
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
        hex_color = rgb_to_hex(r, g, b)
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