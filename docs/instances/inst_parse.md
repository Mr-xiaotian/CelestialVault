# `celestialvault.instances.inst_parse`

## 源文件 - `src/celestialvault/instances/inst_parse.py`

## 模块说明

提供 HTML 内容解析类 `HTMLContentParser`，用于递归遍历 HTML 元素树，将文本、图片和视频信息提取为 markdown 列表、视频列表和图片列表。

## 导入依赖

- `bs4.NavigableString` - BeautifulSoup 文本节点
- `bs4.Tag` - BeautifulSoup 标签节点

## 类

### `HTMLContentParser`

- 继承: 无
- 说明: 解析 HTML 内容，将文本、图片和视频信息提取为 markdown 列表、视频列表和图片列表。子类可重写 `get_image_info` 和 `get_video_info` 方法以自定义信息提取逻辑。

- 构造函数: `__init__(self)` - 无参数。

- 方法:

  #### `init_list(self)`
  - 签名: `init_list(self) -> None`
  - 说明: 初始化 markdown、视频和图片列表，清空上次解析结果。
  - 初始化的属性:
    - `self.md_list` (`list[str]`): markdown 文本列表。
    - `self.video_list` (`list[tuple[str, str]]`): 视频信息列表 `(名称, URL)`。
    - `self.img_list` (`list[tuple[str, str]]`): 图片信息列表 `(名称, URL)`。

  #### `parse(self, element)`
  - 签名: `parse(self, element: Tag) -> None`
  - 说明: 对指定的 HTML Tag 元素进行解析，先调用 `init_list()` 清空上次结果，再递归遍历元素树。
  - 参数:
    - `element` (`Tag`): 要解析的 HTML Tag 元素。

  #### `_traverse(self, element)`
  - 签名: `_traverse(self, element: Tag) -> None`
  - 说明: 递归遍历 HTML 元素树，将文本、图片（`<img>` 标签）、视频（class 含 `"dplayer"` 的元素）信息添加到实例属性中。
  - 参数:
    - `element` (`Tag`): 要遍历的 HTML Tag 元素。

  #### `_handle_text(self, text_node)`
  - 签名: `_handle_text(self, text_node: NavigableString) -> None`
  - 说明: 处理文本节点，将非空文本添加到 `md_list` 中。

  #### `_handle_image(self, img_name, img_url)`
  - 签名: `_handle_image(self, img_name: str, img_url: str) -> None`
  - 说明: 处理图片，将 `![img_url](img_name)` 添加到 `md_list`，将 `(img_name, img_url)` 添加到 `img_list`。

  #### `_handle_video(self, video_name, video_url)`
  - 签名: `_handle_video(self, video_name: str, video_url: str) -> None`
  - 说明: 处理视频，将 HTML video 标签添加到 `md_list`，将 `(video_name, video_url)` 添加到 `video_list`。

  #### `get_image_info(self, img_tag)`
  - 签名: `get_image_info(self, img_tag: Tag) -> tuple[str, str]`
  - 说明: 获取图片相关信息的方法，可以在子类中重写。默认返回 `("unknown_img_name", "unknown_img_url")`。
  - 参数:
    - `img_tag` (`Tag`): 包含图片信息的 HTML Tag 元素。
  - 返回值: `(图片名称, 图片URL)` 元组。

  #### `get_video_info(self, video_tag)`
  - 签名: `get_video_info(self, video_tag: Tag) -> tuple[str, str]`
  - 说明: 获取视频相关信息的方法，可以在子类中重写。默认返回 `("unknown_video_name", "unknown_video_url")`。
  - 参数:
    - `video_tag` (`Tag`): 包含视频信息的 HTML Tag 元素。
  - 返回值: `(视频名称, 视频URL)` 元组。

- 用法示例:

```python
from bs4 import BeautifulSoup, Tag
from celestialvault.instances.inst_parse import HTMLContentParser

html = """
<div>
    <p>这是一段文本</p>
    <img src="https://example.com/img.png" alt="示例图片">
    <div class="dplayer" data-url="https://example.com/video.mp4">视频</div>
</div>
"""

# 自定义子类以提取真实的图片和视频信息
class MyParser(HTMLContentParser):
    def get_image_info(self, img_tag: Tag) -> tuple[str, str]:
        return img_tag.get("alt", ""), img_tag.get("src", "")

    def get_video_info(self, video_tag: Tag) -> tuple[str, str]:
        return "video", video_tag.get("data-url", "")

soup = BeautifulSoup(html, "html.parser")
parser = MyParser()
parser.parse(soup.find("div"))

print(parser.md_list)    # 提取的 markdown 文本列表
print(parser.img_list)   # 提取的图片列表
print(parser.video_list) # 提取的视频列表
```

- 关联: 可配合 `inst_fetch.Fetcher` 获取 HTML 后进行解析；可配合 `inst_save.Saver` 保存提取的内容。
