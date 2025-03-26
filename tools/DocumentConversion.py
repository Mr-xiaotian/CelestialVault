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

def transfer_pdf_to_img(pdf_path: str | Path, img_path: str | Path, dpi: int = 150, quality: int = 85):
    """
    将PDF文件转换为图片文件

    :param pdf_path: PDF文件路径
    :param img_path: 图片文件路径
    :param dpi: 图片分辨率(72/150/300)
    :param quality: 图片质量(75/85/95)
    :return: None
    """
    pdf_path = Path(pdf_path)
    img_path = Path(img_path)
    img_path.mkdir(parents=True, exist_ok=True)  # 创建图片目录(如果不存在)

    scale = dpi / 72  # DPI 转换
    matrix = fitz.Matrix(scale, scale)

    doc = fitz.open(pdf_path)
    for page_num, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix)  # 将页面渲染为图片
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)  # 将 Pixmap 转换为 PIL Image
        img_file = img_path / f"{page_num}.jpg"
        img.save(str(img_file), quality=quality)  # 使用 PIL 保存图像

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
    将指定文件夹下的所有 PDF 文件按指定顺序合并，并在输出 PDF 中为每个源文件添加
    一个一级目录（书签），书签名称为该 PDF 文件的文件名（去掉后缀）。

    :param folder_path: 存放 PDF 文件的文件夹路径。
    :return: 合并时所使用的 PDF 文件列表（按合并顺序）。
    """
    from tools.FileOperations import folder_to_file_path, sort_by_folder_and_number

    folder_path = Path(folder_path)
    pdf_path = folder_to_file_path(folder_path, "pdf")

    # 初始化 PdfWriter 用来输出合并后的 PDF
    output_pdf = PyPDF2.PdfWriter()

    # 按自定义规则排序 PDF 文件，这里用 sort_by_folder_and_number
    pdf_files = sorted(folder_path.glob("*.pdf"), key=lambda path: sort_by_folder_and_number(path, {}))

    # 用来记录当前合并后 PDF 的已有页数，下一个文件的起始页就是它
    current_page_count = 0
    for pdf_file in tqdm(pdf_files, desc="Merging PDFs"):
        with open(pdf_file, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            start_page = current_page_count  # 记录此 PDF 添加前的起始页

            # 把此文件所有页追加到 output_pdf
            for page in pdf_reader.pages:
                output_pdf.add_page(page)

            # 为此文件创建一个书签（即一级目录），标题用文件名（去后缀），
            # 指向它在合并 PDF 中的第一页位置
            # 注：如果要让阅读器显示的“第 1 页”与书签一致，可能需要 +1
            output_pdf.add_outline_item(
                title=pdf_file.stem,        # 例如 "MyDocument"
                page_number=start_page,     # 0-based index
                parent=None                 # 为空表示加在顶级目录
            )
            
            # 更新总页数
            current_page_count += len(pdf_reader.pages)

    # 最后写出合并后的 PDF
    with open(pdf_path, "wb") as f_out:
        output_pdf.write(f_out)

    return pdf_files

def resize_pdf_to_max_width(pdf_path: str | Path, output_path: str | Path, max_width: int = None):
    """
    将 PDF 文件中的每一页的宽度调整为最大宽度，保持纵横比不变。

    :param pdf_path: 输入 PDF 文件路径
    :param output_path: 输出 PDF 文件路径
    :return: None
    """
    def get_max_width(doc):
        """
        获取 PDF 文件中所有页面的最大宽度。
        """
        return max(page.rect.width for page in doc)
    
    pdf_path = Path(pdf_path)
    output_path = Path(output_path)

    # 检查输出文件是否已存在，避免意外覆盖
    if output_path.exists():
        raise FileExistsError(f"错误：文件 '{output_path}' 已存在。")
    
    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with fitz.open(pdf_path) as doc, fitz.open() as output_pdf:
        max_width = max_width or get_max_width(doc)

        # 第二次遍历，缩放每一页
        for page in doc:
            original_width, original_height = page.rect.width, page.rect.height
            scale_ratio = max_width / original_width
            new_height = original_height * scale_ratio

            # 创建新页面并渲染
            new_page = output_pdf.new_page(width=max_width, height=new_height)
            new_page.show_pdf_page(
                new_page.rect,
                doc,
                page.number,
                fitz.Matrix(scale_ratio, scale_ratio)
            )

        # 保存调整后的 PDF
        output_pdf.save(output_path)

    return max_width

def get_max_pdf_width(folder_path: str | Path) -> float:
    """
    检测指定文件夹中所有 PDF 文件中每一页的最大宽度。

    :param folder_path: 输入的文件夹路径
    :return: 所有 PDF 文件中每一页的最大宽度
    """
    folder_path = Path(folder_path)
    if not folder_path.is_dir():
        raise NotADirectoryError(f"错误：'{folder_path}' 不是一个有效的文件夹路径。")

    max_width = 0.0

    # 遍历文件夹中的所有 PDF 文件
    for pdf_file in folder_path.rglob("*.pdf"):
        try:
            with fitz.open(pdf_file) as doc:
                for page in doc:
                    max_width = max(max_width, page.rect.width)
        except Exception as e:
            print(f"警告：处理文件 '{pdf_file}' 时发生错误: {e}")

    return max_width

def resize_pdfs(folder_path: Path, execution_mode: str = 'serial'): 
    def resize_pdf(pdf_path: Path, output_path: Path) -> Path:
        return resize_pdf_to_max_width(pdf_path, output_path, max_pdf_width)
    def rename_pdf(file_path: Path) -> Path:
        name = file_path.stem.replace("_resized", "")
        new_name = f"{name}_resized.pdf"
        return file_path.with_name(new_name)
    
    from tools.FileOperations import handle_folder

    max_pdf_width = get_max_pdf_width(folder_path)
    rules = {'.pdf': (resize_pdf, rename_pdf)}
    return handle_folder(folder_path, rules, execution_mode, progress_desc='Resize PDFs', folder_name_siffix='_resized')
