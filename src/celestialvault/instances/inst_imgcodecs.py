import math
from itertools import product
from pathlib import Path
from PIL import Image
from tqdm import tqdm
from typing import Dict

from ..constants import image_mode_params, style_params
from ..tools.ImageProcessing import generate_palette
from ..tools.TextTools import (
    crc_encode,
    crc_decode,
    compress_text_to_bytes,
    decompress_text_from_bytes,
    rs_encode,
    rs_decode,
    pad_bytes,
    unpad_bytes,
    pad_to_align,
    safe_open_txt,
)
from ..tools.NumberUtils import choose_square_container, redundancy_from_container

# ========== 公共基类 ==========
class BaseCodec:
    """所有编码器的基类"""
    mode_name: str = ""
    show_progress: bool = True  # 默认开启进度条

    # --- 外部统一接口 ---
    def encode(self, text: str) -> Image.Image:
        """对文本加上 CRC 后再调用子类实现的像素编码"""
        crc_text = crc_encode(text)
        return self._encode_core(crc_text)

    def decode(self, img: Image.Image) -> str:
        """对像素数据解码后，再做 CRC 校验"""
        crc_text = self._decode_core(img)
        return crc_decode(crc_text)

    # --- 子类需要实现的接口 ---
    def _encode_core(self, text: str) -> Image.Image:
        raise NotImplementedError

    def _decode_core(self, img: Image.Image) -> str:
        raise NotImplementedError
    
    def encode_text_file(self, file_path: str) -> Image.Image:
        file_path = Path(file_path)

        target_text = safe_open_txt(file_path)
        img = self.encode(target_text)

        new_name = f"{file_path.stem}({self.mode_name}).png"
        output_path = file_path.with_name(new_name)

        img.save(output_path)

        return img
    
    def decode_image_file(self, img_path: str) -> str:
        img = Image.open(img_path)
        actual_text = self.decode(img)

        with open(img_path.replace(f".png", ".txt"), "w", encoding="utf-8") as f:
            f.write(actual_text)

        return actual_text

    @staticmethod
    def get_new_xy(old_x, old_y, width):
        if old_x == width - 1:
            return 0, old_y + 1
        else:
            return old_x + 1, old_y


