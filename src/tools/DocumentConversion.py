import os
import shutil, fitz
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
    # 获取输入目录中的所有Markdown文件
    md_files = [f for f in os.listdir(input_directory) if f.endswith('.md')]

    # 遍历所有Markdown文件
    for md_file in md_files:
        # 获取输入路径和输出路径
        input_path = os.path.join(input_directory, md_file)
        output_path = os.path.join(output_directory, md_file.replace('.md', '.pdf'))

        # 读取Markdown文件内容
        with open(input_path, 'r', encoding='utf-8') as file:
            md_content = file.read()

        # 将Markdown文件内容转换为HTML
        html_content = markdown.markdown(md_content)
        # 将HTML文件转换为PDF
        pdfkit.from_string(html_content, output_path)
        # print(f"Converted {md_file} to PDF")

def transfer_pdf_to_img(pdf_path: str | Path, img_path: str | Path):
    """
    将PDF文件转换为图片文件

    :param pdf_path: PDF文件路径
    :param img_path: 图片文件路径
    :return: None
    """
    image_paths = []

    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # 加载页面
        pix = page.get_pixmap(matrix=fitz.Matrix(150/72, 150/72))  # 将页面渲染为图片
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples) # 将 Pixmap 转换为 PIL Image
        
        img.save(f'{img_path}/{page_num+1}.jpg', quality=50) # 使用 PIL 保存图像
        image_paths.append(img_path)

    doc.close()


def compress_pdf(old_pdf_path: str | Path, new_pdf_path: str | Path):
    '''
    压缩PDF，即将PDF转换为jpg图片，再将图片合并为PDF

    :param old_pdf_path: 原PDF路径
    :param new_pdf_path: 新PDF路径
    :return: None
    '''
    from .ImageProcessing import combine_img_to_pdf

    old_pdf_path = Path(old_pdf_path)
    temp_img_path = old_pdf_path.parent.joinpath('temp')
    temp_img_path.mkdir(parents=True, exist_ok=True)
    
    transfer_pdf_to_img(old_pdf_path, temp_img_path)
    combine_img_to_pdf(temp_img_path, new_pdf_path)
    shutil.rmtree(temp_img_path)

if __name__ == '__main__':
    # a = '(W//R\S/H\\U)'
    # b = "https:\/\/m10.music.126.net\/20211221203525\/cb633fbb6fd0423417ef492e2225ba45\/ymusic\/7dbe\/b17e\/1937\/9982bb924f5c3adc6f85679fcf221418.mp3"
    #t = pro_slash(a)

    # join_and_label_videos(
    # r'F:\下载\魔法擦除_20230731_1(1)\temp\chf3_prob3.mp4', 
    # r'F:\下载\魔法擦除_20230731_1(1)\temp\chf3_prob3_stab_thm2.mp4',
    # r'F:\下载\魔法擦除_20230731_1(1)\temp\mix.mp4'
    #                     )
    pass