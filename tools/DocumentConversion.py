import fitz, shutil, re
import PyPDF2
import subprocess
from PIL import Image
from pathlib import Path
from typing import Union
from tqdm import tqdm


def md_to_pdf(md_file_path: Union[str, Path], pdf_file_path: Union[str, Path]):
    """
    使用pandoc将指定的Markdown文件转换为PDF文件。

    :param md_file_path: 输入的Markdown文件路径
    :param pdf_file_path: 输出的PDF文件路径
    """
    md_file_path = Path(md_file_path)
    pdf_file_path = Path(pdf_file_path)

    # 使用pandoc进行转换, 可根据需要增加其它参数，如:
    # --pdf-engine=xelatex 用于支持Unicode字符
    # --toc 生成目录
    # --template 指定latex模板
    subprocess.run(["pandoc", str(md_file_path), "-o", str(pdf_file_path), "--pdf-engine=xelatex"], check=True)

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

def merge_pdfs_in_order(folder_path: str | Path) -> list:
    """
    将指定文件夹下的所有PDF文件按照指定顺序拼接，并输出到指定文件名的PDF文件中。
    :param folder_path: 存放PDF文件的文件夹路径。
    :return : 拼接后的PDF文件路径。
    """
    def extract_number(file_path: Path) -> tuple:
        """
        提取文件路径中的文件夹名称和文件名中的数字，作为排序依据。
        一级排序：文件夹名称
        二级排序：文件名中的数字
        """
        folder_name = file_path.parent.name
        matches = re.findall(r'\d+', file_path.name)
        number = matches if matches else [float('inf')]
        return (folder_name, *number)
    
    from tools.FileOperations import folder_to_file_path
    # 创建一个PdfWriter对象，用于输出拼接后的PDF文件
    output_pdf = PyPDF2.PdfWriter()
    
    # 使用pathlib.Path来处理路径
    folder_path = Path(folder_path)
    output_filename = folder_to_file_path(folder_path, 'pdf')  # 拼接输出文件路径
    
    # 获取该文件夹下的所有PDF文件，并根据文件名中的数字进行排序
    pdf_files = sorted(folder_path.glob('*.pdf'), key=extract_number)

    # 按照指定顺序依次合并PDF文件
    for pdf_file in tqdm(pdf_files):
        with open(pdf_file, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                output_pdf.add_page(page)
    
    # 将输出对象中的内容写入到输出文件中
    with open(output_filename, 'wb') as f:
        output_pdf.write(f)
    print(f'PDF files from {folder_path.name} have been merged into {output_filename}')

    return pdf_files