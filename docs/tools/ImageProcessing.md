# tools/ImageProcessing.py

## 源文件
- `src/celestialvault/tools/ImageProcessing.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- `import base64`
- `import io`
- `import math`
- `import random`
- `from colorsys import hsv_to_rgb`
- `from itertools import product`
- `from pathlib import Path`
- `import numpy as np`
- `import pandas as pd`
- `import matplotlib.pyplot as plt`
- `from PIL import Image, PngImagePlugin, ImageFile`
- `from pillow_heif import register_heif_opener`
- `from skimage.metrics import structural_similarity as compare_ssim`
- `from tqdm import tqdm`
- `from celestialflow import TaskExecutor`

## 模块常量
- 无

## 顶层函数
### `compress_img`
- 签名: `def compress_img(old_img_path: str | Path, new_img_path: str | Path)`
- 说明: 压缩图片

### `safe_open_image`
- 签名: `def safe_open_image(path: Path) -> tuple[Image.Image | None, bool]`
- 说明: 安全地打开一张图片并返回Image对象。

### `combine_imgs_to_pdf`
- 签名: `def combine_imgs_to_pdf(root_path: str | Path, pdf_path: str | Path = None, special_keywords: dict = None)`
- 说明: 将指定文件夹中的JPEG图片组合成单个PDF文件。

:param root_path: 包含JPEG图片的文件夹路径。
:param pdf_path: 输出的PDF文件路径。
:return: None

### `combine_imgs_dir`
- 签名: `def combine_imgs_dir(dir_path: Path, special_keywords: dict = None)`
- 说明: 将指定文件夹中的JPEG图片组合成单个PDF文件。

:param dir_path: 包含JPEG图片的文件夹路径。
:param special_keywords: 特殊关键词，用于排序图片。eg: {'番外': 1, '特典': 1, '原画': 2}
:return: None

### `img_to_binary`
- 签名: `def img_to_binary(img: Image.Image) -> bytes`
- 说明: 将Image对象转换为二进制数据。

### `binary_to_img`
- 签名: `def binary_to_img(binary_img: bytes) -> Image.Image`
- 说明: 将二进制数据转换为Image对象

### `convert_img_format`
- 签名: `def convert_img_format(img: Image.Image, img_format: str) -> Image.Image`
- 说明: 将 Image 对象转换为指定格式，并返回转换后的 Image 对象。

:param img: PIL Image 对象。
:param img_format: 目标图片格式或后缀，如 PNG、JPEG、WEBP、.jpg。
:return: 转换格式后的 Image 对象。

### `base64_to_img`
- 签名: `def base64_to_img(base64_str: str) -> Image.Image`
- 说明: 将 Base64 编码的字符串解码并转换为 PIL Image 对象。

:param base64_str: Base64 编码的图片字符串。
:return: 解码后的 PIL Image 对象。

### `img_to_base64`
- 签名: `def img_to_base64(img: Image.Image) -> str`
- 说明: 将 PIL Image 对象转换为 Base64 编码的字符串。

:param img: PIL Image 对象。
:return: Base64 编码的字符串。

### `generate_palette`
- 签名: `def generate_palette(color_num: int = 256, style: str = 'morandi', mode: str = 'random', random_seed: int = 0) -> list[int]`
- 说明: 生成调色板，支持随机 均匀和螺旋三种模式，并确保颜色唯一或规律分布。

:param color_num: 要生成的颜色数量
:param style: 调色板风格，可选 'morandi', 'grey', 'hawaiian', 'deepsea', 'twilight', 'sunrise', 'cyberpunk', 'autumn'等
:param mode: 颜色生成模式，可选 'random' 'uniform', 'spiral'
:param random_seed: 随机种子，用于生成可重复的随机颜色
:return: 返回生成的颜色列表

### `palette_to_image`
- 签名: `def palette_to_image(palette, block_size = 50)`
- 说明: 根据颜色列表生成调色板图像。

:param palette: 一个包含 RGB 颜色的平铺列表或元组，例如 [r, g, b, r, g, b, ...]
:param block_size: 每个颜色块的像素大小，默认 50

### `expand_image`
- 签名: `def expand_image(image: Image.Image, expand_factor: int = 50) -> Image.Image`
- 说明: 将图像中的每个像素点扩大为n x n的块

:param image: 要处理的图像。如果是调色板图像（P模式），将其转换为RGB模式。
:param block_size: 扩展因子，默认 50

### `restore_expanded_image`
- 签名: `def restore_expanded_image(expanded_image: Image.Image, expand_factor: int = 50) -> Image.Image`
- 说明: 将扩展后的图像恢复为原始大小

:param expanded_image: 要恢复的扩展图像
:param expand_factor: 扩展因子，默认为50

### `extract_pixels_as_gif`
- 签名: `def extract_pixels_as_gif(image: Image.Image, frame_size = 200, duration = 100, loop = 0)`
- 说明: 将每个像素点提取出来作为GIF中的一帧。

:param image: 要处理的图像。如果是调色板图像（P模式），将其转换为RGB模式。
:param frame_size: 每帧图像的大小。
:param duration: 每帧显示的持续时间（毫秒）。
:param loop: GIF循环的次数，0表示无限循环。

### `compare_ssim_by_path`
- 签名: `def compare_ssim_by_path(path1: Path | str, path2: Path | str) -> float`
- 说明: 比较两张图像的结构相似性指数（SSIM）。

:param path1: 第一张图像的路径。
:param path2: 第二张图像的路径。
:return: 两张图像的SSIM值，范围在-1到1之间，值越大表示越相似。

### `compare_images_by_ssim`
- 签名: `def compare_images_by_ssim(dir1: Path | str, dir2: Path | str) -> pd.DataFrame`
- 说明: 比较两个文件夹中的图像，计算它们的 SSIM 值，并返回一个包含文件名和 SSIM 值的 DataFrame。

:param dir1: 第一个文件夹的路径。
:param dir2: 第二个文件夹的路径。
:return: 包含文件名和 SSIM 值的 DataFrame。

### `is_image_valid`
- 签名: `def is_image_valid(data: str | Path | io.BytesIO) -> bool`
- 说明: 检测图片是否有效

:param data: 图片的路径、文件对象或二进制数据
:return: True 表示正常，False 表示损坏或格式不符

### `is_image_bytes_valid`
- 签名: `def is_image_bytes_valid(byte_data: bytes) -> bool`
- 说明: 检测二进制图片数据是否有效

:param byte_data: 图片的二进制内容
:return: True 表示正常，False 表示损坏或格式不符

### `create_image_with_text_chunk`
- 签名: `def create_image_with_text_chunk(img: Image.Image, output_path: str, messages: dict[str, str])`
- 说明: 将文本字典写入 PNG 文件的 tEXt chunk 中

:param img: PIL.Image 对象
:param output_path: 输出文件路径
:param messages: 键值对形式的文本信息

### `read_text_chunks`
- 签名: `def read_text_chunks(img_path: str) -> dict[str, str]`
- 说明: 从 PNG 文件中读取所有 tEXt chunk 信息

:param img_path: PNG 文件路径
:return: 包含所有文本块的字典

### `simulate_rectangle_damage`
- 签名: `def simulate_rectangle_damage(img: Image.Image, x0: int, y0: int, w: int, h: int) -> Image.Image`
- 说明: 在图像上指定位置生成一个 w×h 的损坏矩形（置零）。

:param img: 原始图像
:param x0: 矩形左上角 x 坐标
:param y0: 矩形左上角 y 坐标
:param w: 矩形宽度
:param h: 矩形高度
:return: 损坏后的图像

### `simulate_random_damage`
- 签名: `def simulate_random_damage(img: Image.Image, damage_ratio: float) -> Image.Image`
- 说明: 随机损坏图像的一部分像素（置零）。

:param img: 原始图像 (RGBA)
:param damage_ratio: 损坏比例 (0~1)，表示要损坏的像素数占总像素的比例
:return: 损坏后的图像

### `ensure_capacity`
- 签名: `def ensure_capacity(ref_img: Image.Image, required_bytes: int, *, min_able: bool = True, min_size: int = 1) -> Image.Image`
- 说明: 自动调整图像尺寸，使其容量刚好匹配存储需求。
- 当容量不足时放大；
- 当容量过剩时缩小；
- 保留视觉结构尽量不失真。

:param ref_img: 参考图像 (RGBA)
:param required_bytes: 需要存储的字节数
:param min_size: 图像的最小宽高限制
:return: 调整后的图像 (RGBA)

### `compare_random_pixels`
- 签名: `def compare_random_pixels(ref_img: Image.Image, enc_img: Image.Image, sample_num: int = 20)`
- 说明: 在随机点位比较两张图的像素差异。
打印每个点位的 RGB(A) 值差异，以及整体平均差。

### `show_diff_heatmap`
- 签名: `def show_diff_heatmap(ref_img: Image.Image, enc_img: Image.Image, save_path: str = None, show: bool = True)`
- 说明: 生成两张图像的像素差异热力图。
:param ref_img: 原图 (PIL.Image)
:param enc_img: 编码图 (PIL.Image)
:param save_path: 保存路径（可选）
:param show: 是否显示结果

## 类
### `CompareSSIMExecutor`
- 继承: `TaskExecutor`
- 说明: SSIM 比较执行器，批量计算图像对的结构相似性并汇总结果。
- 方法:
  - `def process_result_dict(self)`
