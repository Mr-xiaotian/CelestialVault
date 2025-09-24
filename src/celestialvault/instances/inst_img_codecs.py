import math
from itertools import product
from PIL import Image
from tqdm import tqdm
from typing import Dict

from ..constants import image_mode_params, style_params
from ..tools.ImageProcessing import generate_palette
from ..tools.TextTools import (
    compress_text_to_bytes,
    decompress_text_from_bytes,
    encode_crc,
    decode_crc,
    safe_open_txt,
)

# ========== 公共基类 ==========
class BaseCodec:
    """所有编码器的基类"""
    mode_name: str = ""

    # --- 外部统一接口 ---
    def encode(self, text: str) -> Image.Image:
        """对文本加上 CRC 后再调用子类实现的像素编码"""
        crc_text = encode_crc(text)
        return self._encode_core(crc_text)

    def decode(self, img: Image.Image) -> str:
        """对像素数据解码后，再做 CRC 校验"""
        crc_text = self._decode_core(img)
        return decode_crc(crc_text)

    # --- 子类需要实现的接口 ---
    def _encode_core(self, text: str) -> Image.Image:
        raise NotImplementedError

    def _decode_core(self, img: Image.Image) -> str:
        raise NotImplementedError
    
    def encode_text_file(self, file_path: str) -> Image.Image:
        target_text = safe_open_txt(file_path)
        img = self.encode(target_text)
        img.save(file_path.replace(".txt", f"({self.mode_name}).png"))

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
        for i in tqdm(text, desc="Encoding text(grey):", mininterval=0.5):
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
        progress_bar = tqdm(total=progress_len, desc="Decoding img(grey):", mininterval=0.5)
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
        for i in tqdm(range(0, str_len, 3), desc="Encoding text(rgb):", mininterval=0.5):
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
        progress_bar = tqdm(total=progress_len, desc="Decoding img(rgb):", mininterval=0.5)
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
        for i in tqdm(range(0, str_len, 2), desc="Encoding text(rgba):", mininterval=0.5):
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

        progress_bar = tqdm(total=height * width, desc="Decoding img(rgba):", mininterval=0.5)
        for y, x in product(range(height), range(width)):
            rgba = pixels[x, y]
            char1 = chr((rgba[0] << 8) + rgba[1]) if (rgba[0] << 8) + rgba[1] else ""
            char2 = chr((rgba[2] << 8) + rgba[3]) if (rgba[2] << 8) + rgba[3] else ""
            chars.extend([char1, char2])
            progress_bar.update(1)

        progress_bar.close()
        return "".join(chars)


CODEC_REGISTRY: Dict[str, BaseCodec] = {
    GreyCodec.mode_name: GreyCodec(),
    RGBCodec.mode_name: RGBCodec(),
    RGBACodec.mode_name: RGBACodec(),
}

def get_codec(mode: str) -> BaseCodec:
    if mode not in CODEC_REGISTRY:
        raise ValueError(f"Unsupported mode: {mode}")
    return CODEC_REGISTRY[mode]
