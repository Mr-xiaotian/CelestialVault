# tools/DocumentConversion.py

## 源文件
- `src/celestialvault/tools/DocumentConversion.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- `import shutil`
- `import subprocess`
- `from pathlib import Path`
- `import fitz`
- `import PyPDF2`
- `from PIL import Image`
- `from tqdm import tqdm`

## 模块常量
- 无

## 顶层函数
### `md_to_pdf`
- 签名: `def md_to_pdf(md_file_path: str | Path, pdf_file_path: str | Path)`
- 说明: 使用pandoc将指定的Markdown文件转换为PDF文件。

:param md_file_path: 输入的Markdown文件路径
:param pdf_file_path: 输出的PDF文件路径

### `transfer_pdf_to_img`
- 签名: `def transfer_pdf_to_img(pdf_path: str | Path, img_path: str | Path, dpi: int = 150, quality: int = 85)`
- 说明: 将PDF文件转换为图片文件

:param pdf_path: PDF文件路径
:param img_path: 图片文件路径
:param dpi: 图片分辨率(72/150/300)
:param quality: 图片质量(75/85/95)
:return: None

### `compress_pdf`
- 签名: `def compress_pdf(old_pdf_path: str | Path, new_pdf_path: str | Path)`
- 说明: 压缩PDF，即将PDF转换为jpg图片，再将图片合并为PDF

:param old_pdf_path: 原PDF路径
:param new_pdf_path: 新PDF路径
:return: None

### `merge_pdfs_in_order`
- 签名: `def merge_pdfs_in_order(dir_path: str | Path, special_keywords: dict = None) -> tuple[list[Path], dict[str, int]]`
- 说明: 将指定文件夹及子文件夹中的所有 PDF 文件按顺序合并，
并在输出 PDF 中用目录层级构建书签结构。

:param dir_path: 文件夹路径
:param special_keywords: 用于排序的特殊关键字字典
:return: (pdf_files, bookmark_dict)

### `resize_pdf_to_max_width`
- 签名: `def resize_pdf_to_max_width(pdf_path: str | Path, output_path: str | Path, max_width: int = None)`
- 说明: 将 PDF 文件中的每一页的宽度调整为最大宽度，保持纵横比不变。

:param pdf_path: 输入 PDF 文件路径
:param output_path: 输出 PDF 文件路径
:return: None

### `get_max_pdf_width`
- 签名: `def get_max_pdf_width(dir_path: str | Path) -> float`
- 说明: 检测指定文件夹中所有 PDF 文件中每一页的最大宽度。

:param dir_path: 输入的文件夹路径
:return: 所有 PDF 文件中每一页的最大宽度

### `resize_pdfs`
- 签名: `def resize_pdfs(dir_path: Path, execution_mode: str = 'serial')`
- 说明: 批量调整文件夹中所有 PDF 文件的页面宽度为该文件夹中所有 PDF 的最大页面宽度。
  内部调用 `get_max_pdf_width` 检测最大宽度，再通过 `handle_dir_files` 批量处理。

:param dir_path: 文件夹路径
:param execution_mode: 执行模式，可以是 'serial' 或 'thread' 'process'。默认为 'serial'。

## 类
- 无
