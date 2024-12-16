# _*_ coding: utf-8 _*_

import subprocess
from pathlib import Path
from os.path import splitext, join, exists
from instances.inst_task import ExampleTaskManager, SimpleTaskChain
from instances.inst_fetch import Fetcher


class FetchManager(ExampleTaskManager):
    def get_args(self, task: object):
        return (task[1], )
    
    def process_result(self, task, result):
        return (task[0], result, task[2])
    
    
class SaveManager(ExampleTaskManager):
    def get_args(self, task: object):
        return (task[0], task[1], task[2])
    

class Saver(object):
    def __init__(self, base_path = '.', overwrite = False):
        self.overwrite = overwrite

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

    def save_text(self, file_name, text, encoding = 'utf-8', suffix_name = '.txt'):
        if not file_name:
            return None
        
        path = self.get_path(file_name, suffix_name)
        if not self.overwrite and self.is_exist(path):
            return path
        
        with open(path, 'w', encoding = encoding) as f:
            f.write(text.encode(encoding, 'ignore').decode(encoding, "ignore"))
        return path

    def add_text(self, file_name, text, encoding = 'utf-8', suffix_name = '.txt'):
        if not file_name:
            return None
    
        path = self.get_path(file_name, suffix_name)
        if not self.overwrite and self.is_exist(path):
            return path
        
        with open(path, 'a', encoding = encoding) as f:
            f.write(text.encode(encoding, 'ignore').decode(encoding, "ignore"))
        return path

    def save_content(self, file_name, content, suffix_name='.dat'):
        path = self.get_path(file_name, suffix_name)
        if not self.overwrite and self.is_exist(path):
            return path
        
        with open(path, 'wb') as f:
            f.write(content)
        return path

    def download_urls(self, task_list:list[tuple[str,str,str]], chain_mode="serial", show_progress=False):
        """
        下载给定的 URL 列表，并将其内容保存到指定的文件中。

        :param task_list: list[tuple[str, str, str]] 
                        每个元组包含三个元素:
                        - 文件名 (str): 要保存内容的文件名
                        - URL (str): 要下载内容的 URL
                        - 文件后缀 (str): 要保存文件的后缀名（例如 '.txt', '.jpg' 等）
        :param chain_mode: "serial" 或 "parallel" 
                        - "serial": 任务链将串行执行
                        - "parallel": 任务链将并行执行
        :param show_progress: 是否显示下载和保存进度 (默认值为 False)
        :return: 一个字典，包含每个任务的最终结果
        """
        fetcher = Fetcher()  # 创建用于获取 URL 内容的 Fetcher 实例
        fetch_manager = FetchManager(fetcher.getContent, execution_mode='thread',
                                    progress_desc='urlsFetchProcess', show_progress=show_progress)
        
        save_manager = SaveManager(self.save_content, execution_mode='serial',
                                progress_desc='urlsSaveProcess', show_progress=False)

        # 创建 SimpleTaskChain 来管理 Fetch 和 Save 两个阶段的任务处理
        chain = SimpleTaskChain([fetch_manager, save_manager], chain_mode)
        chain.start_chain(task_list)  # 开始任务链

        final_result_dict = chain.get_final_result_dict()  # 获取任务链的最终结果字典
        return final_result_dict  # 返回结果

    async def download_urls_async(self, task_list:list[tuple[str,str,str]]):
        # await self.fetcher.start_session()
        # await self.fetch_threader.start_async(task_list)
        # await self.fetcher.close_session()
        pass

    def download_m3u8(self, m3u8_url, file_name, suffix_name = '.mp4'):
        path = self.get_path(file_name, suffix_name)
        if not self.overwrite and self.is_exist(path):
            return path
        
        command = [
            'ffmpeg',
            '-protocol_whitelist', 'file,http,https,tcp,tls,crypto',
            '-i', m3u8_url,
            '-c', 'copy', path
            ]
        subprocess.run(command)
        return path

    def download_texts(self, text_list, encoding = 'utf-8', suffix_name = '.md'):
        for file_name,text in text_list:
            self.download_text(file_name, text, encoding, suffix_name)

    def download_dataframe(self, file_name, dataframe, suffix_name = '.csv'):
        path = self.get_path(file_name, suffix_name)
        dataframe.to_csv(path, index=False, sep=',',encoding = 'utf-8-sig')
        