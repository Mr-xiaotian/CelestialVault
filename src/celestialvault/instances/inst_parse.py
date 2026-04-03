
from bs4 import NavigableString, Tag


class HTMLContentParser:
    """
    一个用于解析HTML内容的类，将文本、图片和视频信息提取为markdown列表、视频列表和图片列表。
    """

    def __init__(self):
        pass

    def init_list(self):
        """
        初始化 markdown、视频和图片列表，清空上次解析结果。
        """
        self.md_list: list[str] = []
        self.video_list: list[tuple[str, str]] = []
        self.img_list: list[tuple[str, str]] = []

    def parse(self, element: Tag):
        """
        对指定的HTML Tag元素进行解析，并将结果储存在当前实例的md_list、video_list、img_list中。

        :param element: 要解析的 HTML Tag 元素。
        """
        if not element:
            return
        self.init_list()
        self._traverse(element)

    def _traverse(self, element: Tag):
        """
        递归遍历HTML元素树，将文本、图片、视频信息添加到实例的属性中。

        :param element: 要遍历的 HTML Tag 元素。
        """
        if element is None:
            return

        if isinstance(element, NavigableString):
            self._handle_text(element)
        elif isinstance(element, Tag):
            # 处理图片
            if element.name == "img":
                img_name, img_url = self.get_image_info(element)
                if img_name and img_url:
                    self._handle_image(img_name, img_url)

            # 处理视频
            classes = element.get("class", [])
            if "dplayer" in classes:
                video_name, video_url = self.get_video_info(element)
                if video_name and video_url:
                    self._handle_video(video_name, video_url)

            # 递归子元素
            for child in element.children:
                self._traverse(child)

    def _handle_text(self, text_node: NavigableString):
        """
        处理文本节点，将非空文本添加到 markdown 列表中。

        :param text_node: HTML 文本节点。
        """
        text = text_node.strip()
        if not text:
            return
        self.md_list.append(text)

    def _handle_image(self, img_name: str, img_url: str):
        """
        处理图片，将图片信息添加到 markdown 列表和图片列表中。

        :param img_name: 图片名称。
        :param img_url: 图片 URL 地址。
        """
        self.md_list.append(f"![{img_url}]({img_name})")
        self.img_list.append((img_name, img_url))

    def _handle_video(self, video_name: str, video_url: str):
        """
        处理视频，将视频信息添加到 markdown 列表和视频列表中。

        :param video_name: 视频名称。
        :param video_url: 视频 URL 地址。
        """
        self.md_list.append(
            f'<video controls src="{video_name}" width="480" height="320">{video_url}</video>'
        )
        self.video_list.append((video_name, video_url))

    def get_image_info(self, img_tag: Tag) -> tuple[str, str]:
        """
        获取图片相关信息的方法，可以在子类中重写。

        :param img_tag: 包含图片信息的 HTML Tag 元素。
        :return: (图片名称, 图片URL) 元组。
        """
        return "unknown_img_name", "unknown_img_url"

    def get_video_info(self, video_tag: Tag) -> tuple[str, str]:
        """
        获取视频相关信息的方法，可以在子类中重写。

        :param video_tag: 包含视频信息的 HTML Tag 元素。
        :return: (视频名称, 视频URL) 元组。
        """
        return "unknown_video_name", "unknown_video_url"
