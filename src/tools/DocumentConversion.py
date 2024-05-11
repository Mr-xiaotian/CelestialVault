import os
import shutil, fitz
import markdown
import pdfkit
from .FileOperations import creat_folder
from .ImageProcessing import combine_images_to_pdf

def md_to_pdf(input_directory, output_directory):
    # 获取所有的 .md 文件
    md_files = [f for f in os.listdir(input_directory) if f.endswith('.md')]

    for md_file in md_files:
        input_path = os.path.join(input_directory, md_file)
        output_path = os.path.join(output_directory, md_file.replace('.md', '.pdf'))

        # 读取 Markdown 文件内容
        with open(input_path, 'r', encoding='utf-8') as file:
            md_content = file.read()

        # 使用 markdown 库转换为 HTML
        html_content = markdown.markdown(md_content)

        # 使用 pdfkit 将 HTML 转换为 PDF
        pdfkit.from_string(html_content, output_path)

        print(f"Converted {md_file} to PDF")

def compress_pdf(pdf_path):
    """
    将PDF文件的每一页转换为单独的图片文件。
    :param pdf_path: PDF文件的路径。
    :return: 图片文件的路径列表。
    """
    doc = fitz.open(pdf_path)
    image_paths = []
    
    temp_path = os.path.dirname(pdf_path) + '/temp'
    out_path = pdf_path.replace('.pdf', '_compressed.pdf')
    creat_folder(temp_path)
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # 加载页面
        pix = page.get_pixmap(matrix=fitz.Matrix(150/72, 150/72))  # 将页面渲染为图片
        pix.save(f'{temp_path}/{page_num+1}.jpg')  # 保存为PNG格式的图片
        image_paths.append(temp_path)

    doc.close()
    combine_images_to_pdf(temp_path, out_path)
    shutil.rmtree(temp_path)

if __name__ == '__main__':
    # a = '(W//R\S/H\\U)'
    # b = "https:\/\/m10.music.126.net\/20211221203525\/cb633fbb6fd0423417ef492e2225ba45\/ymusic\/7dbe\/b17e\/1937\/9982bb924f5c3adc6f85679fcf221418.mp3"
    #t = pro_slash(a)

    # join_and_label_videos(
    # r'F:\下载\魔法擦除_20230731_1(1)\temp\chf3_prob3.mp4', 
    # r'F:\下载\魔法擦除_20230731_1(1)\temp\chf3_prob3_stab_thm2.mp4',
    # r'F:\下载\魔法擦除_20230731_1(1)\temp\mix.mp4'
    #                     )
    # for i in [r'G:\Project\Spider\xxgirls\download', r'F:\下载\BaiduNetdiskDownload\原神视频\人物']:
    #     compress_fold(i)
    
    # compress_pdf(r'F:\下载\test\服务协议.pdf')
    combine_images_to_pdf(r'Z:\Photo\temp', r'Z:\Photo\temp\output.pdf')