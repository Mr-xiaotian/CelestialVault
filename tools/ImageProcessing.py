import re, io
from PIL import Image
from pathlib import Path
from pillow_heif import register_heif_opener


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