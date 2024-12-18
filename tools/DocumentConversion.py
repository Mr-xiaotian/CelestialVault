import fitz, shutil, re
import markdown
import pdfkit
import PyPDF2
from PIL import Image
from pathlib import Path


def md_to_pdf(input_directory: str | Path, output_directory: str | Path=None):
    """
    将输入目录中的Markdown文件转换为PDF文件

    :param input_directory: 输入目录
    :param output_directory: 输出目录
    :return: None
    """
    # 将输入路径和输出路径转换为Path对象
    input_dir = Path(input_directory)
    output_dir = Path(output_directory) if output_directory else input_dir

    path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'  # Windows
    # path_to_wkhtmltopdf = '/usr/local/bin/wkhtmltopdf'  # macOS 或 Linux

    config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)
    options = {
        'no-outline': None,  # 去掉边框
        'encoding': 'UTF-8',  # 设置编码
        'custom-header': [
            ('Accept-Encoding', 'gzip')
            ]
    }

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
        pdfkit.from_string(html_content, output_path, configuration=config, options=options)
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
        img.save(str(img_file), quality=75)  # 使用 PIL 保存图像

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

def merge_pdfs_in_order(folder_path: str | Path, pdf_path: str | Path = None):
    """
    将指定文件夹下的所有PDF文件按照指定顺序拼接，并输出到指定文件名的PDF文件中。
    :param folder_path: 存放PDF文件的文件夹路径。
    :return: None。
    """
    def extract_number(file_name: Path) -> int:
        """
        从文件名中提取数字，用于排序。
        """
        matches = re.findall(r'\d+', file_name.name)
        return int(''.join(matches)) if matches else float('inf')
    
    from tools.FileOperations import folder_to_file_path
    # 创建一个PdfWriter对象，用于输出拼接后的PDF文件
    output_pdf = PyPDF2.PdfWriter()
    
    # 使用pathlib.Path来处理路径
    folder_path = Path(folder_path)
    
    # 获取该文件夹下的所有PDF文件，并根据文件名中的数字进行排序
    pdf_files = sorted(folder_path.glob('*.pdf'), key=extract_number)

    output_filename = folder_to_file_path(folder_path, 'pdf')  # 拼接输出文件路径

    # 按照指定顺序依次合并PDF文件
    for pdf_file in pdf_files:
        with open(pdf_file, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                output_pdf.add_page(page)
    
    # 将输出对象中的内容写入到输出文件中
    with open(output_filename, 'wb') as f:
        output_pdf.write(f)
    print(f'PDF files from {folder_path.name} have been merged into {output_filename}')