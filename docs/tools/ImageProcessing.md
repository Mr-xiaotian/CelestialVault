# `celestialvault.tools.ImageProcessing`

> 📅 最后更新日期: 2026/04/21

## 源文件

[src/celestialvault/tools/ImageProcessing.py](../../src/celestialvault/tools/ImageProcessing.py)

## 模块说明

图像处理工具模块，提供图片压缩、格式转换、Base64 编解码、调色板生成、图像扩展/恢复、像素提取为 GIF、SSIM 相似度比较、图像有效性检测、PNG 文本块读写、图像损坏模拟、容量自适应调整、像素差异分析等功能。

## 导入依赖

```python
import base64
import io
import math
import random
from colorsys import hsv_to_rgb
from itertools import product
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from celestialflow import TaskExecutor
from PIL import Image, ImageFile, PngImagePlugin
from pillow_heif import register_heif_opener
from tqdm import tqdm

from ..constants import IMAGE_SUFFIX_TO_FORMAT
```

## 顶层函数

### `compress_img`

- 签名: `def compress_img(old_img_path: str | Path, new_img_path: str | Path)`
- 说明: 压缩图片，使用 optimize 和 quality=75 进行有损压缩
- 参数:
  - `old_img_path` (str | Path): 原始图片文件路径
  - `new_img_path` (str | Path): 压缩后图片文件路径
- 返回值: 无
- 用法示例:
  ```python
  from celestialvault.tools.ImageProcessing import compress_img

  compress_img("photo.jpg", "photo_compressed.jpg")
  ```
- 关联: `celestialvault.tools.FileOperations.compress_dir`

### `safe_open_image`

- 签名: `def safe_open_image(path: Path) -> tuple[Image.Image | None, bool]`
- 说明: 安全地打开一张图片并返回 Image 对象，先验证再加载进内存
- 参数:
  - `path` (Path): 图片文件路径
