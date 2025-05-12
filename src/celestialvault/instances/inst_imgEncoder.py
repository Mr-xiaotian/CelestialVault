import math
from itertools import product

from PIL import Image, PngImagePlugin
from tqdm import tqdm

from ..constants import image_mode_params, style_params
from ..tools.ImageProcessing import generate_palette
from ..tools.TextTools import (
    compress_text_to_bytes,
    decode_crc,
    decompress_text_from_bytes,
    encode_crc,
    safe_open_txt,
)


class ImgEncoder:
    def encode_text_file(self, file_path: str, mode: str = "morandi") -> Image.Image:
        target_text = safe_open_txt(file_path)
        img = self.encode_text(target_text, mode)
        img.save(file_path.replace(".txt", f"({mode}).png"))

        return img

    def encode_text(self, target_text, mode: str = "morandi") -> Image.Image:
        crc_text = encode_crc(target_text)

        if mode == "grey_ori":
            img = self.encode_gray(crc_text)
        elif mode == "rgb_ori":
            img = self.encode_rgb(crc_text)
        elif mode == "rgba_ori":
            img = self.encode_rgba(crc_text)
        elif mode == "1bit":
            compressed_binary = compress_text_to_bytes(crc_text, 1)
            img = self.encode_1bit(compressed_binary)
        elif mode in style_params:
            palette = generate_palette(256, style=mode)
            compressed_binary = compress_text_to_bytes(crc_text, 1)
            img = self.encode_channels(compressed_binary, "P", palette)
        elif mode in image_mode_params:
            compressed_binary = compress_text_to_bytes(
                crc_text, image_mode_params[mode]["channels"]
            )
            img = self.encode_channels(
                compressed_binary, image_mode_params[mode]["mode_name"]
            )
        elif "redundancy" in mode and mode[:-11] in image_mode_params:
            compressed_binary = compress_text_to_bytes(crc_text, 1)
            img = self.encode_channels_with_redundancy(
                compressed_binary, image_mode_params[mode[:-11]]["mode_name"]
            )
        else:
            raise ValueError(f"Unsupported mode: {mode}")

        return img

    def get_new_xy(self, old_x, old_y, width):
        if old_x == width - 1:
            return 0, old_y + 1
        else:
            return old_x + 1, old_y

    def encode_gray(self, text: str) -> Image.Image:
        """
        将文本编码为灰度图像(unsafe)
        :param text: 要编码的文本
        :return: 编码后的灰度图像
        """
        str_len = len(text)
        total_pixels_needed = str_len * 2  # 每个字符需要两个像素表示
        width = math.ceil(math.sqrt(total_pixels_needed))
        height = math.ceil(total_pixels_needed / width)

        img = Image.new("L", (width, height), 0)  # 创建一个灰度图像

        x, y = 0, 0
        for i in tqdm(text, desc="Encoding text(grey):"):
            index = ord(i)
            high, low = divmod(index, 256)  # 将index分成两个8位的数

            img.putpixel((x, y), high)  # 将high存入像素
            x, y = self.get_new_xy(x, y, width)

            img.putpixel((x, y), low)  # 将low存入像素
            x, y = self.get_new_xy(x, y, width)
        return img

    def encode_rgb(self, text: str) -> Image.Image:
        """
        将文本编码为RGB图像(unsafe)
        :param text: 要编码的文本
        :return: 编码后的RGB图像
        """
        str_len = len(text)
        total_pixels_needed = math.ceil(str_len * 2 / 3)
        width = math.ceil(math.sqrt(total_pixels_needed))
        height = math.ceil(total_pixels_needed / width)

        img = Image.new("RGB", (width, height), (0, 0, 0))

        x, y = 0, 0
        for i in tqdm(range(0, str_len, 3), desc="Encoding text(rgb):"):
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

    def encode_rgba(self, text: str) -> Image.Image:
        """
        将文本编码为RGBA图像(unsafe)
        :param text: 要编码的文本
        :return: 编码后的RGBA图像
        """
        str_len = len(text)
        total_pixels_needed = math.ceil(str_len / 2)
        width = math.ceil(math.sqrt(total_pixels_needed))
        height = math.ceil(total_pixels_needed / width)

        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        x, y = 0, 0
        for i in tqdm(range(0, str_len, 2), desc="Encoding text(rgba):"):
            index1 = ord(text[i])
            index2 = ord(text[i + 1]) if i + 1 < str_len else 0
            rgba = (index1 >> 8, index1 & 0xFF, index2 >> 8, index2 & 0xFF)
            img.putpixel((x, y), rgba)
            x, y = self.get_new_xy(x, y, width)
        return img

    def encode_1bit(self, binary_str: bytes) -> Image.Image:
        total_bits_needed = len(binary_str) * 8  # 每个字节有8位
        width = math.ceil(math.sqrt(total_bits_needed))  # 计算图像的宽度
        height = math.ceil(total_bits_needed / width)  # 计算图像的高度

        img = Image.new("1", (width, height), 0)  # 创建1位模式的图像，默认黑色

        x, y = 0, 0
        for byte in tqdm(binary_str, desc="Encoding text(1-bit-binary):"):
            for bit in range(8):  # 每个字节的8位逐一处理
                pixel_value = (byte >> (7 - bit)) & 1  # 提取对应位的值
                img.putpixel((x, y), pixel_value)

                x, y = self.get_new_xy(x, y, width)

        return img

    def encode_channels(
        self, binary_str: bytes, mode: str, palette: list = None
    ) -> Image.Image:
        channels = len(mode)
        str_len = len(binary_str)
        total_pixels_needed = math.ceil(str_len / channels)

        width = math.ceil(math.sqrt(total_pixels_needed))
        height = math.ceil(total_pixels_needed / width)

        img = Image.new(mode, (width, height), (0,) * channels)

        # 将调色板应用到图像上
        img.putpalette(palette) if mode == "P" and palette else None

        x, y = 0, 0
        for i in tqdm(
            range(0, str_len, channels), desc=f"Encoding text({mode}-binary):"
        ):
            chars = binary_str[i : i + channels]

            img.putpixel((x, y), tuple(chars))
            x, y = self.get_new_xy(x, y, width)

        return img

    def encode_channels_with_redundancy(
        self, binary_str: bytes, mode: str
    ) -> Image.Image:
        str_len = len(binary_str)

        channels = len(mode)  # 获取图像模式的通道数量
        edge = math.ceil(math.sqrt(str_len))
        total_pixels = edge * edge

        # 为不满的部分填充 0
        binary_str = binary_str.ljust(total_pixels, b"\0")

        img = Image.new(mode, (edge, edge), (0,) * channels)

        # 提前计算索引，减少循环内的计算量
        r_indices = [edge * y + x for y in range(edge) for x in range(edge)]
        g_indices = [edge * x + edge - 1 - y for y in range(edge) for x in range(edge)]
        b_indices = [
            edge * (edge - 1 - y) + edge - 1 - x
            for y in range(edge)
            for x in range(edge)
        ]
        a_indices = [
            edge * (edge - 1 - x) + y for y in range(edge) for x in range(edge)
        ]

        # 编码数据到图像
        for idx in tqdm(range(total_pixels), desc=f"Encoding text({mode}-redundancy)"):
            r = binary_str[r_indices[idx]] if channels > 0 else 0
            g = binary_str[g_indices[idx]] if channels > 1 else 0
            b = binary_str[b_indices[idx]] if channels > 2 else 0
            a = binary_str[a_indices[idx]] if channels > 3 else 0

            pixel_value = (r, g, b, a)[:channels]  # 根据通道数量选择数据

            img.putpixel((idx % edge, idx // edge), pixel_value)

        return img

    def add_message_after_binary(self, binary_img: bytes, message: str) -> bytes:
        # 将消息以二进制形式附加到PNG图像文件的末尾
        binary_message = message.encode("utf-8")
        binary_data = binary_img + binary_message

        return binary_data

    def add_message_in_img(
        self, img: Image.Image, message_dict: dict[str:str]
    ) -> Image.Image:
        # 将文本字典添加到图像
        for key in message_dict:
            img.info[key] = message_dict[key]

        return img

    def create_image_with_text_chunk(message: str, img: Image.Image, output_path: str):
        # 打开图像文件并添加文本块
        meta = PngImagePlugin.PngInfo()
        meta.add_text("Message", message)

        # 保存带有文本块的图像
        img.save(output_path, "PNG", pnginfo=meta)


class ImgDecoder:
    def decode_image_file(self, img_path: str, mode: str = "morandi") -> str:
        img = Image.open(img_path)
        actual_text = self.decode_image(img, mode)

        with open(img_path.replace(f".png", ".txt"), "w", encoding="utf-8") as f:
            f.write(actual_text)

    def decode_image(self, img: Image.Image, mode: str = "morandi") -> None:
        if mode == "grey_ori":
            crc_text = self.decode_gray(img)
        elif mode == "rgb_ori":
            crc_text = self.decode_rgb(img)
        elif mode == "rgba_ori":
            crc_text = self.decode_rgba(img)
        elif mode == "1bit":
            crc_binary = self.decode_1bit(img)
            crc_text = decompress_text_from_bytes(crc_binary)
        elif mode in style_params or mode in image_mode_params:
            crc_binary = self.decode_channels(img)
            crc_text = decompress_text_from_bytes(crc_binary)
        elif "redundancy" in mode and mode[:-11] in image_mode_params:
            crc_binary = self.decode_channels_with_redundancy(img)
            crc_text = decompress_text_from_bytes(crc_binary)
        else:
            raise ValueError(f"Unsupported mode: {mode}")

        actual_text = decode_crc(crc_text)

        return actual_text

    def decode_gray(self, img: Image.Image) -> str:
        """
        将gray图像解码为字符串
        :param img: 图像对象
        :return: 解码后的字符串
        """
        width, height = img.size
        pixels = img.load()
        chars = []

        progress_len = (height * width) // 2
        progress_bar = tqdm(total=progress_len, desc="Decoding img(grey):")
        for i in range(0, progress_len * 2, 2):  # 两个像素表示一个字符
            high = pixels[i % width, i // width]
            low = pixels[(i + 1) % width, (i + 1) // width]

            char = chr(high * 256 + low) if high * 256 + low != 0 else ""
            chars.append(char)
            progress_bar.update(1)

        progress_bar.close()
        return "".join(chars)

    def decode_rgb(self, img: Image.Image) -> str:
        """
        将rgb图像解码为字符串
        :param img: 图像对象
        :return: 解码后的字符串
        """
        width, height = img.size
        pixels = img.load()
        chars = []

        progress_len = (height * width) // 2
        progress_bar = tqdm(total=progress_len, desc="Decoding img(rgb):")
        for i in range(0, progress_len * 2, 2):  # 两个像素表示一个字符
            rgb_0 = pixels[i % width, i // width]
            rgb_1 = pixels[(i + 1) % width, (i + 1) // width]

            char1 = (
                chr((rgb_0[0] << 8) + rgb_0[1])
                if (rgb_0[0] << 8) + rgb_0[1] != 0
                else ""
            )
            char2 = (
                chr((rgb_0[2] << 8) + rgb_1[0])
                if (rgb_0[2] << 8) + rgb_1[0] != 0
                else ""
            )
            char3 = (
                chr((rgb_1[1] << 8) + rgb_1[2])
                if (rgb_1[1] << 8) + rgb_1[2] != 0
                else ""
            )
            chars.extend([char1, char2, char3])
            progress_bar.update(1)

        progress_bar.close()
        return "".join(chars)

    def decode_rgba(self, img: Image.Image) -> str:
        """
        将rgba图像解码为字符串
        :param img: 图像对象
        :return: 解码后的字符串
        """
        width, height = img.size
        pixels = img.load()
        chars = []

        progress_bar = tqdm(total=height * width, desc="Decoding img(rgba):")
        for y, x in product(range(height), range(width)):
            rgba = pixels[x, y]
            char1 = (
                chr((rgba[0] << 8) + rgba[1]) if (rgba[0] << 8) + rgba[1] != 0 else ""
            )
            char2 = (
                chr((rgba[2] << 8) + rgba[3]) if (rgba[2] << 8) + rgba[3] != 0 else ""
            )
            chars.extend([char1, char2])
            progress_bar.update(1)

        progress_bar.close()
        return "".join(chars)

    def decode_1bit(self, img: Image.Image) -> bytes:
        """
        将1bit图像解码为binary串
        :param img: 图像对象
        :return: 解码后的binary串
        """
        width, height = img.size
        pixels = img.load()

        bytes_list = []
        progress_len = (height * width) // 8
        progress_bar = tqdm(total=progress_len, desc="Decoding img(1bit-binary):")
        for i in range(0, progress_len * 8, 8):  # 8个像素表示一个binary
            current_byte = 0
            for index in range(8):
                bit_value = pixels[(i + index) % width, (i + index) // width]

                # 将255转换为1，表示白色
                bit_value = 1 if bit_value == 255 else bit_value

                current_byte += bit_value * (2 ** (7 - index))

            bytes_list.append(current_byte)
            progress_bar.update(1)

        progress_bar.close()
        return bytes(bytes_list)

    def decode_channels(self, img: Image.Image) -> bytes:
        width, height = img.size
        pixels = img.load()

        bytes_list = []
        mode = img.mode  # 获取图像的模式
        channels = len(mode)  # 根据模式确定通道数
        desc = f"Decoding img({channels}-channel-binary):"
        progress_bar = tqdm(total=height * width, desc=desc)

        for y, x in product(range(height), range(width)):
            pixel_data = pixels[x, y]
            if channels == 1:
                bytes_list.append(pixel_data)
            else:
                bytes_list.extend(pixel_data)
            progress_bar.update(1)

        progress_bar.close()
        return bytes(bytes_list)

    def decode_one_channel(self, img: Image.Image, channel_index: int) -> bytes:
        """
        解码给定通道的数据，并从图像中恢复原始字节数据。

        :param img: 输入的图像 (RGBA 模式)
        :param channel_index: 要解码的通道索引（0 = R, 1 = G, 2 = B, 3 = A）
        :return: 解码后的字节数据
        """
        width, height = img.size
        pixels = img.load()

        bytes_list = []
        desc = f"Decoding img(channel {channel_index}-redundancy):"
        progress_bar = tqdm(total=height * width, desc=desc)

        for y, x in product(range(height), range(width)):
            pixel_data = pixels[x, y]
            bytes_list.append(pixel_data[channel_index])  # 读取指定的通道
            progress_bar.update(1)

        progress_bar.close()
        return bytes(bytes_list)

    def decode_channels_with_redundancy(self, img: Image.Image) -> bytes:
        """
        解码所有方向的信息，将结果合并成完整的字节数据。

        :param img: 输入的图像 (RGBA, RGB, L 模式)
        :return: 完整的解码后的字节数据
        """
        mode = img.mode
        channels = len(mode)

        if channels == 1:
            return self.decode_channels(img)

        # 解码通道数据
        decoded_data = []
        for channel_index in range(channels):
            if channel_index == 0:
                data = self.decode_one_channel(img, 0)
            elif channel_index == 1:
                img_rotated = img.rotate(270, expand=True)
                data = self.decode_one_channel(img_rotated, 1)
            elif channel_index == 2:
                img_rotated = img.rotate(180, expand=True)
                data = self.decode_one_channel(img_rotated, 2)
            elif channel_index == 3:
                img_rotated = img.rotate(90, expand=True)
                data = self.decode_one_channel(img_rotated, 3)
            decoded_data.append(data)

        # 如果所有解码数据相同，则直接返回其中一个
        if all(decoded_data[0] == d for d in decoded_data):
            return decoded_data[0]

        # 合并通道数据，处理冗余
        combined_data = bytearray(len(decoded_data[0]))
        for i in range(len(combined_data)):
            candidates = [decoded_data[ch][i] for ch in range(channels)]
            combined_data[i] = max(
                set(candidates), key=candidates.count
            )  # 选取出现最多的值

        return bytes(combined_data)

    def read_message_from_binary(self, binary_data: bytes) -> str:
        from ..tools.ImageProcessing import binary_to_img, img_to_binary

        img_len = len(img_to_binary(binary_to_img(binary_data)))
        return binary_data[img_len:]
