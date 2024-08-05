import fitz, shutil
import markdown
import pdfkit
from PIL import Image
from pathlib import Path


def md_to_pdf(input_directory: str | Path, output_directory: str | Path):
    """
    将输入目录中的Markdown文件转换为PDF文件

    :param input_directory: 输入目录
    :param output_directory: 输出目录
    :return: None
    """
    # 将输入路径和输出路径转换为Path对象
    input_dir = Path(input_directory)
    output_dir = Path(output_directory)

    # 获取输入目录中的所有Markdown文件
    md_files = [f for f in input_dir.glob('*.md')]

    # 遍历所有Markdown文件
    for md_file in md_files:
        # 获取输出路径
        output_path = output_dir / md_file.with_suffix('.pdf').name

        # 读取Markdown文件内容
        md_content = md_file.read_text(encoding='utf-8')

        # 将Markdown文件内容转换为HTML
        html_content = markdown.markdown(md_content)

        # 将HTML文件转换为PDF
        pdfkit.from_string(html_content, output_path)
        # print(f"Converted {md_file.name} to PDF")

def transfer_pdf_to_img(pdf_path: str | Path, img_path: str | Path):
    """
    将PDF文件转换为图片文件

    :param pdf_path: PDF文件路径
    :param img_path: 图片文件路径
    :return: None
    """
    pdf_path = Path(pdf_path)
    img_path = Path(img_path)
    img_path.mkdir(parents=True, exist_ok=True)  # 创建图片目录(如果不存在)

    doc = fitz.open(pdf_path)
    for page_num, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=fitz.Matrix(150/72, 150/72))  # 将页面渲染为图片
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)  # 将 Pixmap 转换为 PIL Image
        img_file = img_path / f"{page_num}.jpg"
        img.save(str(img_file), quality=50)  # 使用 PIL 保存图像

    doc.close()


def compress_pdf(old_pdf_path: str | Path, new_pdf_path: str | Path):
    '''
    压缩PDF，即将PDF转换为jpg图片，再将图片合并为PDF

    :param old_pdf_path: 原PDF路径
    :param new_pdf_path: 新PDF路径
    :return: None
    '''
    from .ImageProcessing import combine_imgs_to_pdf

    old_pdf_path = Path(old_pdf_path)
    new_pdf_path = Path(new_pdf_path)
    temp_img_path = old_pdf_path.parent.joinpath('temp')
    
    transfer_pdf_to_img(old_pdf_path, temp_img_path)
    combine_imgs_to_pdf(temp_img_path, new_pdf_path)
    shutil.rmtree(temp_img_path)
