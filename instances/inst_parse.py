import re
from typing import List, Tuple
from bs4 import Tag, NavigableString
from json import loads, JSONDecodeError


class HTMLContentParser:
    """
    一个用于解析HTML内容的类，将文本、图片和视频信息提取为markdown列表、视频列表和图片列表。
    """

    def __init__(self):
        pass

    def init_list(self):
        self.md_list: List[str] = []
        self.video_list: List[str] = []
        self.img_list: List[Tuple[str, str]] = []

    def parse(self, element: Tag):
        """
        对指定的HTML Tag元素进行解析，并将结果储存在当前实例的md_list、video_list、img_list中。
        """
        if not element:
            return
        self.init_list()
        self._traverse(element)

    def _traverse(self, element: Tag):
        """
        递归遍历HTML元素树，将文本、图片、视频信息添加到实例的属性中。
        """
        if element is None:
            return

        if isinstance(element, NavigableString):
            self._handle_text(element)
        elif isinstance(element, Tag):
            # 处理图片
            if element.name == 'img' and element.get('title') is not None:
                self._handle_image(element)

            # 处理视频
            classes = element.get('class', [])
            if 'dplayer' in classes:
                self._handle_video(element)

            # 递归子元素
            for child in element.children:
                self._traverse(child)

    def _handle_text(self, text_node: NavigableString):
        text = text_node.strip()
        if not text:
            return
        self.md_list.append(text)

    def _handle_image(self, img_tag: Tag):
        img_src = img_tag.get('data-xkrkllgl')
        img_title = img_tag.get('title').replace(':', '_')
        if not img_src:
            return
        # 确保markdown中图片语法：![alt_text](url)
        # 这里假设img_title作为alt文本，img_src为图片URL
        self.md_list.append(f"![{img_title}]({img_src})")
        self.img_list.append((img_title, img_src))

    def _handle_video(self, video_tag: Tag):
        video_config = video_tag.get('data-config')
        if not video_config:
            return
        try:
            config_json = loads(video_config)
        except JSONDecodeError:
            config_json = {}

        video_url = config_json.get('url', '')
        match = re.search(r'([0-9a-z]*?).m3u8', video_url, re.S)
        if match:
            video_name = match.group(1)
        else:
            video_name = "unknown_video_name"

        # 将视频以<video>标签的HTML形式插入md_list
        # 注：Markdown本身不支持原生video标签，如果需要严格纯Markdown，这里可改为文字链接或其它方案
        self.md_list.append(f'<video controls src="{video_name}.mp4" width="480" height="320">{video_url}</video>')
        self.video_list.append((video_name, video_url))