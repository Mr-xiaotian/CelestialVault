# _*_ coding: utf-8 _*_

from os import walk,listdir,rename
from os.path import splitext, join, exists
import asyncio
import my_thread
import common_functions as cf
from .inst_fetch import Fetcher
        

class FetchThread(my_thread.ThreadManager):
    def get_args(self, obj: object):
        return (obj[1], )
    
    def process_result(self):
        result_dict = self.get_result_dict()
        return [(d[0], result_dict[d], d[2]) for d in result_dict]
    
    def handle_error(self):
        if not self.get_error_list():
            return ''
        # print(f'Some Error Happen', end='')
        error_text_list = []
        for error in self.get_error_list():
            error_text_list.append(f'{error}')

        return '\n'.join(error_text_list)
    
class SaveThread(my_thread.ExampleThreadManager):
    def get_args(self, obj: object):
        return (obj[0], obj[1], obj[2])
    
    def process_result(self, dictory_len, path):
        # print(f'{dictory_len}个文件已下载至{path}')
        return


class Saver(object):
    def __init__(self, base_path = '.', show_progress=False, **kwargs):   
        self.fetcher = Fetcher(**kwargs)
        self.fetch_threader = FetchThread(
            self.fetcher.getHtml_async_content, 
            tqdm_desc='urlsFetchProcess', show_progress=show_progress)
        self.save_threader = SaveThread(
            self.download_content, 
            tqdm_desc='urlsSaveProcess', show_progress=False)

        self.set_base_path(base_path)
        self.add_path = ''

    def set_base_path(self, base_path):
        self.base_path = cf.creat_folder(base_path)

    def set_add_path(self, add_path):
        self.add_path = add_path

    def get_path(self, file_name, suffix_name):
        middle_path = cf.creat_folder(self.base_path + '\\' + self.add_path)
        path = join(middle_path, file_name)
        
        if splitext(path)[1] == '':
            path += suffix_name
        return path
    
    def is_exist(self, file_name, suffix_name):
        return exists(self.get_path(file_name, suffix_name))

    def download_text(self, file_name, text, encoding = 'utf-8', suffix_name = '.md'):
        path = self.get_path(file_name, suffix_name)
        with open(path, 'w', encoding = encoding) as f:
            f.write(text.encode(encoding, 'ignore').decode(encoding, "ignore"))

    def add_text(self, file_name, text, encoding = 'utf-8', suffix_name = '.md'):
        path = self.get_path(file_name, suffix_name)
        with open(path, 'a', encoding = encoding) as f:
            f.write(text.encode(encoding, 'ignore').decode(encoding, "ignore"))

    def download_content(self, file_name, content, suffix_name='.dat'):
        path = self.get_path(file_name, suffix_name)
        with open(path, 'wb') as f:
            f.write(content)

    async def download_urls(self, url_list:list[tuple[str,str,str]], start_type="serial"):
        await self.fetcher.start_session()
        await self.fetch_threader.start_async(url_list)
        await self.fetcher.close_session()
        error_text = self.fetch_threader.handle_error()
        content_list = self.fetch_threader.process_result()
        if error_text != '':
            self.download_text('fetcher_error', error_text, suffix_name='.txt')

        self.save_threader.start(content_list, start_type = start_type)
        self.save_threader.handle_error()
        self.save_threader.process_result(
            len(content_list), self.base_path + '\\' + self.add_path)
        
    def download_texts(self, text_list, encoding = 'utf-8', suffix_name = '.md'):
        for file_name,text in text_list:
            self.download_text(file_name, text, encoding, suffix_name)

    def download_dataframe(self, file_name, dataframe, suffix_name = '.csv'):
        path = self.get_path(file_name, suffix_name)
        dataframe.to_csv(path, index=False,
                         sep=',',encoding = 'utf-8-sig')

if __name__ == '__main__':
    saver = Saver(r'F:\下载')
    saver.set_add_path('test_jpg')

    li = ['https://ttzytp.com/dongman/xvhu6d.jpg',
        'https://ttzytp.com/dongman/xvjq0t.jpg',
        'https://ttzytp.com/dongman/xvlwc7.jpg',
        'https://ttzytp.com/dongman/xvoi5z.jpg',
        'https://ttzytp.com/dongman/xvznus.jpg',
        'https://ttzytp.com/dongman/xw2j01.jpg',
        'https://ttzytp.com/dongman/xw4svq.jpg',
        'https://ttzytp.com/dongman/xw6sif.jpg',
        'https://ttzytp.com/dongman/xw9d0e.jpg',
        'https://ttzytp.com/dongman/xwkvsc.jpg',
        'https://ttzytp.com/dongman/xwne5w.jpg',
        'https://ttzytp.com/dongman/xwq5ud.jpg',
        'https://ttzytp.com/dongman/xwst1v.jpg',
        'https://ttzytp.com/dongman/xwv52q.jpg',
        'https://ttzytp.com/dongman/xx6sjn.jpg',
        'https://ttzytp.com/dongman/xx8ty1.jpg',
        'https://ttzytp.com/dongman/xxc8h6.jpg',
        'https://ttzytp.com/dongman/xxeni2.jpg',
        'https://ttzytp.com/dongman/xxgmgl.jpg',
        'https://ttzytp.com/dongman/xxrabi.jpg',
        'https://ttzytp.com/dongman/xxtftc.jpg',
        'https://ttzytp.com/dongman/xxvkih.jpg',
        'https://ttzytp.com/dongman/xxy5gf.jpg',
        'https://ttzytp.com/dongman/xy0965.jpg',
        'https://ttzytp.com/dongman/xy26a8.jpg',
        'https://ttzytp.com/dongman/xyd87f.jpg']

    saver.set_add_path('test_jpg')
    saver.download_urls([(num, i, '.jpg') for num,i in enumerate(li)])
