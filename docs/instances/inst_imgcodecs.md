# `celestialvault.instances.inst_imgcodecs`

> 📅 最后更新日期: 2026/04/21

## 源文件 - `src/celestialvault/instances/inst_imgcodecs.py`

## 模块说明

提供多种图像编解码器，将文本或二进制数据编码为图像，或从图像中解码还原数据。所有编解码器继承自 `BaseCodec` 基类，支持文本、二进制和文件级别的编解码操作。模块末尾通过 `CODEC_REGISTRY` 字典注册所有可用编解码器。

## 导入依赖

- `math` - 数学计算
- `numpy` - 数组操作
- `itertools.product` - 笛卡尔积
- `pathlib.Path` - 路径操作
- `PIL.Image` - 图像处理
- `tqdm` - 进度条
- `celestialvault.constants.image_mode_params` - 图像模式参数
- `celestialvault.constants.style_params` - 调色板风格参数
- `celestialvault.tools.ImageProcessing.generate_palette` - 调色板生成
- `celestialvault.tools.ImageProcessing.ensure_capacity` - 容量检查
- `celestialvault.tools.TextTools` - CRC 编解码、压缩解压、Base64、RS 纠错、填充等
- `celestialvault.tools.NumberUtils.choose_square_container` - 正方形容器选择
- `celestialvault.tools.NumberUtils.redundancy_from_container` - 冗余计算

## 类

### `BaseCodec`

- 继承: 无
- 说明: 所有编码器的基类，提供文本/二进制/文件级别的编解码公共接口。子类需实现 `_encode_text_core`、`_decode_text_core`、`_encode_bytes_core`、`_decode_bytes_core` 四个方法。
- 类属性:
  - `mode_name` (`str`): 编码模式名称，默认 `""`。
  - `show_progress` (`bool`): 是否显示进度条，默认 `True`。

- 方法:

  #### `encode_text(self, text)`
  - 签名: `encode_text(self, text: str) -> Image.Image`
  - 说明: 对文本加上 CRC 后再调用子类实现的像素编码。
  - 参数: `text` (`str`): 要编码的文本。
  - 返回值: 编码后的 `Image` 对象。

  #### `decode_text(self, img)`
  - 签名: `decode_text(self, img: Image.Image) -> str`
  - 说明: 对像素数据解码后，再做 CRC 校验。
  - 参数: `img` (`Image.Image`): 编码图像。
  - 返回值: 解码后的文本字符串。

  #### `encode_bytes(self, data)`
  - 签名: `encode_bytes(self, data: bytes) -> Image.Image`
  - 说明: 对二进制数据加上 CRC 和长度头后再编码为图像。
  - 参数: `data` (`bytes`): 要编码的二进制数据。
  - 返回值: 编码后的 `Image` 对象。

  #### `decode_bytes(self, img)`
  - 签名: `decode_bytes(self, img: Image.Image) -> bytes`
  - 说明: 从图像解码并还原 CRC 校验后的二进制数据。
  - 参数: `img` (`Image.Image`): 编码图像。
  - 返回值: 解码后的二进制数据。

  #### `encode_txt_file(self, file_path, save_img=False)`
  - 签名: `encode_txt_file(self, file_path: str | Path, save_img: bool = False) -> Image.Image`
  - 说明: 读取文本文件并编码为图像。输出文件名格式: `<原文件名>(<mode_name>)(<原扩展名>).png`。
  - 参数:
    - `file_path` (`str | Path`): 文本文件路径。
    - `save_img` (`bool`): 是否将编码后的图像保存到磁盘。
  - 返回值: 编码后的 `Image` 对象。

  #### `decode_txt_file(self, img_path, save_text=False)`
  - 签名: `decode_txt_file(self, img_path: str, save_text: bool = False) -> str`
  - 说明: 从图像文件中解码还原文本内容。从文件名中解析原始扩展名。
  - 参数:
    - `img_path` (`str`): 编码图像的文件路径。
    - `save_text` (`bool`): 是否将解码后的文本保存到磁盘。
  - 返回值: 解码后的文本字符串。

  #### `encode_binary_file(self, file_path, save_img=False)`
  - 签名: `encode_binary_file(self, file_path: str | Path, save_img: bool = False) -> Image.Image`
  - 说明: 读取任意二进制文件并编码为图像。输出文件名格式: `<原文件名>(<mode_name>)(<原扩展名>).png`。
  - 参数:
    - `file_path` (`str | Path`): 二进制文件路径。
    - `save_img` (`bool`): 是否将编码后的图像保存到磁盘。
  - 返回值: 编码后的 `Image` 对象。

  #### `decode_binary_file(self, img_path, save_file=False)`
  - 签名: `decode_binary_file(self, img_path: str | Path, save_file: bool = False) -> bytes`
  - 说明: 从图像文件中恢复二进制数据。从文件名中解析原始扩展名。
  - 参数:
    - `img_path` (`str | Path`): 编码图像的文件路径。
    - `save_file` (`bool`): 是否将解码后的二进制数据保存到磁盘。
  - 返回值: 解码后的二进制数据。

  #### `get_new_xy(old_x, old_y, width)` (静态方法)
  - 签名: `get_new_xy(old_x, old_y, width) -> tuple[int, int]`
  - 说明: 计算下一个像素坐标，到达行尾时换行。
  - 参数:
    - `old_x` (`int`): 当前 x 坐标。
    - `old_y` (`int`): 当前 y 坐标。
    - `width` (`int`): 图像宽度。
  - 返回值: `(新 x 坐标, 新 y 坐标)` 元组。

