import base64
import math
from PIL import Image, PngImagePlugin
from tqdm import tqdm
from itertools import product

class ImgEncoder:
    def __init__(self, text_encoder=None) -> None:
        self.text_encoder = text_encoder
        
        
    def encode_text(self, text_path: str, mode: str='grey') -> None:
        with open(text_path, 'r', encoding = "utf-8") as f:
            text = f.read()

        if mode == 'grey':
            img = self.encodes_gray(text)
        elif mode == 'rgba':
            img = self.encodes_rgba(text)
        elif mode == 'rgba_full':
            img = self.encodes_rgba_full(text)
        else:
            raise ValueError(f'Unsupported mode: {mode}')
        
        img.save(text_path.replace('.txt', f'({mode}).png'))

    def encodes_gray(self, text: str) -> Image.Image:
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

    def encodes_rgba(self, text: str) -> Image.Image:
        str_len = len(text)
        total_pixels_needed = str_len // 2 + str_len % 2
        width = math.ceil(math.sqrt(total_pixels_needed))
        height = math.ceil(total_pixels_needed / width)
        
        img = Image.new("RGBA", (width, height), (0,0,0,0))

        x,y = 0,0
        for i in tqdm(range(0, len(text), 2), desc='Encoding text(rgba):'):
            index1 = ord(text[i])
            index2 = ord(text[i+1]) if i+1 < len(text) else 0
            rgba = (index1 >> 8, index1 & 0xFF, index2 >> 8, index2 & 0xFF)
            img.putpixel((x, y), rgba)
            if x == width - 1:
                x = 0
                y += 1
            else:
                x += 1
        return img

    def encodes_rgba_full(self, text: str) -> Image.Image:
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
    
    def base64_to_img(self, base64_str: str) -> Image.Image:
        from tools.ImageProcessing import binary_to_img
        # 将Base64文本解码回二进制数据
        binary_data = base64.b64decode(base64_str)

        # 将二进制数据转换为Image对象
        img = binary_to_img(binary_data)

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
        img = Image.open(img_path)

        if mode == 'grey':
            text = self.decodes_gray(img)
        elif mode == 'rgba':
            text = self.decodes_rgba(img)
        elif mode == 'rgba_full':
            text = self.decodes_rgba_full(img)
        else:
            raise ValueError(f'Unsupported mode: {mode}')
        
        with open(img_path.replace(f'.png', '.txt'), 'w', encoding='utf-8') as f:
            f.write(text)

    def decodes_gray(self, img: Image.Image) -> str:
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
            high = img.getpixel((i%width, i//width))  # 获取high
            low = img.getpixel(((i+1)%width, (i+1)//width))
            
            index = high * 256 + low  # 还原index
            text += chr(index)  # 转化为字符
            progress_bar.update(1)
            
        progress_bar.close()
        return text

    def decodes_rgba(self, img: Image.Image) -> str:
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
    
    def decodes_rgba_full(self, img: Image.Image) -> str:
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
            chars.append(chr(unicode_value))
            progress_bar.update(1)

        progress_bar.close()
        return ''.join(chars)
    
    def img_to_base64(self, img: Image.Image) -> str:
        from tools.ImageProcessing import img_to_binary
        # 将Image数据转换为二进制数据
        binary_data = img_to_binary(img)

        # 将二进制数据编码成Base64文本
        encoded_text = base64.b64encode(binary_data).decode('utf-8')

        return encoded_text
    
    def read_message_from_binary(self, binary_data: bytes) -> str:
        from tools.ImageProcessing import binary_to_img, img_to_binary

        img_len = len(img_to_binary(binary_to_img(binary_data)))
        return binary_data[img_len:]