import re
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
    将JPEG图片组合成单个PDF文件。

    :param image_paths: JPEG图片所在的保存文件夹。
    :param output_pdf_path: 输出的PDF文件路径。
    :return: None
    """
    from ..constants import IMG_SUFFIXES
    def extract_number(file_name: Path) -> int:
        """
        从文件名中提取数字。
        """
        match = re.search(r'\d+', file_name.name)
        return int(match.group()) if match else 0

    image_path = Path(image_path)
    pdf_path = Path(pdf_path)
    
    image_paths = []
    IMG_SUFFIXES.append('gif')
    for ext in IMG_SUFFIXES:
        image_paths += list(image_path.glob(f'*.{ext}'))
    image_paths = [p for p in image_paths if p.is_file()]
    image_paths = list(set(image_paths))
    image_paths = sorted(image_paths, key=extract_number)

    images = [Image.open(img_path) for img_path in image_paths]
    # 将所有图片转换为相同的模式以保证兼容性
    images = [img.convert('RGB') for img in images]
    # 将所有图片保存为单个PDF
    images[0].save(pdf_path, save_all=True, append_images=images[1:])