import re, io, base64
import numpy as np
from PIL import Image
from pathlib import Path
from pillow_heif import register_heif_opener
from colorsys import rgb_to_hsv, hsv_to_rgb


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

def generate_morandi_colors(n=256, random_seed=0):
    colors = []
    np.random.seed(random_seed)
    
    for _ in range(n):
        # 随机生成低饱和度的颜色
        h = np.random.uniform(0, 1)  # 随机色调
        s = np.random.uniform(0.1, 0.3)  # 低饱和度
        v = np.random.uniform(0.7, 0.9)  # 较高亮度
        
        r, g, b = hsv_to_rgb(h, s, v)
        colors += [int(r*255), int(g*255), int(b*255)]
    
    return colors

def expand_image(image: Image.Image, n: int=50) -> Image.Image:
    """
    将图像中的每个像素点扩大为n x n的块
    """
    width, height = image.size
    new_width = width * n
    new_height = height * n
    
    # 创建一个新图像，大小是原图的n倍
    expanded_image = Image.new(image.mode, (new_width, new_height))
    
    for x in range(width):
        for y in range(height):
            # 获取原图中的像素值
            pixel = image.getpixel((x, y))
            
            # 在新图中创建n x n的块
            for i in range(n):
                for j in range(n):
                    expanded_image.putpixel((x * n + i, y * n + j), pixel)
    
    return expanded_image

def expand_palette_image(image: Image.Image, n: int=50) -> Image.Image:
    """
    将调色板模式图像中的每个像素点扩大为n x n的块
    """
    # 将图像转换为RGB模式
    rgb_image = image.convert("RGB")
    
    # 获取原图像的尺寸
    width, height = rgb_image.size
    new_width = width * n
    new_height = height * n
    
    # 创建一个新图像，大小是原图的n倍
    expanded_image = Image.new("RGB", (new_width, new_height))
    
    for x in range(width):
        for y in range(height):
            # 获取原图中的像素值
            pixel = rgb_image.getpixel((x, y))
            
            # 在新图中创建n x n的块
            for i in range(n):
                for j in range(n):
                    expanded_image.putpixel((x * n + i, y * n + j), pixel)
    
    # 将扩展后的图像转换回调色板模式
    expanded_palette_image = expanded_image.convert("P", palette=Image.ADAPTIVE, colors=256)
    
    return expanded_palette_image

from PIL import Image

def restore_expanded_image(expanded_image: Image.Image, n) -> Image.Image:
    """
    将扩展后的 RGB 图像恢复为原始大小
    """
    # 获取扩展图像的尺寸
    new_width, new_height = expanded_image.size
    width = new_width // n
    height = new_height // n
    
    # 创建一个新图像，大小是原始尺寸
    restored_image = Image.new(expanded_image.mode, (width, height))
    
    for x in range(width):
        for y in range(height):
            # 获取扩展图像中对应的 n x n 块的左上角像素
            pixel = expanded_image.getpixel((x * n, y * n))
            
            # 将该像素写入恢复图像
            restored_image.putpixel((x, y), pixel)
    
    return restored_image

def restore_expanded_palette_image(expanded_palette_image: Image.Image, n) -> Image.Image:
    """
    将扩展后的调色板图像恢复为原始大小
    """
    # 将调色板图像转换为 RGB 模式
    expanded_rgb_image = expanded_palette_image.convert("RGB")
    
    # 恢复图像的原始大小
    restored_rgb_image = restore_expanded_image(expanded_rgb_image, n)
    
    # 将恢复后的图像转换回调色板模式
    restored_palette_image = restored_rgb_image.convert("P", palette=Image.ADAPTIVE, colors=256)
    
    return restored_palette_image
