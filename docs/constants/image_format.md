# `celestialvault.constants.image_format`

## 源文件
- `src/celestialvault/constants/image_format.py`

## 模块说明
定义图片文件后缀名到 Pillow 图片格式名称的映射字典，用于根据文件扩展名确定对应的图像格式。

## 导入依赖
- 无

## 模块常量

### `IMAGE_SUFFIX_TO_FORMAT`
- **类型**: `dict[str, str]`
- **值**: 文件后缀名（含点号）到 Pillow 图片格式名称的映射，共 42 个条目
- **说明**: 支持以下格式：

| 后缀 | 格式 | 后缀 | 格式 |
|------|------|------|------|
| `.apng` | `"PNG"` | `.msp` | `"MSP"` |
| `.avif` | `"AVIF"` | `.pbm` | `"PPM"` |
| `.avifs` | `"AVIF"` | `.pcx` | `"PCX"` |
| `.bmp` | `"BMP"` | `.pgm` | `"PPM"` |
| `.dib` | `"BMP"` | `.png` | `"PNG"` |
| `.dds` | `"DDS"` | `.pnm` | `"PPM"` |
| `.gif` | `"GIF"` | `.ppm` | `"PPM"` |
| `.heic` | `"HEIF"` | `.sgi` | `"SGI"` |
| `.heif` | `"HEIF"` | `.rgb` | `"SGI"` |
| `.icb` | `"TGA"` | `.rgba` | `"SGI"` |
| `.icns` | `"ICNS"` | `.bw` | `"SGI"` |
| `.ico` | `"ICO"` | `.tga` | `"TGA"` |
| `.im` | `"IM"` | `.tif` | `"TIFF"` |
| `.jfif` | `"JPEG"` | `.tiff` | `"TIFF"` |
| `.jpe` | `"JPEG"` | `.vda` | `"TGA"` |
| `.jpeg` | `"JPEG"` | `.vst` | `"TGA"` |
| `.jpg` | `"JPEG"` | `.webp` | `"WEBP"` |
| `.j2c` | `"JPEG2000"` | `.j2k` | `"JPEG2000"` |
| `.jp2` | `"JPEG2000"` | `.jpc` | `"JPEG2000"` |
| `.jpf` | `"JPEG2000"` | `.jpx` | `"JPEG2000"` |

## 用法示例

```python
from celestialvault.constants.image_format import IMAGE_SUFFIX_TO_FORMAT

# 根据文件后缀获取图片格式
suffix = ".jpg"
fmt = IMAGE_SUFFIX_TO_FORMAT.get(suffix)
print(fmt)  # "JPEG"

# 检查后缀是否为已知图片格式
if ".webp" in IMAGE_SUFFIX_TO_FORMAT:
    print("WebP is supported")
```

## 关联
- 可用于图像处理模块中根据文件扩展名自动识别 Pillow 保存格式
- 与 `celestialvault.constants.suffix` 中的 `IMG_SUFFIXES` 配合使用

## 顶层函数
- 无

## 类
- 无
