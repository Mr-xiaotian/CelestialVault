# `celestialvault.tools.DocumentConversion`

> 📅 最后更新日期: 2026/04/21

## 源文件

[src/celestialvault/tools/DocumentConversion.py](../../src/celestialvault/tools/DocumentConversion.py)

## 模块说明

文档转换工具模块，提供 Markdown 转 PDF、PDF 转图片、PDF 压缩、PDF 合并、PDF 页面宽度统一等功能。

## 导入依赖

```python
import shutil
import subprocess
from pathlib import Path

import fitz
import PyPDF2
from PIL import Image
from tqdm import tqdm
```

## 顶层函数

### `md_to_pdf`

- 签名: `def md_to_pdf(md_file_path: str | Path, pdf_file_path: str | Path)`
- 说明: 使用 pandoc 将指定的 Markdown 文件转换为 PDF 文件
- 参数:
  - `md_file_path` (str | Path): 输入的 Markdown 文件路径
  - `pdf_file_path` (str | Path): 输出的 PDF 文件路径
- 返回值: 无
- 用法示例:
  ```python
  from celestialvault.tools.DocumentConversion import md_to_pdf

  md_to_pdf("docs/readme.md", "output/readme.pdf")
  ```
- 关联: 无

### `transfer_pdf_to_img`

- 签名: `def transfer_pdf_to_img(pdf_path: str | Path, img_path: str | Path, dpi: int = 150, quality: int = 85)`
- 说明: 将 PDF 文件转换为图片文件
- 参数:
  - `pdf_path` (str | Path): PDF 文件路径
  - `img_path` (str | Path): 图片输出目录路径
  - `dpi` (int): 图片分辨率(72/150/300)
  - `quality` (int): 图片质量(75/85/95)
- 返回值: 无
- 用法示例:
  ```python
  from celestialvault.tools.DocumentConversion import transfer_pdf_to_img

  transfer_pdf_to_img("document.pdf", "images/", dpi=300, quality=95)
  ```
- 关联: `compress_pdf`

### `compress_pdf`

- 签名: `def compress_pdf(old_pdf_path: str | Path, new_pdf_path: str | Path)`
- 说明: 压缩 PDF，即将 PDF 转换为 jpg 图片，再将图片合并为 PDF
- 参数:
  - `old_pdf_path` (str | Path): 原 PDF 路径
  - `new_pdf_path` (str | Path): 新 PDF 路径
- 返回值: 无
- 用法示例:
  ```python
  from celestialvault.tools.DocumentConversion import compress_pdf

  compress_pdf("large_doc.pdf", "compressed_doc.pdf")
  ```
- 关联: `transfer_pdf_to_img`, `celestialvault.tools.ImageProcessing.combine_imgs_to_pdf`

### `merge_pdfs_in_order`

- 签名: `def merge_pdfs_in_order(dir_path: str | Path, special_keywords: dict = None) -> tuple[list[Path], dict[str, int]]`
- 说明: 将指定文件夹及子文件夹中的所有 PDF 文件按顺序合并，并在输出 PDF 中用目录层级构建书签结构
- 参数:
  - `dir_path` (str | Path): 文件夹路径
  - `special_keywords` (dict): 用于排序的特殊关键字字典
- 返回值: bookmark_dict，包含书签名称与页码的字典
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.DocumentConversion import merge_pdfs_in_order

  bookmarks = merge_pdfs_in_order(Path("pdfs/chapters"), special_keywords={"附录": 1})
  print(bookmarks)
  ```
- 关联: `resize_pdfs`, `celestialvault.tools.FileOperations.dir_to_file_path`, `celestialvault.tools.FileOperations.sort_by_number`

### `resize_pdf_to_max_width`

- 签名: `def resize_pdf_to_max_width(pdf_path: str | Path, output_path: str | Path, max_width: int = None)`
- 说明: 将 PDF 文件中的每一页的宽度调整为最大宽度，保持纵横比不变
- 参数:
  - `pdf_path` (str | Path): 输入 PDF 文件路径
  - `output_path` (str | Path): 输出 PDF 文件路径
  - `max_width` (int): 目标最大宽度，默认为文件中所有页面的最大宽度
- 返回值: 实际使用的最大宽度值
- 用法示例:
  ```python
  from celestialvault.tools.DocumentConversion import resize_pdf_to_max_width

  actual_width = resize_pdf_to_max_width("input.pdf", "output.pdf", max_width=800)
  ```
- 关联: `resize_pdfs`, `get_max_pdf_width`

### `get_max_pdf_width`

- 签名: `def get_max_pdf_width(dir_path: str | Path) -> float`
- 说明: 检测指定文件夹中所有 PDF 文件中每一页的最大宽度
- 参数:
  - `dir_path` (str | Path): 输入的文件夹路径
- 返回值: 所有 PDF 文件中每一页的最大宽度
- 用法示例:
  ```python
  from celestialvault.tools.DocumentConversion import get_max_pdf_width

  max_w = get_max_pdf_width("pdfs/")
  print(f"最大宽度: {max_w}")
  ```
- 关联: `resize_pdfs`, `resize_pdf_to_max_width`

### `resize_pdfs`

- 签名: `def resize_pdfs(dir_path: Path, execution_mode: str = "serial")`
- 说明: 将文件夹中所有 PDF 文件的页面宽度统一调整为最大宽度
- 参数:
  - `dir_path` (Path): 包含 PDF 文件的文件夹路径
  - `execution_mode` (str): 执行模式，默认 "serial"
- 返回值: 处理结果列表
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.DocumentConversion import resize_pdfs

  resize_pdfs(Path("pdfs/mixed_sizes"))
  ```
- 关联: `resize_pdf_to_max_width`, `get_max_pdf_width`, `merge_pdfs_in_order`, `celestialvault.tools.FileOperations.handle_dir_files`
