import fitz, shutil, re
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
    from tools.ImageProcessing import combine_imgs_to_pdf

    old_pdf_path = Path(old_pdf_path)
    new_pdf_path = Path(new_pdf_path)
    temp_img_path = old_pdf_path.parent.joinpath('temp')
    
    transfer_pdf_to_img(old_pdf_path, temp_img_path)
    combine_imgs_to_pdf(temp_img_path, new_pdf_path)
    shutil.rmtree(temp_img_path)

def combine_txt_files(folder_path: str | Path):
    """
    将指定文件夹内的所有txt文件按文件名中的数字排序，合并为一个新的txt文件。
    合并时每个文件的内容前面加入该文件的名字，合并文件名为文件夹名。

    :param folder_path: 包含txt文件的文件夹路径。
    :return: None
    """
    def extract_number(file_name: Path) -> int:
        """
        从文件名中提取数字，用于排序。
        """
        match = re.search(r'\d+', file_name.name)
        return int(match.group()) if match else 0

    # 转换路径为 Path 对象
    folder_path = Path(folder_path)

    if not folder_path.is_dir():
        raise ValueError(f"The provided path {folder_path} is not a directory.")

    # 获取文件夹名称作为输出文件名
    output_file_name = f"{folder_path.name}.txt"
    output_file_path = folder_path / output_file_name

    # 获取所有txt文件路径，并按文件名中的数字排序
    txt_files = sorted(folder_path.glob('*.txt'), key=extract_number)

    if not txt_files:
        raise ValueError(f"No txt files found in {folder_path}.")

    # 合并文件
    with open(output_file_path, 'w', encoding='utf-8') as outfile:
        for txt_file in txt_files:
            with open(txt_file, 'r', encoding='utf-8') as infile:
                content = infile.read()
                # 写入文件名和内容
                outfile.write(f"== {txt_file.name} ==\n")
                outfile.write(content + "\n\n")

    print(f"All files have been combined into {output_file_path}")

