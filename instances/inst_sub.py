import re, chardet
from tqdm import tqdm
from html import unescape
from urllib.parse import unquote
from pathlib import Path


class Suber:
    def __init__(self):
        self.special_character_removal = [
            ('(\t|\r|\f|\v|\0|　|| )+', ''),  # 移除制表符、回车符、换页符、垂直制表符、空字符、全角空格和特殊符号
            ('\~', '-'),  # 将波浪号替换为连字符
        ]

        self.newline_handling = [
            ('(?<!－|#|＊|◆|\*|=|＝|…|～|。|]|』|」|】|》|\)|）|!|！|\?|？|—|”|"|_|\.)\n', ''),  # 移除不在某些标点符号后的换行符
            ('(?<!\n)\n(?!\n)', '\n\n'),  # 确保单独的换行符前后有两个换行符
            ('(\n){3,}', '\n\n'),  # 限制连续换行符的数量为最多2个
        ]

        self.html_md_handling = [
            ('<br>', '\n'),  # 替换 HTML 换行标签为换行符
            ('<p>', ''), ('</p>', '\n'),  # 替换 HTML 段落标签
            ('<code.{0,50}?>', '```\n'), ('</code>', '```'),  # 替换 <code> 标签为 Markdown 代码块标记
            ('(?<!\n\n)<code>', '\n\n<code>'), ('</code>(?!\n\n)', '</code>\n\n'),  # 确保 <code> 标签前后有两个换行符
            ('(?<!\n)```', '\n```'), ('```(?!\n)', '```\n'),  # 确保 Markdown 代码块标记前后有换行符
        ]

        self.sub_list = (
            self.special_character_removal +
            self.newline_handling
        )
                         
        self.sub_name_list = [
            ('：','_'), (':','_'), (r'\\','_'), ('/','_'),
            ('\|','_'), ('\*','_'), ('-','_'),
            ('"', "_"), ("'", "_"), ('？', ''), ('\?', ''),
            (r'\t', '_'),('\.+', '_'), ('<', '_'), ('>', '_'),
        ]

    def clear_books(self, folder_path):
        from tools.FileOperations import handle_folder
        from constants import TXT_SUFFIXES

        rules = {suffix: (self.clear_book, lambda a: a) for suffix in TXT_SUFFIXES}

        return handle_folder(folder_path, rules)
        
    def clear_book(self, book_path, new_path):
        sample_len = min(100, book_path.stat().st_size)
        raw = book_path.read_bytes()[:sample_len]
        detect = chardet.detect(raw)['encoding']
        if not detect:
            raise ValueError("无法检测到编码")
        if 'GBK' in detect:
            detect = 'GB18030'
        elif 'ISO-8859' in detect:
            detect = 'GB18030'
        elif "IBM" in detect:
            detect = 'GB18030'
        elif "Windows" in detect:
            detect = 'GB18030'
        elif "EUC" in detect:
            detect = 'GB18030'
    
        book_text = book_path.read_text(encoding=detect)
        book_text = self.clear_text(book_text)
        new_path.write_text(book_text, encoding='utf-8')

    def clear_text(self, text):
        from tools.TextTools import pro_slash
        text = pro_slash(text)
        text = unquote(unescape(text))
        
        for sub in self.sub_list:
            text = re.sub(sub[0], sub[1], text, flags = re.S)

        #re_png = '<([0-9a-z]+)>'
        #png_list = re.findall(re_png, text)
        
        return text

    def sub_name(self, name):
        for sub in self.sub_name_list:
            name = re.sub(sub[0],sub[1], name)
        return name
