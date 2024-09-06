# _*_ coding: utf-8 _*_

import logging
import subprocess
from pathlib import Path
from os.path import splitext, join, exists
from instances.task_manager import ExampleTaskManager, TaskChain
from instances.inst_fetch import Fetcher


class FetchThread(ExampleTaskManager):
    def get_args(self, obj: object):
        return (obj[1], )
    
    def process_result(self, task, result):
        return (task[0], result, task[2])
    
    
class SaveThread(ExampleTaskManager):
    def get_args(self, obj: object):
        return (obj[0], obj[1], obj[2])
    

class Saver(object):
    def __init__(self, base_path = '.', show_progress=False, **kwargs):   
        self.fetcher = Fetcher(**kwargs)
        self.fetch_threader = FetchThread(
            self.fetcher.getContent, 
            tqdm_desc='urlsFetchProcess', 
            show_progress=show_progress)
        self.save_threader = SaveThread(
            self.save_content, 
            tqdm_desc='urlsSaveProcess', 
            show_progress=False)

        self.set_base_path(base_path)
        self.set_add_path('')

    def set_base_path(self, base_path):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def set_add_path(self, add_path):
        self.add_path = Path(add_path)

    def get_path(self, file_name, suffix_name):
        middle_path = self.base_path / self.add_path
        middle_path.mkdir(parents=True, exist_ok=True)
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
        return path

    def add_text(self, file_name, text, encoding = 'utf-8', suffix_name = '.md'):
        path = self.get_path(file_name, suffix_name)
        with open(path, 'a', encoding = encoding) as f:
            f.write(text.encode(encoding, 'ignore').decode(encoding, "ignore"))
        return path

    def save_content(self, file_name, content, suffix_name='.dat'):
        path = self.get_path(file_name, suffix_name)
        with open(path, 'wb') as f:
            f.write(content)
        return path

    def download_urls(self, task_list:list[tuple[str,str,str]], execution_mode="serial"):
        self.fetch_threader.set_execution_mode(execution_mode)
        self.save_threader.set_execution_mode(execution_mode)

        chain = TaskChain([self.fetch_threader, self.save_threader])
        chain.start_chain(task_list)

        final_result_dict = chain.get_final_result_dict()
        return final_result_dict
        
    async def download_urls_async(self, task_list:list[tuple[str,str,str]]):
        # await self.fetcher.start_session()
        # await self.fetch_threader.start_async(task_list)
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
        