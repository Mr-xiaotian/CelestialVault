# _*_ coding: utf-8 _*_

import logging
import subprocess
from os.path import splitext, join, exists
from .my_thread import ExampleThreadManager
from .inst_fetch import Fetcher
from ..tools import create_folder

class FetchThread(ExampleThreadManager):
    def get_args(self, obj: object):
        return (obj[1], )
    
    def process_result(self):
        result_dict = self.get_result_dict()
        return [(d[0], result_dict[d], d[2]) for d in result_dict]
    
    
class SaveThread(ExampleThreadManager):
    def get_args(self, obj: object):
        return (obj[0], obj[1], obj[2])
    
    def process_result(self, dictory_len, path):
        logging.info(f'{dictory_len} files has saved to {path}.')
        return
    

class Saver(object):
    def __init__(self, base_path = '.', show_progress=False, **kwargs):   
        self.fetcher = Fetcher(**kwargs)
        self.fetch_threader = FetchThread(
            self.fetcher.getContent, 
            tqdm_desc='urlsFetchProcess', 
            show_progress=show_progress)
        self.save_threader = SaveThread(
            self.download_content, 
            tqdm_desc='urlsSaveProcess', 
            show_progress=False)

        self.set_base_path(base_path)
        self.add_path = ''

    def set_base_path(self, base_path):
        self.base_path = create_folder(base_path)

    def set_add_path(self, add_path):
        self.add_path = add_path

    def get_path(self, file_name, suffix_name):
        middle_path = create_folder(f'{self.base_path}/{self.add_path}')
        path = join(middle_path, str(file_name))
        
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
        logging.info(f'save {file_name} in {path}')
        with open(path, 'wb') as f:
            f.write(content)

    def download_urls(self, url_list:list[tuple[str,str,str]], start_type="serial"):
        logging.info(f'Start download {len(url_list)} urls by {start_type}.')
        self.fetch_threader.start(url_list, start_type)
        self.fetch_threader.handle_error()
        content_list = self.fetch_threader.process_result()

        logging.info(f'Start save {len(content_list)} urls by {start_type}.')
        self.save_threader.start(content_list, start_type = start_type)
        self.save_threader.handle_error()
        self.save_threader.process_result(
            len(content_list), self.base_path + '\\' + self.add_path
            )
        
    async def download_urls_async(self, url_list:list[tuple[str,str,str]]):
        # await self.fetcher.start_session()
        # await self.fetch_threader.start_async(url_list)
        # await self.fetcher.close_session()
        pass

    def download_m3u8(self, output_path, m3u8_url):
        command = [
            'ffmpeg',
            '-protocol_whitelist', 'file,http,https,tcp,tls,crypto',
            '-i', m3u8_url,
            '-c', 'copy',
            output_path
            ]
        subprocess.run(command)

    def download_texts(self, text_list, encoding = 'utf-8', suffix_name = '.md'):
        for file_name,text in text_list:
            self.download_text(file_name, text, encoding, suffix_name)

    def download_dataframe(self, file_name, dataframe, suffix_name = '.csv'):
        path = self.get_path(file_name, suffix_name)
        dataframe.to_csv(path, index=False, sep=',',encoding = 'utf-8-sig')
        