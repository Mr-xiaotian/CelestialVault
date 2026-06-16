import io
import json
import pickle
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd
from celestialflow import TaskChain, TaskStage

from ..tools.ImageProcessing import binary_to_img, convert_img_format
from .inst_error import FFmpegError
from .inst_fetch import Fetcher


def meta_get_content(fetcher: Fetcher):
    def get_content(task: tuple[str, str, str]) -> tuple[bytes, str, str]:
        """
        从抓取结果中提取内容。

        :param task: (url, file_name, file_suffix) 元组。
        :return: (内容, 文件名, 后缀) 元组。
        """
        url, file_name, file_suffix = task
        content: bytes = fetcher.getContent(url)  # type: ignore[reportUnknownMemberType]
        return content, file_name, file_suffix

    return get_content


def _save_content_for_task_stage(task: tuple[bytes, str, str | None]) -> Path:
    """供 TaskStage 使用的包装函数，保持返回 Path 以兼容任务链。"""
    content, file_name, file_suffix = task
    saver = Saver()
    path, _size = saver.save_content(content, file_name, file_suffix)
    return path


class Saver:
    """文件保存器，支持文本、二进制、DataFrame、JSON、Pickle 等多种格式的保存和下载。"""

    def __init__(self, base_path: str | Path = ".", overwrite: bool = False):
        """
        初始化保存器并设置基础路径与覆盖策略。

        :param base_path: 文件保存的基础路径。
        :param overwrite: 是否允许覆盖已存在文件。
        """
        self.overwrite = overwrite

        self.set_base_path(base_path)
        self.set_add_path("")

    def set_base_path(self, base_path: str | Path) -> None:
        """
        设置文件保存的基础路径。

        :param base_path: 基础路径。
        """
        self.base_path = Path(base_path)

    def set_add_path(self, add_path: str | Path) -> None:
        """
        设置附加子路径，与基础路径拼接形成最终保存目录。

        :param add_path: 附加子路径。
        """
        self.add_path = Path(add_path)

    def get_path(self, file_name: str, file_suffix: str | None) -> Path:
        """
        根据基础路径、附加路径、文件名和后缀生成完整文件路径，并确保目录存在。

        :param file_name: 文件名。
        :param file_suffix: 文件后缀（如 '.txt'）；为 None 则不添加后缀。
        :return: 完整的文件路径（Path）。
        """
        middle_path = self.base_path / self.add_path  # 拼接路径
        middle_path.mkdir(parents=True, exist_ok=True)  # 确保目录存在

        path: Path = middle_path / str(file_name)  # 拼接文件路径
        if file_suffix is not None:
            path = path.with_suffix(file_suffix)  # 添加后缀
        return path

    def _get_writable_path(
        self, file_name: str, file_suffix: str | None
    ) -> tuple[Path, bool]:
        """
        检查是否允许写入指定路径（若禁止覆盖且文件已存在则返回 False）。

        :param file_name: 文件名。
        :param file_suffix: 文件后缀（如 '.txt'）；为 None 则不添加后缀。
        :return: (路径, 是否允许写入) 元组。
        """
        path = self.get_path(file_name, file_suffix)
        if not self.overwrite and path.exists():
            return path, False
        return path, True

    @staticmethod
    def _get_size(file_path: Path) -> int:
        """获取文件大小（字节）。"""
        return file_path.stat().st_size

    # ==== core methods ====
    def _text_core(
        self,
        text: str,
        file_name: str,
        encoding: str = "utf-8",
        file_suffix: str | None = None,
    ) -> tuple[Path, int]:
        """
        直接将文本写入目标文件，不执行覆盖检查。

        :param text: 要保存的文本内容。
        :param file_name: 文件名。
        :param encoding: 文件编码。
        :param file_suffix: 文件后缀。
        :return: (路径, 文件大小) 元组。
        """
        path = self.get_path(file_name, file_suffix)
        path.write_text(text, encoding=encoding, errors="ignore")
        return path, self._get_size(path)

    def _content_core(
        self, content: bytes, file_name: str, file_suffix: str | None = None
    ) -> tuple[Path, int]:
        """
        直接将二进制内容写入目标文件，不执行覆盖检查。

        :param content: 要保存的二进制内容。
        :param file_name: 文件名。
        :param file_suffix: 文件后缀。
        :return: (路径, 文件大小) 元组。
        """
        path = self.get_path(file_name, file_suffix)
        path.write_bytes(content)
        return path, self._get_size(path)

    def _image_core(
        self, image: Any, file_name: str, file_suffix: str | None = None
    ) -> tuple[Path, int]:
        """
        直接将图像保存到目标文件，不执行覆盖检查。

        :param image: 要保存的图像对象。
        :param file_name: 文件名。
        :param file_suffix: 文件后缀。
        :return: (路径, 文件大小) 元组。
        """
        path = self.get_path(file_name, file_suffix)
        save_image = image
        if path.suffix:
            save_image = convert_img_format(image, path.suffix)
        save_image.save(path)
        return path, self._get_size(path)

    def _dataframe_core(
        self, dataframe: pd.DataFrame, file_name: str, file_suffix: str | None = None
    ) -> tuple[Path, int]:
        """
        直接将 DataFrame 写入目标文件，不执行覆盖检查。

        :param dataframe: 要保存的 DataFrame 对象。
        :param file_name: 文件名。
        :param file_suffix: 文件后缀。
        :return: (路径, 文件大小) 元组。
        """
        path = self.get_path(file_name, file_suffix)
        dataframe.to_csv(path, index=False, sep=",", encoding="utf-8-sig")  # type: ignore[reportUnknownMemberType]
        return path, self._get_size(path)

    def _pickle_core(
        self, obj: Any, file_name: str, file_suffix: str | None = None
    ) -> tuple[Path, int]:
        """
        直接将对象序列化到目标文件，不执行覆盖检查。

        :param obj: 要序列化的 Python 对象。
        :param file_name: 文件名。
        :param file_suffix: 文件后缀。
        :return: (路径, 文件大小) 元组。
        """
        path = self.get_path(file_name, file_suffix)
        with open(path, "wb") as f:
            pickle.dump(obj, f)
        return path, self._get_size(path)

    def _json_core(
        self,
        data: Any,
        file_name: str,
        file_suffix: str | None = None,
        encoding: str | None = None,
    ) -> tuple[Path, int]:
        """
        直接将数据写入 JSON 文件，不执行覆盖检查。

        :param data: 要保存的数据对象。
        :param file_name: 文件名。
        :param file_suffix: 文件后缀。
        :param encoding: 文件编码。
        :return: (路径, 文件大小) 元组。
        """
        path = self.get_path(file_name, file_suffix)
        with open(path, "w", encoding=encoding) as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return path, self._get_size(path)

    # ==== save methods ====
    def save_text(
        self,
        text: str,
        file_name: str,
        encoding: str = "utf-8",
        file_suffix: str | None = None,
    ) -> tuple[Path, int] | tuple[Path, None]:
        """
        将文本内容保存到文件。

        :param text: 要保存的文本内容。
        :param file_name: 文件名。
        :param encoding: 文件编码，默认 'utf-8'。
        :param file_suffix: 文件后缀。
        :return: (路径, 文件大小) 元组；不可写入时大小为 None。
        """
        path, can_write = self._get_writable_path(file_name, file_suffix)
        if not can_write:
            return path, None

        return self._text_core(text, file_name, encoding, file_suffix)

    def add_text(
        self,
        text: str,
        file_name: str,
        encoding: str = "utf-8",
        file_suffix: str | None = None,
    ) -> tuple[Path, int] | tuple[Path, None]:
        """
        将文本内容追加到文件末尾。

        :param text: 要追加的文本内容。
        :param file_name: 文件名。
        :param encoding: 文件编码，默认 'utf-8'。
        :param file_suffix: 文件后缀。
        :return: (路径, 文件大小) 元组；不可写入时大小为 None。
        """
        path, can_write = self._get_writable_path(file_name, file_suffix)
        if not can_write:
            return path, None

        with open(path, "a", encoding=encoding) as f:
            f.write(text.encode(encoding, "ignore").decode(encoding, "ignore"))
        return path, self._get_size(path)

    def save_content(
        self, content: bytes, file_name: str, file_suffix: str | None = None
    ) -> tuple[Path, int] | tuple[Path, None]:
        """
        将二进制内容保存到文件。

        :param content: 要保存的二进制内容。
        :param file_name: 文件名。
        :param file_suffix: 文件后缀。
        :return: (路径, 文件大小) 元组；不可写入时大小为 None。
        """
        path, can_write = self._get_writable_path(file_name, file_suffix)
        if not can_write:
            return path, None

        return self._content_core(content, file_name, file_suffix)

    def save_image(
        self, image: Any, file_name: str, file_suffix: str | None = None
    ) -> tuple[Path, int] | tuple[Path, None]:
        """
        将图像保存为文件。

        :param image: 要保存的图像对象。
        :param file_name: 文件名。
        :param file_suffix: 文件后缀。
        :return: (路径, 文件大小) 元组；不可写入时大小为 None。
        """
        path, can_write = self._get_writable_path(file_name, file_suffix)
        if not can_write:
            return path, None

        return self._image_core(image, file_name, file_suffix)

    def save_dataframe(
        self, dataframe: pd.DataFrame, file_name: str, file_suffix: str | None = None
    ) -> tuple[Path, int] | tuple[Path, None]:
        """
        将 DataFrame 保存为 CSV 文件。

        :param dataframe: 要保存的 DataFrame 对象。
        :param file_name: 文件名。
        :param file_suffix: 文件后缀。
        :return: (路径, 文件大小) 元组；不可写入时大小为 None。
        """
        path, can_write = self._get_writable_path(file_name, file_suffix)
        if not can_write:
            return path, None

        return self._dataframe_core(dataframe, file_name, file_suffix)

    def save_pickle(
        self, obj: Any, file_name: str, file_suffix: str | None = None
    ) -> tuple[Path, int] | tuple[Path, None]:
        """
        将 Python 对象序列化为 pickle 文件。

        :param obj: 要序列化的 Python 对象。
        :param file_name: 文件名。
        :param file_suffix: 文件后缀。
        :return: (路径, 文件大小) 元组；不可写入时大小为 None。
        """
        path, can_write = self._get_writable_path(file_name, file_suffix)
        if not can_write:
            return path, None

        return self._pickle_core(obj, file_name, file_suffix)

    def save_json(
        self,
        data: Any,
        file_name: str,
        file_suffix: str | None = None,
        encoding: str | None = None,
    ) -> tuple[Path, int] | tuple[Path, None]:
        """
        将数据保存为格式化的 JSON 文件。

        :param data: 要保存的数据对象。
        :param file_name: 文件名。
        :param file_suffix: 文件后缀。
        :param encoding: 文件编码。
        :return: (路径, 文件大小) 元组；不可写入时大小为 None。
        """
        path, can_write = self._get_writable_path(file_name, file_suffix)
        if not can_write:
            return path, None

        return self._json_core(data, file_name, file_suffix, encoding)

    # ==== delete methods ====
    def delete_file(
        self, file_name: str, file_suffix: str | None = None
    ) -> tuple[Path, bool]:
        """
        删除指定文件。

        :param file_name: 文件名。
        :param file_suffix: 文件后缀。
        :return: (文件路径, 是否成功删除) 元组。
        """
        path = self.get_path(file_name, file_suffix)
        if path.exists():
            path.unlink()
            return path, True
        return path, False

    # ==== download methods ====
    def download_text(
        self,
        url: str,
        file_name: str,
        encoding: str = "utf-8",
        file_suffix: str | None = None,
    ) -> tuple[Path, int] | tuple[Path, None]:
        """
        从 URL 下载文本并保存为文件。

        :param url: 文本资源的 URL 地址。
        :param file_name: 文件名。
        :param encoding: 保存文件时使用的编码。
        :param file_suffix: 文件后缀。
        :return: (路径, 文件大小) 元组；不可写入时大小为 None。
        """
        path, can_write = self._get_writable_path(file_name, file_suffix)
        if not can_write:
            return path, None

        fetcher = Fetcher()
        text: str = fetcher.getText(url)  # type: ignore[reportUnknownMemberType]
        return self._text_core(text, file_name, encoding, file_suffix)

    def download_content(
        self, url: str, file_name: str, file_suffix: str | None = None
    ) -> tuple[Path, int] | tuple[Path, None]:
        """
        从 URL 下载内容并保存为文件。

        :param url: 下载的 URL 地址。
        :param file_name: 文件名。
        :param file_suffix: 文件后缀。
        :return: (路径, 文件大小) 元组；不可写入时大小为 None。
        """
        path, can_write = self._get_writable_path(file_name, file_suffix)
        if not can_write:
            return path, None

        fetcher = Fetcher()
        content: bytes = fetcher.getContent(url)  # type: ignore[reportUnknownMemberType]
        return self._content_core(content, file_name, file_suffix)

    def download_image(
        self, url: str, file_name: str, file_suffix: str | None = None
    ) -> tuple[Path, int] | tuple[Path, None]:
        """
        从 URL 下载图片并保存为文件。

        :param url: 图片的 URL 地址。
        :param file_name: 文件名。
        :param file_suffix: 文件后缀。
        :return: (路径, 文件大小) 元组；不可写入时大小为 None。
        """
        path, can_write = self._get_writable_path(file_name, file_suffix)
        if not can_write:
            return path, None

        fetcher = Fetcher()
        content: bytes = fetcher.getContent(url)  # type: ignore[reportUnknownMemberType]
        image = binary_to_img(content)
        return self._image_core(image, file_name, file_suffix)

    def download_dataframe(
        self,
        url: str,
        file_name: str,
        file_suffix: str | None = None,
        read_kwargs: dict[str, Any] | None = None,
    ) -> tuple[Path, int] | tuple[Path, None]:
        """
        从 URL 下载表格文本并解析为 DataFrame 后保存。

        :param url: 表格资源的 URL 地址。
        :param file_name: 文件名。
        :param file_suffix: 文件后缀。
        :param read_kwargs: 传给 pandas.read_csv 的额外参数。
        :return: (路径, 文件大小) 元组；不可写入时大小为 None。
        """
        path, can_write = self._get_writable_path(file_name, file_suffix)
        if not can_write:
            return path, None

        fetcher = Fetcher()
        text: str = fetcher.getText(url)  # type: ignore[reportUnknownMemberType]
        dataframe: pd.DataFrame = pd.read_csv(  # type: ignore[reportUnknownArgumentType, reportCallIssue]
            io.StringIO(text), **(read_kwargs or {})
        )
        return self._dataframe_core(dataframe, file_name, file_suffix)  # type: ignore[reportUnknownArgumentType]

    def download_pickle(
        self, url: str, file_name: str, file_suffix: str | None = None
    ) -> tuple[Path, int] | tuple[Path, None]:
        """
        从 URL 下载 pickle 二进制内容并反序列化后保存。

        :param url: pickle 资源的 URL 地址。
        :param file_name: 文件名。
        :param file_suffix: 文件后缀。
        :return: (路径, 文件大小) 元组；不可写入时大小为 None。
        """
        path, can_write = self._get_writable_path(file_name, file_suffix)
        if not can_write:
            return path, None

        fetcher = Fetcher()
        content: bytes = fetcher.getContent(url)  # type: ignore[reportUnknownMemberType]
        obj = pickle.loads(content)
        return self._pickle_core(obj, file_name, file_suffix)

    def download_json(
        self,
        url: str,
        file_name: str,
        file_suffix: str | None = None,
        encoding: str | None = None,
    ) -> tuple[Path, int] | tuple[Path, None]:
        """
        从 URL 下载 JSON 内容并保存为文件。

        :param url: JSON 资源的 URL 地址。
        :param file_name: 文件名。
        :param file_suffix: 文件后缀。
        :param encoding: 保存文件时使用的编码。
        :return: (路径, 文件大小) 元组；不可写入时大小为 None。
        """
        path, can_write = self._get_writable_path(file_name, file_suffix)
        if not can_write:
            return path, None

        fetcher = Fetcher()
        text: str = fetcher.getText(url)  # type: ignore[reportUnknownMemberType]
        data = json.loads(text)
        return self._json_core(data, file_name, file_suffix, encoding)

    def download_urls(
        self,
        task_list: list[tuple[str, str, str]],
        stage_mode: str = "serial",
    ) -> None:
        """
        下载给定的 URL 列表，并将其内容保存到指定的文件中。

        :param task_list: list[tuple[str, str, str]]
                        每个元组包含三个元素:
                        - URL (str): 要下载内容的 URL
                        - 文件名 (str): 要保存内容的文件名
                        - 文件后缀 (str): 要保存文件的后缀名（例如 '.txt', '.jpg' 等）
        :param stage_mode: "serial" 或 "process"
                        - "serial": 任务链将串行执行
                        - "process": 任务链将并行执行
        :return: 一个字典，包含每个任务的最终结果
        """
        fetcher = Fetcher()  # 创建用于获取 URL 内容的 Fetcher 实例
        fetch_stage: TaskStage[Any, Any] = TaskStage(  # type: ignore[reportUnknownVariableType]
            "urlsFetchProcess",
            meta_get_content(fetcher),
            execution_mode="thread",
        )
        save_stage: TaskStage[Any, Any] = TaskStage(  # type: ignore[reportUnknownVariableType]
            "urlsSaveProcess",
            _save_content_for_task_stage,
            execution_mode="serial",
        )

        # 创建 TaskChain 来管理 Fetch 和 Save 两个阶段的任务处理
        chain = TaskChain(
            "DownloadUrls", [fetch_stage, save_stage], stage_mode=stage_mode
        )
        chain.start_chain({fetch_stage.get_tag(): task_list})  # type: ignore[reportUnknownMemberType]  # 开始任务树

    async def download_urls_async(self, task_list: list[tuple[str, str, str]]):
        """
        异步批量下载 URL 列表（尚未实现）。

        :param task_list: 任务列表，每个元组包含 (URL, 文件名, 文件后缀)。
        """
        # await self.fetcher.start_session()
        # await self.fetch_threader.start_async(task_list)
        # await self.fetcher.close_session()
        pass

    def download_m3u8(
        self,
        m3u8_url: str,
        file_name: str,
        file_suffix: str | None = None,
        timeout: int = 3600,
    ) -> tuple[Path, int] | tuple[Path, None]:
        """
        使用 ffmpeg 下载 m3u8 流媒体并保存为文件。

        :param m3u8_url: m3u8 流媒体的 URL 地址。
        :param file_name: 保存的文件名。
        :param file_suffix: 文件后缀。
        :param timeout: 下载超时时间（秒），默认 3600。
        :return: (路径, 文件大小) 元组；不可写入时大小为 None。
        :raises TimeoutError: 下载超时时抛出。
        :raises FFmpegError: ffmpeg 执行失败时抛出。
        """
        m3u8_path, can_overwrite = self._get_writable_path(file_name, file_suffix)
        if not can_overwrite:
            return m3u8_path, None

        command: list[str | Path] = [
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
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as e:
            raise TimeoutError(f"Download process timed out for {m3u8_url}.") from e
        except Exception as e:
            raise FFmpegError(f"Failed to download {m3u8_url}.", stderr=str(e)) from e

        # 检查 FFmpeg 是否返回了错误
        if result.returncode != 0:
            error_msg = result.stderr.strip()
            raise FFmpegError(f"Failed to download {m3u8_url}.", stderr=error_msg)

        return m3u8_path, self._get_size(m3u8_path)
