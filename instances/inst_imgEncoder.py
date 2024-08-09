import math
from PIL import Image, PngImagePlugin
from tqdm import tqdm
from itertools import product

class ImgEncoder:
    def __init__(self, text_encoder=None) -> None:
        self.text_encoder = text_encoder
        
    def encode_text(self, text_path: str, mode: str='grey') -> None:
        from tools.TextTools import encode_crc, safe_open_txt

        text = safe_open_txt(text_path)
        crc_text = encode_crc(text)

        if mode == 'grey':
            img = self.encode_gray(crc_text)
        elif mode == 'rgba':
            img = self.encode_rgba(crc_text)
        elif mode == 'rgba_full':
            img = self.encode_rgba_full(crc_text)
        elif mode == 'rgb':
            img = self.encode_rgb(crc_text)
        else:
            raise ValueError(f'Unsupported mode: {mode}')
        
        img.save(text_path.replace('.txt', f'({mode}).png'))

        return img

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
        for i in tqdm(text, desc='Encoding text(grey):'):
            index = ord(i)
            high, low = divmod(index, 256)  # 将index分成两个8位的数

            img.putpixel((x, y), high)  # 将high存入像素
            if x == width - 1:  # 如果x达到宽度，则转到下一行
                x = 0
                y += 1
            else:
                x += 1

            img.putpixel((x, y), low)  # 将low存入像素
            if x == width - 1:
                x = 0
                y += 1
            else:
                x += 1
        return img

    def encode_rgba(self, text: str) -> Image.Image:
        """
        将文本编码为RGBA图像(unsafe)
        :param text: 要编码的文本
        :return: 编码后的RGBA图像
        """
        str_len = len(text)
        total_pixels_needed = str_len // 2 + str_len % 2
        width = math.ceil(math.sqrt(total_pixels_needed))
        height = math.ceil(total_pixels_needed / width)
        
        img = Image.new("RGBA", (width, height), (0,0,0,0))

        x,y = 0,0
        for i in tqdm(range(0, str_len, 2), desc='Encoding text(rgba):'):
            index1 = ord(text[i])
            index2 = ord(text[i+1]) if i+1 < str_len else 0
            rgba = (index1 >> 8, index1 & 0xFF, index2 >> 8, index2 & 0xFF)
            img.putpixel((x, y), rgba)
            if x == width - 1:
                x = 0
                y += 1
            else:
                x += 1
        return img

    def encode_rgba_full(self, text: str) -> Image.Image:
        """
        将文本编码为RGBA图像，每个字符占用一个像素(safe)
        :param text: 要编码的文本
        :return: 编码后的RGBA图像
        """
        str_len = len(text)
        width = math.ceil(math.sqrt(str_len))
        img = Image.new("RGBA", (width, width), (0,0,0,0))

        x, y = 0, 0
        for i in tqdm(text, desc='Encoding text(rgba_full):'):
            index = ord(i)
            rgba = ((index >> 24) & 0xFF, (index >> 16) & 0xFF, (index >> 8) & 0xFF, index & 0xFF)
            img.putpixel((x, y), rgba)
            if x == width - 1:
                x = 0
                y += 1
            else:
                x += 1
        return img
    
    def encode_rgb(self, text: str) -> Image.Image:
        """
        将文本编码为RGB图像(safe)
        :param text: 要编码的文本
        :return: 编码后的RGB图像
        """
        from tools.TextTools import compress_to_base64

        base64_text = compress_to_base64(text)
        str_len = len(base64_text)
        
        total_pixels_needed = math.ceil(str_len / 4)
        width = math.ceil(math.sqrt(total_pixels_needed))
        height = math.ceil(total_pixels_needed / width)
        
        img = Image.new("RGB", (width, height), (0, 0, 0))
        
        base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
        char_to_value = {char: index for index, char in enumerate(base64_chars)}
        
        x, y = 0, 0
        for i in tqdm(range(0, str_len, 4), desc='Encoding text(rgb):'):
            chars = base64_text[i:i+4]
        
            val1 = char_to_value[chars[0]]
            val2 = char_to_value[chars[1]]
            val3 = char_to_value[chars[2]]
            val4 = char_to_value[chars[3]]

            r = (val1 << 2) | (val2 >> 4)
            g = ((val2 & 0xF) << 4) | (val3 >> 2)
            b = ((val3 & 0x3) << 6) | val4
            
            img.putpixel((x, y), (r, g, b))
            if x == width - 1:
                x = 0
                y += 1
            else:
                x += 1
        
        return img
    
    def add_message_after_binary(self, binary_img: bytes, message: str) -> bytes:
        # 将消息以二进制形式附加到PNG图像文件的末尾
        binary_message = message.encode('utf-8')
        binary_data = binary_img + binary_message

        return binary_data
    
    def add_message_in_img(self, img: Image.Image, message_dict: dict[str: str]) -> Image.Image:
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
    def decode_image(self, img_path: str, mode: str='grey') -> None:
        from tools.TextTools import decode_crc

        img = Image.open(img_path)

        if mode == 'grey':
            crc_text = self.decode_gray(img)
        elif mode == 'rgba':
            crc_text = self.decode_rgba(img)
        elif mode == 'rgba_full':
            crc_text = self.decode_rgba_full(img)
        elif mode == 'rgb':
            crc_text = self.decode_rgb(img)
        else:
            raise ValueError(f'Unsupported mode: {mode}')
        
        if not decode_crc(crc_text):
            print('CRC校验失败')

        actual_text = crc_text[4:]
        with open(img_path.replace(f'.png', '.txt'), 'w', encoding='utf-8') as f:
            f.write(actual_text)

        return actual_text

    def decode_gray(self, img: Image.Image) -> str:
        '''
        将gray图像解码为字符串
        :param im: 图像对象
        :return: 解码后的字符串
        '''
        width, height = img.size
        text = ""

        progress_len = (height * width) // 2
        progress_bar = tqdm(total=progress_len, desc='Decoding img(grey):')
        for i in range(0, progress_len*2, 2):  # 两个像素表示一个字符
            high = img.getpixel((i%width, i//width))
            low = img.getpixel(((i+1)%width, (i+1)//width))
            
            index = high * 256 + low  # 还原index
            text += chr(index)  if index != 0 else '' # 转化为字符
            progress_bar.update(1)
            
        progress_bar.close()
        return text

    def decode_rgba(self, img: Image.Image) -> str:
        '''
        将rgba图像解码为字符串
        :param img: 图像对象
        :return: 解码后的字符串
        '''
        width, height = img.size
        pixels = img.load()

        chars = []
        progress_bar = tqdm(total=height * width, desc='Decoding img(rgba):')
        for y, x in product(range(height), range(width)):
            rgba = pixels[x, y]
            char1 = chr((rgba[0] << 8) + rgba[1]) if (rgba[0] << 8) + rgba[1] != 0 else ''
            char2 = chr((rgba[2] << 8) + rgba[3]) if (rgba[2] << 8) + rgba[3] != 0 else ''
            chars.extend([char1, char2])
            progress_bar.update(1)
            
        progress_bar.close()
        return ''.join(chars)
    
    def decode_rgba_full(self, img: Image.Image) -> str:
        '''
        将rgba图像解码为字符串
        :param img: 图像对象
        :return: 解码后的字符串
        '''
        width, height = img.size
        pixels = img.load()

        chars = []
        progress_bar = tqdm(total=height * width, desc='Decoding img(rgba_full):')
        for y, x in product(range(height), range(width)):
            rgba = pixels[x, y]
            unicode_value = (rgba[0] << 24) + (rgba[1] << 16) + (rgba[2] << 8) + rgba[3]
            char = chr(unicode_value) if unicode_value != 0 else ''
            chars.append(char)
            progress_bar.update(1)

        progress_bar.close()
        return ''.join(chars)
    
    def decode_rgb(self, img: Image.Image) -> str:
        '''
        将rgb图像解码为字符串
        :param img: 图像对象
        :return: 解码后的字符串
        '''
        from tools.TextTools import decode_from_base64
        width, height = img.size
        base64_text = []
        
        base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
        value_to_char = {index: char for index, char in enumerate(base64_chars)}
        
        progress_bar = tqdm(total=height * width, desc='Decoding img(rgb):')
        for y, x in product(range(height), range(width)):
            r, g, b = img.getpixel((x, y))
            
            char1 = value_to_char[r >> 2]
            char2 = value_to_char[((r & 0x3) << 4) | (g >> 4)]
            char3 = value_to_char[((g & 0xF) << 2) | (b >> 6)]
            char4 = value_to_char[b & 0x3F]
            
            base64_text.extend([char1, char2, char3, char4])
            progress_bar.update(1)
        
        base64_text = ''.join(base64_text)
        
        return decode_from_base64(base64_text)
    
    def read_message_from_binary(self, binary_data: bytes) -> str:
        from tools.ImageProcessing import binary_to_img, img_to_binary

        img_len = len(img_to_binary(binary_to_img(binary_data)))
        return binary_data[img_len:]