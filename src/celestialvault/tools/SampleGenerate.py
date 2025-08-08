import random
import string
from pathlib import Path
from typing import List, Union

import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont


def generate_test_images(
    root_dir: str | Path, num_folders: int = 3, images_per_folder: int = 5
):
    """
    在指定路径下生成多个子文件夹，每个文件夹中包含若干张大小随机、颜色不同的测试图片。

    :param root_dir: 根目录路径，将在其下创建子文件夹和图片
    :param num_folders: 子文件夹数量
    :param images_per_folder: 每个子文件夹中生成的图片数量
    """
    root_dir = Path(root_dir)
    root_dir.mkdir(parents=True, exist_ok=True)

    for folder_idx in range(1, num_folders + 1):
        folder = root_dir / f"folder_{folder_idx}"
        folder.mkdir(exist_ok=True)

        for img_idx in range(1, images_per_folder + 1):
            width = random.randint(300, 800)
            height = random.randint(300, 1000)
            color = tuple(random.randint(0, 255) for _ in range(3))

            img = Image.new("RGB", (width, height), color=color)
            draw = ImageDraw.Draw(img)

            text = f"{folder.name}_{img_idx}\n{width}x{height}"
            try:
                font = ImageFont.truetype("arial.ttf", size=24)
            except:
                font = ImageFont.load_default()
            draw.text((10, 10), text, fill="white", font=font)

            img.save(folder / f"img_{img_idx:02d}.jpg")

    print(
        f"✅ 成功生成 {num_folders} 个子文件夹，每个包含 {images_per_folder} 张测试图片。"
    )


def create_sample_pdf(file_path: str | Path):
    """
    创建一个包含不同尺寸页面的示例 PDF 文件。

    :param file_path: 输出 PDF 文件的路径
    """
    # 创建新的 PDF 文档
    doc = fitz.open()

    # 页面 1 - A5 尺寸 (420x595)
    page = doc.new_page(width=420, height=595)
    page.insert_text((72, 100), "页面 1：A5 尺寸 (420x595)", fontsize=14)
    page.insert_text(
        (72, 130), "这是一个示例 PDF，页面尺寸较小，用于测试页面宽度调整功能。"
    )

    # 页面 2 - A4 尺寸 (595x842)
    page = doc.new_page(width=595, height=842)
    page.insert_text((72, 100), "页面 2：A4 尺寸 (595x842)", fontsize=14)
    page.insert_text((72, 130), "该页面的宽度较上一页更大，适用于文本内容较多的场景。")

    # 页面 3 - A3 尺寸 (842x1191)
    page = doc.new_page(width=842, height=1191)
    page.insert_text((72, 100), "页面 3：A3 尺寸 (842x1191)", fontsize=14)
    page.insert_text(
        (72, 130), "这是一个超宽页面，适用于需要展示更大图片或表格的场景。"
    )

    # 保存 PDF 文件
    doc.save(str(file_path))

    print(f"✅ 成功创建示例 PDF 文件：{file_path}")


def generate_test_data(length: int, data_types: Union[str, List[str]] = None):
    """
    生成测试数据
    :param data_types: 数据类型，可以是字符串（'str', 'word', 'int', 'float'）或列表（支持多选）。
                       如果为 None，则默认全选所有类型。
    :param length: 数据数量
    :return: 随机数据列表
    """
    all_types = ["str", "word", "int", "float"]

    # 统一成列表形式
    if data_types is None:
        data_types = all_types
    elif isinstance(data_types, str):
        data_types = [data_types]
    else:
        # 过滤无效类型
        data_types = [t for t in data_types if t in all_types]
        if not data_types:
            raise ValueError(f"不支持的数据类型: {data_types}")

    def random_item(dtype: str):
        if dtype == "str":
            return ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 10)))
        elif dtype == "word":
            return ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 8))).capitalize()
        elif dtype == "int":
            return random.randint(1, 1000)
        elif dtype == "float":
            return round(random.uniform(0, 100), 2)
        else:
            raise ValueError(f"不支持的数据类型: {dtype}")

    return [random_item(random.choice(data_types)) for _ in range(length)]