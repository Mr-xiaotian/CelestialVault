import math
from PIL import Image
from tqdm import tqdm
from itertools import product

class ImgEncoder:
    def encode_text(self, text_path: str, mode='grey') -> None:
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

    def encodes_gray(self, text: str) -> Image:
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

    def encodes_rgba(self, text: str) -> Image:
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

    def encodes_rgba_full(self, text: str) -> Image:
        str_len = len(text)
        width = math.ceil(str_len ** 0.5)
        img = Image.new("RGBA", (width, width), 0x0)

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


class ImgDecoder:
    def decode_image(self, img_path, mode='grey') -> None:
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

    def decodes_gray(self, img: Image) -> str:
        '''
        将gray图像解码为字符串
        :param im: 图像对象
        :return: 解码后的字符串
        '''
        width, height = img.size
        text = ""
        progress_bar = tqdm(total=height * width // 2, desc='Decoding img(grey):')
        for y, x in product(range(height), range(0, width, 2)):  # 两个像素表示一个字符
            high = img.getpixel((x, y))  # 获取high
            if x + 1 < width:  # 如果还有像素，获取low
                low = img.getpixel((x+1, y))
            else:
                low = 0
            index = high * 256 + low  # 还原index
            text += chr(index)  # 转化为字符
            progress_bar.update(1)
            
        progress_bar.close()
        return text

    def decodes_rgba(self, img: Image) -> str:
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
    
    def decodes_rgba_full(self, img: Image) -> str:
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


if __name__ == '__main__':
    text_path = r'G:\Project\test\寻找走丢的舰娘(34653).txt'
    image_path_grey = r'G:\Project\test\寻找走丢的舰娘(34653)(grey).png'
    image_path_rgba = r'G:\Project\test\寻找走丢的舰娘(34653)(rgba).png'
    image_path_rgba_full = r'G:\Project\test\寻找走丢的舰娘(34653)(rgba_full).png'

    # 编码
    encoder = ImgEncoder()
    # encoder.encode_text(text_path, mode='grey')
    # encoder.encode_text(text_path, mode='rgba')
    # encoder.encode_text(text_path, mode='rgba_full')
    
    # 解码
    decoder = ImgDecoder()
    decoder.decode_image(image_path_grey, mode='grey')
    # decoder.decode_image(image_path_rgba, mode='rgba')
    # decoder.decode_image(image_path_rgba_full, mode='rgba_full')

