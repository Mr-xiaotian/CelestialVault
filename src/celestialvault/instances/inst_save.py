# _*_ coding: utf-8 _*_

import json
import pickle
import subprocess
from pathlib import Path

import pandas as pd
from celestialflow import TaskChain, TaskStage

from .inst_error import FFmpegError
from .inst_fetch import Fetcher


class FetchStage(TaskStage):
    def get_args(self, task: object):
        return (task[0],)

    def process_result(self, task, result):
        return (result, task[1], task[2])


class SaveStage(TaskStage):
    pass


class Saver(object):
    def __init__(self, base_path=".", overwrite=False):
        self.overwrite = overwrite

        self.set_base_path(base_path)
        self.set_add_path("")

    def set_base_path(self, base_path):
        self.base_path = Path(base_path)

    def set_add_path(self, add_path):
        self.add_path = Path(add_path)

    def get_path(self, file_name, file_suffix):
        middle_path = self.base_path / self.add_path  # 拼接路径
        middle_path.mkdir(parents=True, exist_ok=True)  # 确保目录存在

        path: Path = middle_path / str(file_name)  # 拼接文件路径
        if file_suffix is not None:
            path = path.with_suffix(file_suffix)  # 添加后缀
        return path

    def can_overwrite(self, path):
        if not self.overwrite and Path(path).exists():  # 使用 Path 的 exists 方法
            return False
        return True

    def save_text(self, text, file_name, encoding="utf-8", file_suffix=None):
        path = self.get_path(file_name, file_suffix)
        if not self.can_overwrite(path):
            return path

        # 使用 Path 对象的写入操作
        path.write_text(text, encoding=encoding, errors="ignore")
        return path

    def add_text(self, text, file_name, encoding="utf-8", file_suffix=None):
        path = self.get_path(file_name, file_suffix)
        if not self.can_overwrite(path):
            return path

        with open(path, "a", encoding=encoding) as f:
            f.write(text.encode(encoding, "ignore").decode(encoding, "ignore"))
        return path

    def save_content(self, content, file_name, file_suffix=None):
        path = self.get_path(file_name, file_suffix)
        if not self.can_overwrite(path):
            return path

        # 写入二进制内容
        path.write_bytes(content)
        return path

    def save_dataframe(
        self, dataframe: pd.DataFrame, file_name: str, file_suffix=None
    ):
        path = self.get_path(file_name, file_suffix)
        if not self.can_overwrite(path):
            return path

        dataframe.to_csv(path, index=False, sep=",", encoding="utf-8-sig")

    def save_pickle(self, obj, file_name, file_suffix=None):
        path = self.get_path(file_name, file_suffix)
        if not self.can_overwrite(path):
            return path

        with open(path, "wb") as f:
            pickle.dump(obj, f)
        return path

    def save_json(self, data, file_name, file_suffix=None, encoding=None):
        path = self.get_path(file_name, file_suffix)
        if not self.can_overwrite(path):
            return path

        with open(path, "w", encoding=encoding) as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return path

    def download_url(self, url, file_name, file_suffix=None):
        path = self.get_path(file_name, file_suffix)
        if not self.can_overwrite(path):
            return path

        fetcher = Fetcher()
        content = fetcher.getContent(url)
        path.write_bytes(content)
        return path

    def download_urls(
        self,
        task_list: list[tuple[str, str, str]],
        chain_mode="serial",
        show_progress=False,
    ):
        """
        下载给定的 URL 列表，并将其内容保存到指定的文件中。

        :param task_list: list[tuple[str, str, str]]
                        每个元组包含三个元素:
                        - URL (str): 要下载内容的 URL
                        - 文件名 (str): 要保存内容的文件名
                        - 文件后缀 (str): 要保存文件的后缀名（例如 '.txt', '.jpg' 等）
        :param chain_mode: "serial" 或 "process"
                        - "serial": 任务链将串行执行
                        - "process": 任务链将并行执行
        :param show_progress: 是否显示下载和保存进度 (默认值为 False)
        :return: 一个字典，包含每个任务的最终结果
        """
        fetcher = Fetcher()  # 创建用于获取 URL 内容的 Fetcher 实例
        fetch_stage = FetchStage(
            fetcher.getContent,
            execution_mode="thread",
            progress_desc="urlsFetchProcess",
            show_progress=show_progress,
        )
        save_stage = SaveStage(
            self.save_content,
            execution_mode="serial",
            progress_desc="urlsSaveProcess",
            show_progress=show_progress,
            unpack_task_args=True,
        )

        # 创建 TaskChain 来管理 Fetch 和 Save 两个阶段的任务处理
        chain = TaskChain([fetch_stage, save_stage], chain_mode)
        chain.start_chain({fetch_stage.get_tag(): task_list})  # 开始任务树

    async def download_urls_async(self, task_list: list[tuple[str, str, str]]):
        # await self.fetcher.start_session()
        # await self.fetch_threader.start_async(task_list)
        # await self.fetcher.close_session()
        pass

    def download_m3u8(self, m3u8_url, file_name, file_suffix=None, timeout=3600):
        m3u8_path = self.get_path(file_name, file_suffix)
        if not self.can_overwrite(m3u8_path):
            return m3u8_path

        command = [
            "ffmpeg",
            "-protocol_whitelist",
            "file,http,https,tcp,tls,crypto",
            "-i",
            str(m3u8_url),
            "-c",
            "copy",
            m3u8_path,
        ]
        # 运行命令并捕获错误
        try:
            result = subprocess.run(
                command,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Download process timed out for {m3u8_url}.")
        except Exception as e:
            raise FFmpegError(f"Failed to download {m3u8_url}.", stderr=str(e))

        # 检查 FFmpeg 是否返回了错误
        if result.returncode != 0:
            error_msg = result.stderr.strip()
            raise FFmpegError(f"Failed to download {m3u8_url}.", stderr=error_msg)

        return m3u8_path
