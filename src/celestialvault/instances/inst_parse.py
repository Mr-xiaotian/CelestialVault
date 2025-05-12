from typing import List, Tuple

from bs4 import NavigableString, Tag


class HTMLContentParser:
    """
    一个用于解析HTML内容的类，将文本、图片和视频信息提取为markdown列表、视频列表和图片列表。
    """
    def __init__(self):
        pass

    def init_list(self):
        self.md_list: List[str] = []
        self.video_list: List[Tuple[str, str]] = []
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
            if element.name == 'img':
                img_name, img_url = self.get_image_info(element)
                if img_name and img_url:
                    self._handle_image(img_name, img_url)

            # 处理视频
            classes = element.get('class', [])
            if 'dplayer' in classes:
                video_name, video_url = self.get_video_info(element)
                if video_name and video_url:
                    self._handle_video(video_name, video_url)

            # 递归子元素
            for child in element.children:
                self._traverse(child)

    def _handle_text(self, text_node: NavigableString):
        """
        处理文本节点，将文本添加到markdown列表中。
        如果文本为空，则不添加。
        """
        text = text_node.strip()
        if not text:
            return
        self.md_list.append(text)

    def _handle_image(self, img_name: str, img_url: str):
        """
        处理图片，将图片信息添加到markdown列表和图片列表中。
        """
        self.md_list.append(f"![{img_url}]({img_name})")
        self.img_list.append((img_name, img_url))

    def _handle_video(self, video_name: str, video_url: str):
        """
        处理视频，将视频信息添加到markdown列表和视频列表中。
        """
        self.md_list.append(f'<video controls src="{video_name}.mp4" width="480" height="320">{video_url}</video>')
        self.video_list.append((video_name, video_url))

    def get_image_info(self, img_tag: Tag) -> Tuple[str, str]:
        """
        获取图片相关信息的方法，可以在子类中重写。
        返回 (img_name, img_url)
        """
        return "unknown_img_name", "unknown_img_url"

    def get_video_info(self, video_tag: Tag) -> Tuple[str, str]:
        """
        获取视频相关信息的方法，可以在子类中重写。
        返回 (video_name, video_url)
        """
        return "unknown_video_name", "unknown_video_url"
