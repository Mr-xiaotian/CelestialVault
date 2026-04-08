# instances/inst_imgcodecs.py

## 源文件
- `src/celestialvault/instances/inst_imgcodecs.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- `import math`
- `import numpy as np`
- `from itertools import product`
- `from pathlib import Path`
- `from PIL import Image`
- `from tqdm import tqdm`
- `from ..constants import image_mode_params, style_params`
- `from ..tools.ImageProcessing import generate_palette, ensure_capacity`
- `from ..tools.TextTools import crc_encode_text, crc_decode_text, crc_encode_bytes, crc_decode_bytes, add_length_header_to_bytes, restore_bytes_from_length_header, encode_bytes_to_base64, decode_bytes_from_base64, compress_text_to_bytes, decompress_text_from_bytes, rs_encode, rs_decode, pad_bytes, unpad_bytes, pad_to_align, safe_open_txt`
- `from ..tools.NumberUtils import choose_square_container, redundancy_from_container`

## 模块常量
- `CODEC_REGISTRY`

## 顶层函数
- 无

## 类
### `BaseCodec`
- 继承: `object`
- 说明: 所有编码器的基类
- 方法:
  - `def encode_text(self, text: str) -> Image.Image`
  - `def decode_text(self, img: Image.Image) -> str`
  - `def encode_bytes(self, data: bytes) -> Image.Image`
  - `def decode_bytes(self, img: Image.Image) -> bytes`
  - `def encode_txt_file(self, file_path: str | Path, save_img: bool = False) -> Image.Image`
  - `def decode_txt_file(self, img_path: str, save_text: bool = False) -> str`
  - `def encode_binary_file(self, file_path: str | Path, save_img: bool = False) -> Image.Image`
  - `def decode_binary_file(self, img_path: str | Path, save_file: bool = False) -> bytes`
  - `def _encode_text_core(self, text: str) -> Image.Image`
  - `def _decode_text_core(self, img: Image.Image) -> str`
  - `def _encode_bytes_core(self, data: bytes) -> Image.Image`
  - `def _decode_bytes_core(self, img: Image.Image) -> bytes`
  - `def get_new_xy(old_x, old_y, width)`

### `GreyCodec`
- 继承: `BaseCodec`
- 说明: 灰度模式编解码器，使用双像素存储一个 Unicode 字符（高8位 + 低8位）。
- 方法:
  - `def _encode_text_core(self, text: str) -> Image.Image`
  - `def _decode_text_core(self, img: Image.Image) -> str`
  - `def _encode_bytes_core(self, data: bytes) -> Image.Image`
  - `def _decode_bytes_core(self, img: Image.Image) -> bytes`

### `RGBCodec`
- 继承: `BaseCodec`
- 说明: RGB 模式编解码器，使用双像素（6通道）存储 3 个 Unicode 字符。
- 方法:
  - `def _encode_text_core(self, text: str) -> Image.Image`
  - `def _decode_text_core(self, img: Image.Image) -> str`
  - `def _encode_bytes_core(self, data: bytes) -> Image.Image`
  - `def _decode_bytes_core(self, img: Image.Image) -> bytes`

### `RGBACodec`
- 继承: `BaseCodec`
- 说明: RGBA 模式编解码器，使用单像素（4通道）存储 2 个 Unicode 字符。
- 方法:
  - `def _encode_text_core(self, text: str) -> Image.Image`
  - `def _decode_text_core(self, img: Image.Image) -> str`
  - `def _encode_bytes_core(self, data: bytes) -> Image.Image`
  - `def _decode_bytes_core(self, img: Image.Image) -> bytes`

### `OneBitCodec`
- 继承: `BaseCodec`
- 说明: 1-bit 黑白模式编解码器，每个像素存储 1 bit 数据。
- 方法:
  - `def _encode_text_core(self, text: str) -> Image.Image`
  - `def _decode_text_core(self, img: Image.Image) -> str`
  - `def _encode_bytes_core(self, data: bytes) -> Image.Image`
  - `def _decode_bytes_core(self, img: Image.Image) -> bytes`

### `ChannelCodec`
- 继承: `BaseCodec`
- 说明: 通用多通道编解码器，每个像素的各通道各存储 1 字节数据。
- 方法:
  - `def __init__(self, mode_name: str, channels: int)`
  - `def _encode_text_core(self, text: str) -> Image.Image`
  - `def _decode_text_core(self, img: Image.Image) -> str`
  - `def _encode_bytes_core(self, data: bytes) -> Image.Image`
  - `def _decode_bytes_core(self, img: Image.Image) -> bytes`

### `RefRGBALSBCodec`
- 继承: `BaseCodec`
- 说明: RGBA-LSB 通道编码器：
- RGBA 每个通道的低 2 bit 存储数据；
- 每像素可嵌入 1 字节；
- 视觉效果几乎无变化。
- 方法:
  - `def __init__(self, ref_image: str | Path | Image.Image)`
  - `def _encode_text_core(self, text: str) -> Image.Image`
  - `def _decode_text_core(self, img: Image.Image) -> str`
  - `def _encode_bytes_core(self, data: bytes) -> Image.Image`
  - `def _decode_bytes_core(self, img: Image.Image) -> bytes`

### `PaletteCodec`
- 继承: `BaseCodec`
- 说明: 调色板模式编解码器，使用 256 色调色板，每个像素存储 1 字节数据。
- 方法:
  - `def __init__(self, palette_style: str, palatte_mode: str = 'random')`
  - `def _encode_text_core(self, text: str) -> Image.Image`
  - `def _decode_text_core(self, img: Image.Image) -> str`
  - `def _encode_bytes_core(self, data: bytes) -> Image.Image`
  - `def _decode_bytes_core(self, img: Image.Image) -> bytes`

### `PaletteWithRsCodec`
- 继承: `BaseCodec`
- 说明: 带 Reed-Solomon 纠错的调色板编解码器，可容忍一定比例的像素损坏。
- 方法:
  - `def __init__(self, palette_style: str, palatte_mode: str = 'random', threshold: float = 0.7)`
  - `def _encode_text_core(self, text: str) -> Image.Image`
  - `def _decode_text_core(self, img: Image.Image) -> str`
  - `def _encode_bytes_core(self, data: bytes) -> Image.Image`
  - `def _decode_bytes_core(self, img: Image.Image) -> bytes`

### `RedundancyCodec`
- 继承: `BaseCodec`
- 说明: 冗余编解码器，通过多通道旋转写入实现数据冗余存储，解码时以多数投票恢复数据。
- 方法:
  - `def __init__(self, mode_name: str, channels: int)`
  - `def _encode_text_core(self, text: str) -> Image.Image`
  - `def _decode_text_core(self, img: Image.Image) -> str`
  - `def _encode_bytes_core(self, data: bytes) -> Image.Image`
  - `def _decode_bytes_core(self, img: Image.Image) -> bytes`
  - `def _decode_one_channel(self, img: Image.Image, channel_index: int) -> bytes`
