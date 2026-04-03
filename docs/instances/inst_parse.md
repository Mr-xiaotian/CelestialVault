# instances/inst_parse.py

## 源文件
- `src/celestialvault/instances/inst_parse.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- `from bs4 import NavigableString, Tag`

## 模块常量
- 无

## 顶层函数
- 无

## 类
### `HTMLContentParser`
- 继承: `object`
- 说明: 一个用于解析HTML内容的类，将文本、图片和视频信息提取为markdown列表、视频列表和图片列表。
- 方法:
  - `def __init__(self)`
  - `def init_list(self)`
  - `def parse(self, element: Tag)`
  - `def _traverse(self, element: Tag)`
  - `def _handle_text(self, text_node: NavigableString)`
  - `def _handle_image(self, img_name: str, img_url: str)`
  - `def _handle_video(self, video_name: str, video_url: str)`
  - `def get_image_info(self, img_tag: Tag) -> tuple[str, str]`
  - `def get_video_info(self, video_tag: Tag) -> tuple[str, str]`