# ========== grey_ori ==========
class GreyCodec(BaseCodec):
    mode_name = "grey_ori"

    def _encode_core(self, text: str) -> Image.Image:
        if not text:
            raise ValueError("Input text cannot be empty")

        str_len = len(text)
        total_pixels_needed = str_len * 2
        width = math.ceil(math.sqrt(total_pixels_needed))
        height = math.ceil(total_pixels_needed / width)

        img = Image.new("L", (width, height), 0)

        x, y = 0, 0
        for i in tqdm(text, desc="Encoding text(grey):", mininterval=0.5, disable=not self.show_progress):
            index = ord(i)
            high, low = divmod(index, 256)

            img.putpixel((x, y), high)
            x, y = self.get_new_xy(x, y, width)

            img.putpixel((x, y), low)
            x, y = self.get_new_xy(x, y, width)

        return img

    def _decode_core(self, img: Image.Image) -> str:
        width, height = img.size
        pixels = img.load()
        chars = []

        progress_len = (height * width) // 2
        progress_bar = tqdm(total=progress_len, desc="Decoding img(grey):", mininterval=0.5, disable=not self.show_progress)
        for i in range(0, progress_len * 2, 2):
            high = pixels[i % width, i // width]
            low = pixels[(i + 1) % width, (i + 1) // width]
            char = chr(high * 256 + low) if high * 256 + low != 0 else ""
            chars.append(char)
            progress_bar.update(1)

        progress_bar.close()
        return "".join(chars)


# ========== rgb_ori ==========
class RGBCodec(BaseCodec):
    mode_name = "rgb_ori"

    def _encode_core(self, text: str) -> Image.Image:
        if not text:
            raise ValueError("Input text cannot be empty")
        
        str_len = len(text)
        total_pixels_needed = math.ceil(str_len * 2 / 3)
        width = math.ceil(math.sqrt(total_pixels_needed))
        height = math.ceil(total_pixels_needed / width)

        img = Image.new("RGB", (width, height), (0, 0, 0))

        x, y = 0, 0
        for i in tqdm(range(0, str_len, 3), desc="Encoding text(rgb):", mininterval=0.5, disable=not self.show_progress):
            index1 = ord(text[i])
            index2 = ord(text[i + 1]) if i + 1 < str_len else 0
            index3 = ord(text[i + 2]) if i + 2 < str_len else 0

            rgb_0 = (index1 >> 8, index1 & 0xFF, index2 >> 8)
            img.putpixel((x, y), rgb_0)
            x, y = self.get_new_xy(x, y, width)

            rgb_1 = (index2 & 0xFF, index3 >> 8, index3 & 0xFF)
            img.putpixel((x, y), rgb_1)
            x, y = self.get_new_xy(x, y, width)

        return img

    def _decode_core(self, img: Image.Image) -> str:
        width, height = img.size
        pixels = img.load()
        chars = []

        progress_len = (height * width) // 2
        progress_bar = tqdm(total=progress_len, desc="Decoding img(rgb):", mininterval=0.5, disable=not self.show_progress)
        for i in range(0, progress_len * 2, 2):
            rgb_0 = pixels[i % width, i // width]
            rgb_1 = pixels[(i + 1) % width, (i + 1) // width]

            char1 = chr((rgb_0[0] << 8) + rgb_0[1]) if (rgb_0[0] << 8) + rgb_0[1] else ""
            char2 = chr((rgb_0[2] << 8) + rgb_1[0]) if (rgb_0[2] << 8) + rgb_1[0] else ""
            char3 = chr((rgb_1[1] << 8) + rgb_1[2]) if (rgb_1[1] << 8) + rgb_1[2] else ""
            chars.extend([char1, char2, char3])
            progress_bar.update(1)

        progress_bar.close()
        return "".join(chars)


# ========== rgba_ori ==========
class RGBACodec(BaseCodec):
    mode_name = "rgba_ori"

    def _encode_core(self, text: str) -> Image.Image:
        if not text:
            raise ValueError("Input text cannot be empty")
        
        str_len = len(text)
        total_pixels_needed = math.ceil(str_len / 2)
        width = math.ceil(math.sqrt(total_pixels_needed))
        height = math.ceil(total_pixels_needed / width)

        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        x, y = 0, 0
        for i in tqdm(range(0, str_len, 2), desc="Encoding text(rgba):", mininterval=0.5, disable=not self.show_progress):
            index1 = ord(text[i])
            index2 = ord(text[i + 1]) if i + 1 < str_len else 0
            rgba = (index1 >> 8, index1 & 0xFF, index2 >> 8, index2 & 0xFF)
            img.putpixel((x, y), rgba)
            x, y = self.get_new_xy(x, y, width)

        return img

    def _decode_core(self, img: Image.Image) -> str:
        width, height = img.size
        pixels = img.load()
        chars = []

        progress_bar = tqdm(total=height * width, desc="Decoding img(rgba):", mininterval=0.5, disable=not self.show_progress)
        for y, x in product(range(height), range(width)):
            rgba = pixels[x, y]
            char1 = chr((rgba[0] << 8) + rgba[1]) if (rgba[0] << 8) + rgba[1] else ""
            char2 = chr((rgba[2] << 8) + rgba[3]) if (rgba[2] << 8) + rgba[3] else ""
            chars.extend([char1, char2])
            progress_bar.update(1)

        progress_bar.close()
        return "".join(chars)


# ========== 1bit ==========
class OneBitCodec(BaseCodec):
    mode_name = "1bit"

    def _encode_core(self, text: str) -> Image.Image:
        """
        将带CRC的文本压缩为二进制串，并编码为1bit黑白图像
        """
        # 压缩为二进制（1通道）
        compressed_binary = compress_text_to_bytes(text)

        total_bits_needed = len(compressed_binary) * 8
        width = math.ceil(math.sqrt(total_bits_needed))
        height = math.ceil(total_bits_needed / width)

        img = Image.new("1", (width, height), 0)  # 黑白图像

        x, y = 0, 0
        for byte in tqdm(compressed_binary, desc="Encoding text(1bit-binary):", mininterval=0.5, disable=not self.show_progress):
            for bit in range(8):
                pixel_value = (byte >> (7 - bit)) & 1
                img.putpixel((x, y), pixel_value)
                x, y = self.get_new_xy(x, y, width)

        return img

    def _decode_core(self, img: Image.Image) -> str:
        """
        将1bit图像解码为带CRC的文本串（解压缩）
        """
        width, height = img.size
        pixels = img.load()

        bytes_list = []
        progress_len = (height * width) // 8
        progress_bar = tqdm(total=progress_len, desc="Decoding img(1bit-binary):", mininterval=0.5, disable=not self.show_progress)

        for i in range(0, progress_len * 8, 8):
            current_byte = 0
            for index in range(8):
                bit_value = pixels[(i + index) % width, (i + index) // width]

                # Pillow在"1"模式下返回的是 0 或 255，需要转成 0/1
                bit_value = 1 if bit_value == 255 else bit_value

                current_byte |= (bit_value << (7 - index))

            bytes_list.append(current_byte)
            progress_bar.update(1)

        progress_bar.close()

        # 解压缩
        crc_text = decompress_text_from_bytes(bytes(bytes_list))
        return crc_text


class ChannelCodec(BaseCodec):
    def __init__(self, mode_name: str, channels: int):
        self.mode_name = mode_name
        self.channels = channels

    def _encode_core(self, text: str) -> Image.Image:
        compressed_binary = compress_text_to_bytes(text)
        pad_binary = pad_to_align(compressed_binary, self.channels)

        str_len = len(pad_binary)
        total_pixels_needed = math.ceil(str_len / self.channels)
        width = math.ceil(math.sqrt(total_pixels_needed))
        height = math.ceil(total_pixels_needed / width)

        img = Image.new(self.mode_name, (width, height), (0,) * self.channels)

        x, y = 0, 0
        for i in tqdm(range(0, str_len, self.channels), desc=f"Encoding text({self.mode_name}-binary):", mininterval=0.5, disable=not self.show_progress):
            chars = pad_binary[i : i + self.channels]
            img.putpixel((x, y), tuple(chars))
            x, y = self.get_new_xy(x, y, width)

        return img

    def _decode_core(self, img: Image.Image) -> str:
        width, height = img.size
        pixels = img.load()
        channels = len(img.mode)

        bytes_list = []
        desc = f"Decoding img({channels}-channel-binary):"
        progress_bar = tqdm(total=height * width, desc=desc, mininterval=0.5, disable=not self.show_progress)

        for y in range(height):
            for x in range(width):
                pixel_data = pixels[x, y]
                if channels == 1:
                    bytes_list.append(pixel_data)
                else:
                    bytes_list.extend(pixel_data)
                progress_bar.update(1)

        progress_bar.close()
        crc_text = decompress_text_from_bytes(bytes(bytes_list))

        return crc_text
    

class PaletteCodec(BaseCodec):
    def __init__(self, palette_style: str, palatte_mode: str = "random"):
        self.mode_name = palette_style  # 用 palette_style 名称作为 mode
        self.palette = generate_palette(256, style=palette_style, mode=palatte_mode)

    def _encode_core(self, text: str) -> Image.Image:
        compressed_binary = compress_text_to_bytes(text)

        str_len = len(compressed_binary)
        width = math.ceil(math.sqrt(str_len))
        height = math.ceil(str_len / width)

        img = Image.new("P", (width, height))
        img.putpalette(self.palette)

        x, y = 0, 0
        for byte in tqdm(compressed_binary, desc=f"Encoding text(Palette-{self.mode_name})", disable=not self.show_progress):
            img.putpixel((x, y), byte)
            x, y = self.get_new_xy(x, y, width)

        return img

    def _decode_core(self, img: Image.Image) -> str:
        width, height = img.size
        pixels = img.load()

        bytes_list = []
        progress_bar = tqdm(total=height * width, desc=f"Decoding img(Palette-{self.mode_name})", disable=not self.show_progress)
        for y in range(height):
            for x in range(width):
                bytes_list.append(pixels[x, y])
                progress_bar.update(1)

        progress_bar.close()
        crc_text = decompress_text_from_bytes(bytes(bytes_list))
        return crc_text


class PaletteWithRsCodec(BaseCodec):
    def __init__(self, palette_style: str, palatte_mode: str = "random", threshold: float = 0.7):
        self.mode_name = palette_style + "_rs"  # 用 style 名称作为 mode
        self.palette = generate_palette(256, style=palette_style, mode=palatte_mode)
        self.threshold = threshold

    def _encode_core(self, text: str) -> Image.Image:
        compressed_binary = compress_text_to_bytes(text)
        side_len, max_payload, nsym = choose_square_container(len(compressed_binary), self.threshold)
        pad_binary = pad_bytes(compressed_binary, max_payload)
        rs_binary = rs_encode(pad_binary, nsym)

        img = Image.new("P", (side_len, side_len))
        img.putpalette(self.palette)

        x, y = 0, 0
        for byte in tqdm(rs_binary, desc=f"Encoding text(Palette-{self.mode_name})", disable=not self.show_progress):
            img.putpixel((x, y), byte)
            x, y = self.get_new_xy(x, y, side_len)

        return img

    def _decode_core(self, img: Image.Image) -> str:
        side_len, side_len = img.size
        pixels = img.load()

        bytes_list = []
        progress_bar = tqdm(total=side_len * side_len, desc=f"Decoding img(Palette-{self.mode_name})", disable=not self.show_progress)
        for y in range(side_len):
            for x in range(side_len):
                bytes_list.append(pixels[x, y])
                progress_bar.update(1)

        progress_bar.close()

        nsym = redundancy_from_container(side_len*side_len, self.threshold)
        ders_binary = rs_decode(bytes(bytes_list), nsym)
        unpad_binary = unpad_bytes(ders_binary)
        crc_text = decompress_text_from_bytes(unpad_binary)
        return crc_text


class RedundancyCodec(BaseCodec):
    def __init__(self, mode_name: str, channels: int):
        """
        mode_name: 图像模式名称，比如 'RGB', 'RGBA', 'L'
        channels: 通道数
        """
        self.mode_name = mode_name.lower() + "_redundancy"  # 注册名
        self.base_mode = mode_name.upper()                  # Pillow 图像模式
        self.channels = channels

    def _encode_core(self, text: str) -> Image.Image:
        compressed_binary = compress_text_to_bytes(text)

        str_len = len(compressed_binary)
        edge = math.ceil(math.sqrt(str_len))
        total_pixels = edge * edge

        # 填充到正方形
        binary_str = compressed_binary.ljust(total_pixels, b"\0")

        img = Image.new(self.base_mode, (edge, edge), (0,) * self.channels)

        # 索引表
        r_indices = [edge * y + x for y in range(edge) for x in range(edge)]
        g_indices = [edge * x + edge - 1 - y for y in range(edge) for x in range(edge)]
        b_indices = [edge * (edge - 1 - y) + edge - 1 - x for y in range(edge) for x in range(edge)]
        a_indices = [edge * (edge - 1 - x) + y for y in range(edge) for x in range(edge)]

        for idx in tqdm(range(total_pixels), desc=f"Encoding text({self.mode_name})", mininterval=0.5, disable=not self.show_progress):
            r = binary_str[r_indices[idx]] if self.channels > 0 else 0
            g = binary_str[g_indices[idx]] if self.channels > 1 else 0
            b = binary_str[b_indices[idx]] if self.channels > 2 else 0
            a = binary_str[a_indices[idx]] if self.channels > 3 else 0
            pixel_value = (r, g, b, a)[:self.channels]
            img.putpixel((idx % edge, idx // edge), pixel_value)

        return img

    def _decode_core(self, img: Image.Image) -> str:
        channels = len(img.mode)
        decoded_data = []

        for channel_index in range(channels):
            if channel_index == 0:
                data = self._decode_one_channel(img, 0)
            elif channel_index == 1:
                data = self._decode_one_channel(img.rotate(270, expand=True), 1)
            elif channel_index == 2:
                data = self._decode_one_channel(img.rotate(180, expand=True), 2)
            elif channel_index == 3:
                data = self._decode_one_channel(img.rotate(90, expand=True), 3)
            decoded_data.append(data)

        # 如果完全一致
        if all(decoded_data[0] == d for d in decoded_data):
            merged_bytes = decoded_data[0]
        else:
            # 多数投票
            combined_data = bytearray(len(decoded_data[0]))
            for i in range(len(combined_data)):
                candidates = [decoded_data[ch][i] for ch in range(channels)]
                combined_data[i] = max(set(candidates), key=candidates.count)
            merged_bytes = bytes(combined_data)

        return decompress_text_from_bytes(merged_bytes)

    def _decode_one_channel(self, img: Image.Image, channel_index: int) -> bytes:
        width, height = img.size
        pixels = img.load()
        bytes_list = []

        desc = f"Decoding img(channel {channel_index}-redundancy):"
        progress_bar = tqdm(total=height * width, desc=desc, mininterval=0.5, disable=not self.show_progress)

        for y in range(height):
            for x in range(width):
                pixel_data = pixels[x, y]
                if isinstance(pixel_data, int):
                    # L 模式
                    bytes_list.append(pixel_data)
                else:
                    # RGB/RGBA 模式
                    bytes_list.append(pixel_data[channel_index])
                progress_bar.update(1)

        progress_bar.close()
        return bytes(bytes_list)


CODEC_REGISTRY: Dict[str, BaseCodec] = {}

CODEC_REGISTRY.update({
    GreyCodec.mode_name: GreyCodec(),
    RGBCodec.mode_name: RGBCodec(),
    RGBACodec.mode_name: RGBACodec(),
    OneBitCodec.mode_name: OneBitCodec(),
})

# 从 image_mode_params 动态生成
for mode, params in image_mode_params.items():
    # 普通模式
    CODEC_REGISTRY[mode] = ChannelCodec(
        mode_name=params["mode_name"],
        channels=params["channels"]
    )

    # 冗余模式
    redundancy_mode = mode + "_redundancy"
    CODEC_REGISTRY[redundancy_mode] = RedundancyCodec(
        mode_name=params["mode_name"],
        channels=params["channels"]
    )

# 从 style_params 动态生成
for style in style_params:
    CODEC_REGISTRY[style] = PaletteCodec(palette_style=style)
    CODEC_REGISTRY[style + "_rs"] = PaletteWithRsCodec(palette_style=style)
