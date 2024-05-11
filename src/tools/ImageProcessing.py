import re, os
from PIL import Image
from pillow_heif import register_heif_opener


def compress_img(old_img_path, new_img_path):
    register_heif_opener()
    Image.LOAD_TRUNCATED_IMAGES = True
    Image.MAX_IMAGE_PIXELS = None

    # 打开图片并压缩
    img = Image.open(old_img_path)
    img.save(new_img_path, optimize=True, quality=50)
    

def combine_images_to_pdf(image_directory, output_pdf_path):
    """
    将JPEG图片组合成单个PDF文件。
    :param image_paths: JPEG图片所在的保存文件夹。
    :param output_pdf_path: 输出的PDF文件路径。
    :return: 组合后的PDF文件路径。
    """
    def extract_number(file_name):
        """
        从文件名中提取数字。
        """
        match = re.search(r'\d+', file_name)
        return int(match.group()) if match else 0
    
    from .FileOperations import get_all_file_paths
    image_paths = get_all_file_paths(image_directory)
    image_paths = sorted(image_paths, key=lambda f: extract_number(os.path.basename(f)))

    images = [Image.open(img_path) for img_path in image_paths if img_path.endswith('.jpg') or img_path.endswith('.jpeg')]
    # 将所有图片转换为相同的模式以保证兼容性
    images = [img.convert('RGB') for img in images]
    # 将所有图片保存为单个PDF
    images[0].save(output_pdf_path, save_all=True, append_images=images[1:])

    return output_pdf_path