---

### `GreyCodec`

- 继承: `BaseCodec`
- 说明: 灰度模式编解码器，使用双像素存储一个 Unicode 字符（高8位 + 低8位）。
- `mode_name`: `"grey_ori"`
- 二进制编解码通过 Base64 转换后复用文本编解码实现。

---

### `RGBCodec`

- 继承: `BaseCodec`
- 说明: RGB 模式编解码器，使用双像素（6通道）存储 3 个 Unicode 字符。
- `mode_name`: `"rgb_ori"`
- 二进制编解码通过 Base64 转换后复用文本编解码实现。

---

### `RGBACodec`

- 继承: `BaseCodec`
- 说明: RGBA 模式编解码器，使用单像素（4通道）存储 2 个 Unicode 字符。
- `mode_name`: `"rgba_ori"`
- 二进制编解码通过 Base64 转换后复用文本编解码实现。

---

### `OneBitCodec`

- 继承: `BaseCodec`
- 说明: 1-bit 黑白模式编解码器，每个像素存储 1 bit 数据。文本先压缩为二进制再编码。
- `mode_name`: `"1bit"`

---

### `ChannelCodec`

- 继承: `BaseCodec`
- 说明: 通用多通道编解码器，每个像素的各通道各存储 1 字节数据。文本先压缩为二进制再编码。数据按通道数对齐填充。

- 构造函数: `__init__(self, mode_name: str, channels: int)`
  - 参数:
    - `mode_name` (`str`): 图像模式名称，如 `'RGB'`、`'RGBA'`、`'L'`。
    - `channels` (`int`): 通道数。

---

### `RefRGBALSBCodec`

- 继承: `BaseCodec`
- 说明: RGBA-LSB 通道编码器，使用参考图像的 RGBA 每通道低 2 bit 存储数据，每像素可嵌入 1 字节，视觉效果几乎无变化（隐写术）。

- 构造函数: `__init__(self, ref_image: str | Path | Image.Image)`
  - 参数:
    - `ref_image` (`str | Path | Image.Image`): 参考图像，可以是路径或 Image 对象。自动转换为 RGBA 模式。

---

### `PaletteCodec`

- 继承: `BaseCodec`
- 说明: 调色板模式编解码器，使用 256 色调色板，每个像素存储 1 字节数据。

