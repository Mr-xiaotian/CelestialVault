import re, chardet, tqdm
from os import listdir
from os.path import getsize
from html import unescape
from urllib.parse import quote,unquote


class Suber:
    def __init__(self):
        self.sub_list = [#('[0-9a-zA-Z④∨４Ｆｈ２ｕ]*(,|\.|，|`|。){0,1}' + \
                         # '(c|C|с|Ｃ|ㄈ|ｃ)(o|0|〇|☉|０|ò|&)(m|M|Μ|Ｍ|㎡|М|#)', ''),
                         ('(\t|\0|　)+', ''), ('\~', '-'),
                         ('<br>', '\n'), ('<p>', ''), ('</p>', '\n'),
                         ('(\n){4,25}', '\n'*3),
                         ('(?<!\n\n)<code>', '\n\n<code>'),
                         ('</code>(?!\n\n)', '</code>\n\n'),
                         ('<code.{0,50}?>', '```\n'),
                         ('</code>', '```'),
                         ('(?<!\n)```', '\n```'),
                         ('```(?!\n)', '```\n'),
                         ('(?<!\n)\n(?!\n)', '\n\n'),
                         ('\s{3,}', '\n\n'), ('', ''),
                         ('　', '')
                         (r'(?<![.!?。！？])\n', '')
                         ]
                         
        self.sub_name_list = [('：','_'), (':','_'), (r'\\','_'), ('/','_'),
                             ('\|','_'), ('\*','_'), ('-','_'),
                             ('"', "_"), ("'", "_"), ('？', ''), ('\?', ''),
                             (r'\t', '_'),('\.+', '_'), ('<', '_'), ('>', '_'),
                             ]

    def clear_books(self, base_path):
        book_list = listdir(base_path)
        error_list = []

        for book in book_list:
            print(book.split('.')[0], end = '')
            book_path = base_path + '\\' + book
            sample_len = min(100, getsize(book_path))
            raw = open(book_path, 'rb').read(sample_len)
            detect = chardet.detect(raw)['encoding']
            if 'GB' in detect:
                detect = 'GB18030'
            
            try:
                with open(book_path, 'r', encoding = detect) as f:
                    book_text = f.read()
                book_text = self.clear_texts(book_text)  
                
                with open(base_path + '\\' + book, 'w', encoding = 'utf-8') as f:
                    f.write(book_text)

                print('成功')
            except Exception as e:
                print(f'清理失败')
                error_list.append((book_path, e))
                
        return error_list

    def clear_texts(self, texts, dicts = {}):
        # from ..tools import pro_slash
        # texts = pro_slash(texts)
        texts = unquote(unescape(texts))
        
        for sub in self.sub_list:
            texts = re.sub(sub[0], sub[1], texts, flags = re.S)
            pass
        
        for png_id in dicts:
            replace_text = f'<{png_id}>'
            texts = texts.replace(replace_text, dicts[png_id])

        #re_png = '<([0-9a-z]+)>'
        #png_list = re.findall(re_png, texts)
        
        return texts

    def sub_name(self, name):
        for sub in self.sub_name_list:
            name = re.sub(sub[0],sub[1], name)
        return name

if __name__ == '__main__':
    suber = Suber()

    suber.sub_list += [('(?<!－|#|＊|◆|\*|=|＝|…|～|。|]|』|」|】|》|\)|）|!|！|\?|？|—|”|"|_|\.)\n', ''),
                       ('\n', '\n'*2),]
    #suber.clear_books(r'G:\书籍\文件夹\')

    print(suber.sub_name(''))