- 返回值: 元组 (Image 对象或 None, 是否成功)
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.ImageProcessing import safe_open_image

  img, ok = safe_open_image(Path("photo.jpg"))
  if ok:
      print(img.size)
  ```
- 关联: `combine_imgs_to_pdf`

### `combine_imgs_to_pdf`

- 签名: `def combine_imgs_to_pdf(root_path: str | Path, pdf_path: str | Path = None, special_keywords: dict = None)`
- 说明: 将指定文件夹中的图片组合成单个 PDF 文件
- 参数:
  - `root_path` (str | Path): 包含图片的文件夹路径
  - `pdf_path` (str | Path): 输出的 PDF 文件路径，默认使用文件夹同名 PDF
  - `special_keywords` (dict): 特殊关键词用于排序。例如 `{'番外': 1, '特典': 1, '原画': 2}`
- 返回值: 无
- 用法示例:
  ```python
  from celestialvault.tools.ImageProcessing import combine_imgs_to_pdf

  combine_imgs_to_pdf("manga/chapter1/", special_keywords={"番外": 1})
  ```
- 关联: `safe_open_image`, `celestialvault.tools.FileOperations.dir_to_file_path`, `celestialvault.tools.FileOperations.sort_by_number`, `celestialvault.tools.DocumentConversion.compress_pdf`

### `combine_imgs_dir`

- 签名: `def combine_imgs_dir(dir_path: Path, special_keywords: dict = None)`
- 说明: 批量将多个子文件夹中的图片分别组合成 PDF 文件
- 参数:
  - `dir_path` (Path): 包含图片子文件夹的路径
  - `special_keywords` (dict): 特殊关键词用于排序
- 返回值: 处理结果
- 用法示例:
  ```python
  from pathlib import Path
  from celestialvault.tools.ImageProcessing import combine_imgs_dir

  combine_imgs_dir(Path("manga/"), special_keywords={"番外": 1})
  ```
- 关联: `combine_imgs_to_pdf`, `celestialvault.tools.FileOperations.handle_subdirs`, `celestialvault.tools.FileOperations.dir_to_file_path`

### `img_to_binary`

- 签名: `def img_to_binary(img: Image.Image) -> bytes`
- 说明: 将 Image 对象转换为 PNG 格式的二进制数据
- 参数:
  - `img` (Image.Image): PIL Image 对象
- 返回值: PNG 格式的二进制数据
- 用法示例:
  ```python
  from PIL import Image
  from celestialvault.tools.ImageProcessing import img_to_binary

  img = Image.new("RGB", (100, 100), "red")
  data = img_to_binary(img)
  ```
- 关联: `binary_to_img`, `img_to_base64`

### `binary_to_img`

- 签名: `def binary_to_img(binary_img: bytes) -> Image.Image`
- 说明: 将二进制数据转换为 Image 对象
- 参数:
  - `binary_img` (bytes): 图片的二进制数据
- 返回值: PIL Image 对象
- 用法示例:
  ```python
  from celestialvault.tools.ImageProcessing import binary_to_img

  img = binary_to_img(png_bytes)
  img.show()
  ```
- 关联: `img_to_binary`, `base64_to_img`

### `convert_img_format`

- 签名: `def convert_img_format(img: Image.Image, img_format: str) -> Image.Image`
- 说明: 将 Image 对象转换为指定格式，并返回转换后的 Image 对象
- 参数:
  - `img` (Image.Image): PIL Image 对象
  - `img_format` (str): 目标图片格式或后缀，如 PNG、JPEG、WEBP、.jpg
- 返回值: 转换格式后的 Image 对象
- 用法示例:
  ```python
  from PIL import Image
  from celestialvault.tools.ImageProcessing import convert_img_format

  img = Image.open("photo.png")
  jpeg_img = convert_img_format(img, "JPEG")
  ```
- 关联: 无

### `base64_to_img`

- 签名: `def base64_to_img(base64_str: str) -> Image.Image`
- 说明: 将 Base64 编码的字符串解码并转换为 PIL Image 对象
- 参数:
  - `base64_str` (str): Base64 编码的图片字符串
- 返回值: 解码后的 PIL Image 对象
- 用法示例:
  ```python
  from celestialvault.tools.ImageProcessing import base64_to_img

  img = base64_to_img(encoded_str)
  img.show()
  ```
- 关联: `binary_to_img`, `img_to_base64`

### `img_to_base64`

- 签名: `def img_to_base64(img: Image.Image) -> str`
- 说明: 将 PIL Image 对象转换为 Base64 编码的字符串
- 参数:
  - `img` (Image.Image): PIL Image 对象
- 返回值: Base64 编码的字符串
- 用法示例:
  ```python
  from PIL import Image
  from celestialvault.tools.ImageProcessing import img_to_base64

  img = Image.open("photo.png")
  encoded = img_to_base64(img)
  ```
- 关联: `img_to_binary`, `base64_to_img`

### `generate_palette`

- 签名: `def generate_palette(color_num: int = 256, style: str = "morandi", mode: str = "random", random_seed: int = 0) -> list[int]`
- 说明: 生成调色板，支持随机、均匀和螺旋三种模式，并确保颜色唯一或规律分布
- 参数:
  - `color_num` (int): 要生成的颜色数量
  - `style` (str): 调色板风格，可选 'morandi', 'grey', 'hawaiian', 'deepsea', 'twilight', 'sunrise', 'cyberpunk', 'autumn' 等
  - `mode` (str): 颜色生成模式，可选 'random', 'uniform', 'spiral'
  - `random_seed` (int): 随机种子，用于生成可重复的随机颜色
- 返回值: 返回生成的颜色平铺列表 [r, g, b, r, g, b, ...]
- 用法示例:
  ```python
  from celestialvault.tools.ImageProcessing import generate_palette, palette_to_image

  palette = generate_palette(64, style="cyberpunk", mode="spiral")
  img = palette_to_image(palette)
  img.show()
  ```
- 关联: `palette_to_image`

### `palette_to_image`

- 签名: `def palette_to_image(palette, block_size=50)`
- 说明: 根据颜色列表生成调色板图像
- 参数:
  - `palette`: 一个包含 RGB 颜色的平铺列表，例如 [r, g, b, r, g, b, ...]
  - `block_size` (int): 每个颜色块的像素大小，默认 50
- 返回值: 生成的调色板图像
- 用法示例:
  ```python
  from celestialvault.tools.ImageProcessing import generate_palette, palette_to_image

  palette = generate_palette(256)
  img = palette_to_image(palette, block_size=30)
  img.save("palette.png")
  ```
- 关联: `generate_palette`, `expand_image`

### `expand_image`

- 签名: `def expand_image(image: Image.Image, expand_factor: int = 50) -> Image.Image`
- 说明: 将图像中的每个像素点扩大为 n x n 的块
- 参数:
  - `image` (Image.Image): 要处理的图像
  - `expand_factor` (int): 扩展因子，默认 50
- 返回值: 扩展后的图像
- 用法示例:
  ```python
  from PIL import Image
  from celestialvault.tools.ImageProcessing import expand_image

  small = Image.new("RGB", (4, 4), "blue")
  big = expand_image(small, 100)
  big.save("expanded.png")
  ```
- 关联: `restore_expanded_image`, `palette_to_image`

### `restore_expanded_image`

- 签名: `def restore_expanded_image(expanded_image: Image.Image, expand_factor: int = 50) -> Image.Image`
- 说明: 将扩展后的图像恢复为原始大小
- 参数:
  - `expanded_image` (Image.Image): 要恢复的扩展图像
  - `expand_factor` (int): 扩展因子，默认 50
- 返回值: 恢复后的原始大小图像
- 用法示例:
  ```python
  from celestialvault.tools.ImageProcessing import expand_image, restore_expanded_image

  restored = restore_expanded_image(expanded_img, 50)
  ```
- 关联: `expand_image`

### `extract_pixels_as_gif`

- 签名: `def extract_pixels_as_gif(image: Image.Image, frame_size=200, duration=100, loop=0)`
- 说明: 将每个像素点提取出来作为 GIF 中的一帧
- 参数:
  - `image` (Image.Image): 要处理的图像
  - `frame_size` (int): 每帧图像的大小
  - `duration` (int): 每帧显示的持续时间（毫秒）
  - `loop` (int): GIF 循环次数，0 表示无限循环
- 返回值: 包含 GIF 数据的 BytesIO 对象
- 用法示例:
  ```python
  from PIL import Image
  from celestialvault.tools.ImageProcessing import extract_pixels_as_gif

  small_img = Image.new("RGB", (4, 4), "red")
  gif_io = extract_pixels_as_gif(small_img, frame_size=100, duration=200)
  with open("pixels.gif", "wb") as f:
      f.write(gif_io.read())
  ```
- 关联: 无

### `compare_ssim_by_path`

- 签名: `def compare_ssim_by_path(path1: Path | str, path2: Path | str) -> float`
- 说明: 比较两张图像的结构相似性指数（SSIM）
- 参数:
  - `path1` (Path | str): 第一张图像的路径
  - `path2` (Path | str): 第二张图像的路径
- 返回值: 两张图像的 SSIM 值，范围在 -1 到 1 之间，值越大表示越相似
- 用法示例:
  ```python
  from celestialvault.tools.ImageProcessing import compare_ssim_by_path

  ssim = compare_ssim_by_path("img1.jpg", "img2.jpg")
  print(f"SSIM: {ssim:.4f}")
  ```
- 关联: `compare_images_by_ssim`

### `compare_images_by_ssim`

- 签名: `def compare_images_by_ssim(dir1: Path | str, dir2: Path | str) -> pd.DataFrame`
- 说明: 比较两个文件夹中的同名图像，计算它们的 SSIM 值
- 参数:
  - `dir1` (Path | str): 第一个文件夹的路径
  - `dir2` (Path | str): 第二个文件夹的路径
- 返回值: 包含文件名和 SSIM 值的 DataFrame
- 用法示例:
  ```python
  from celestialvault.tools.ImageProcessing import compare_images_by_ssim

  df = compare_images_by_ssim("original/", "compressed/")
  print(df)
  ```
- 关联: `compare_ssim_by_path`, `CompareSSIMExecutor`

### `is_image_valid`

- 签名: `def is_image_valid(data: str | Path | io.BytesIO) -> bool`
- 说明: 检测图片是否有效
- 参数:
  - `data` (str | Path | io.BytesIO): 图片的路径、文件对象或二进制数据
- 返回值: True 表示正常，False 表示损坏或格式不符
- 用法示例:
  ```python
  from celestialvault.tools.ImageProcessing import is_image_valid

  print(is_image_valid("photo.jpg"))  # True or False
  ```
- 关联: `is_image_bytes_valid`

### `is_image_bytes_valid`

- 签名: `def is_image_bytes_valid(byte_data: bytes) -> bool`
- 说明: 检测二进制图片数据是否有效
- 参数:
  - `byte_data` (bytes): 图片的二进制内容
- 返回值: True 表示正常，False 表示损坏或格式不符
- 用法示例:
  ```python
  from celestialvault.tools.ImageProcessing import is_image_bytes_valid

  with open("photo.jpg", "rb") as f:
      print(is_image_bytes_valid(f.read()))
  ```
- 关联: `is_image_valid`

### `create_image_with_text_chunk`

- 签名: `def create_image_with_text_chunk(img: Image.Image, output_path: str, messages: dict[str, str])`
- 说明: 将文本字典写入 PNG 文件的 tEXt chunk 中
- 参数:
  - `img` (Image.Image): PIL.Image 对象
  - `output_path` (str): 输出文件路径
  - `messages` (dict[str, str]): 键值对形式的文本信息
- 返回值: 无
- 用法示例:
  ```python
  from PIL import Image
  from celestialvault.tools.ImageProcessing import create_image_with_text_chunk

  img = Image.new("RGB", (100, 100), "white")
  create_image_with_text_chunk(img, "output.png", {"author": "Alice", "title": "Test"})
  ```
- 关联: `read_text_chunks`

### `read_text_chunks`

- 签名: `def read_text_chunks(img_path: str) -> dict[str, str]`
- 说明: 从 PNG 文件中读取所有 tEXt chunk 信息
- 参数:
  - `img_path` (str): PNG 文件路径
- 返回值: 包含所有文本块的字典
- 用法示例:
  ```python
  from celestialvault.tools.ImageProcessing import read_text_chunks

  chunks = read_text_chunks("output.png")
  print(chunks)  # {'author': 'Alice', 'title': 'Test'}
  ```
- 关联: `create_image_with_text_chunk`

### `simulate_rectangle_damage`

- 签名: `def simulate_rectangle_damage(img: Image.Image, x0: int, y0: int, w: int, h: int) -> Image.Image`
- 说明: 在图像上指定位置生成一个 w x h 的损坏矩形（置零）
- 参数:
  - `img` (Image.Image): 原始图像
  - `x0` (int): 矩形左上角 x 坐标
  - `y0` (int): 矩形左上角 y 坐标
  - `w` (int): 矩形宽度
  - `h` (int): 矩形高度
- 返回值: 损坏后的图像
- 用法示例:
  ```python
  from PIL import Image
  from celestialvault.tools.ImageProcessing import simulate_rectangle_damage

  img = Image.open("photo.png")
  damaged = simulate_rectangle_damage(img, 50, 50, 100, 100)
  damaged.save("damaged.png")
  ```
- 关联: `simulate_random_damage`

### `simulate_random_damage`

- 签名: `def simulate_random_damage(img: Image.Image, damage_ratio: float) -> Image.Image`
- 说明: 随机损坏图像的一部分像素（置零）
- 参数:
  - `img` (Image.Image): 原始图像
  - `damage_ratio` (float): 损坏比例 (0~1)，表示要损坏的像素数占总像素的比例
- 返回值: 损坏后的图像
- 用法示例:
  ```python
  from PIL import Image
  from celestialvault.tools.ImageProcessing import simulate_random_damage

  img = Image.open("photo.png")
  damaged = simulate_random_damage(img, 0.1)
  ```
- 关联: `simulate_rectangle_damage`

### `ensure_capacity`

- 签名: `def ensure_capacity(ref_img: Image.Image, required_bytes: int, *, min_able: bool = True, min_size: int = 1) -> Image.Image`
- 说明: 自动调整图像尺寸，使其容量刚好匹配存储需求。当容量不足时放大，当容量过剩时缩小
- 参数:
  - `ref_img` (Image.Image): 参考图像
  - `required_bytes` (int): 需要存储的字节数
  - `min_able` (bool): 是否允许缩小图像，默认 True
  - `min_size` (int): 图像的最小宽高限制
- 返回值: 调整后的图像
- 用法示例:
  ```python
  from PIL import Image
  from celestialvault.tools.ImageProcessing import ensure_capacity

  ref = Image.new("RGBA", (100, 100))
  resized = ensure_capacity(ref, 50000)
  print(resized.size)
  ```
- 关联: `compare_random_pixels`, `show_diff_heatmap`

### `compare_random_pixels`

- 签名: `def compare_random_pixels(ref_img: Image.Image, enc_img: Image.Image, sample_num: int = 20)`
- 说明: 在随机点位比较两张图的像素差异，打印每个点位的 RGB(A) 值差异及整体平均差
- 参数:
  - `ref_img` (Image.Image): 参考原图
  - `enc_img` (Image.Image): 编码后的图像
  - `sample_num` (int): 随机抽样的像素数量，默认 20
- 返回值: 无
- 用法示例:
  ```python
  from PIL import Image
  from celestialvault.tools.ImageProcessing import compare_random_pixels

  ref = Image.open("original.png")
  enc = Image.open("encoded.png")
  compare_random_pixels(ref, enc, sample_num=10)
  ```
- 关联: `ensure_capacity`, `celestialvault.tools.TextTools.format_table`

### `show_diff_heatmap`

- 签名: `def show_diff_heatmap(ref_img: Image.Image, enc_img: Image.Image, save_path: str = None, show: bool = True)`
- 说明: 生成两张图像的像素差异热力图
- 参数:
  - `ref_img` (Image.Image): 原图
  - `enc_img` (Image.Image): 编码图
  - `save_path` (str): 保存路径（可选）
  - `show` (bool): 是否显示结果
- 返回值: 差异强度矩阵，每像素的平均通道差异值
- 用法示例:
  ```python
  from PIL import Image
  from celestialvault.tools.ImageProcessing import show_diff_heatmap

  ref = Image.open("original.png")
  enc = Image.open("encoded.png")
  diff = show_diff_heatmap(ref, enc, save_path="heatmap.png", show=False)
  ```
- 关联: `ensure_capacity`

## 类

### `CompareSSIMExecutor`

- 继承: `TaskExecutor` (from celestialflow)
- 说明: SSIM 比较执行器，批量计算图像对的结构相似性并汇总结果
- 关联: `compare_images_by_ssim`