- 构造函数: `__init__(self, palette_style: str, palatte_mode: str = 'random')`
  - 参数:
    - `palette_style` (`str`): 调色板风格名称。
    - `palatte_mode` (`str`): 颜色生成模式，默认 `'random'`。

---

### `PaletteWithRsCodec`

- 继承: `BaseCodec`
- 说明: 带 Reed-Solomon 纠错的调色板编解码器，可容忍一定比例的像素损坏。使用正方形图像，数据经 RS 编码后填充到正方形中。

- 构造函数: `__init__(self, palette_style: str, palatte_mode: str = 'random', threshold: float = 0.7)`
  - 参数:
    - `palette_style` (`str`): 调色板风格名称。
    - `palatte_mode` (`str`): 颜色生成模式，默认 `'random'`。
    - `threshold` (`float`): 最大数据填充率（0~1），默认 `0.7`。

---

### `RedundancyCodec`

- 继承: `BaseCodec`
- 说明: 冗余编解码器，通过在不同通道中以不同旋转方向（0/90/180/270度）存储相同数据实现容错。解码时使用多数投票合并各通道结果。

- 构造函数: `__init__(self, mode_name: str, channels: int)`
  - 参数:
    - `mode_name` (`str`): 图像模式名称，如 `'RGB'`、`'RGBA'`、`'L'`。注册名为 `mode_name.lower() + "_redundancy"`。
    - `channels` (`int`): 通道数。

- 方法:
  #### `_decode_one_channel(self, img, channel_index)`
  - 签名: `_decode_one_channel(self, img: Image.Image, channel_index: int) -> bytes`
  - 说明: 从图像中解码指定通道的数据。
  - 参数:
    - `img` (`Image.Image`): 要解码的图像对象。
    - `channel_index` (`int`): 通道索引（0=R, 1=G, 2=B, 3=A）。
  - 返回值: 该通道的字节数据。

## 顶层变量

### `CODEC_REGISTRY`

- 类型: `dict[str, BaseCodec]`
- 说明: 编解码器注册表，以 `mode_name` 为键存储所有可用编解码器实例。包含:
  - 手动注册: `GreyCodec` (`"grey_ori"`), `RGBCodec` (`"rgb_ori"`), `RGBACodec` (`"rgba_ori"`), `OneBitCodec` (`"1bit"`)
  - 从 `image_mode_params` 动态生成: `ChannelCodec` 和 `RedundancyCodec`
  - 从 `style_params` 动态生成: `PaletteCodec` 和 `PaletteWithRsCodec`

- 用法示例:

```python
from celestialvault.instances.inst_imgcodecs import CODEC_REGISTRY, RGBCodec, RefRGBALSBCodec
from PIL import Image

# 使用注册表获取编解码器
codec = CODEC_REGISTRY["rgb_ori"]

# 编码文本为图像
img = codec.encode_text("Hello, World!")
img.save("encoded.png")

# 从图像解码文本
img = Image.open("encoded.png")
text = codec.decode_text(img)
print(text)  # "Hello, World!"

# 编码二进制文件并保存图像
codec.encode_binary_file("data.bin", save_img=True)
# 输出: data(rgb_ori)(bin).png

# 从编码图像恢复二进制文件
codec.decode_binary_file("data(rgb_ori)(bin).png", save_file=True)

# LSB 隐写编码
lsb_codec = RefRGBALSBCodec("cover_image.png")
stego_img = lsb_codec.encode_text("隐藏的消息")
stego_img.save("stego.png")
decoded = lsb_codec.decode_text(Image.open("stego.png"))
```

- 关联: 所有编解码器继承自 `BaseCodec`。依赖 `celestialvault.tools.TextTools` 的 CRC、压缩、Base64、RS 编码函数和 `celestialvault.tools.ImageProcessing` 的调色板/容量工具。`celestialvault.tools.NumberUtils` 用于 RS 编解码的容器计算。
