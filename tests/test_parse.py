import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest, logging
from bs4 import BeautifulSoup
from instances.inst_parse import HTMLContentParser

def test_html_content_parser():
    # 示例HTML片段，包含文本、图片和视频配置
    html_content = """
    <div>
        <p>这是一些文本内容。</p>
        <img title="示例图片.jpg" data-xkrkllgl="http://example.com/image.jpg" />
        <div class="dplayer" data-config='{"url":"http://example.com/video123.m3u8"}'></div>
        <div>
            <p>另一段文本</p>
        </div>
    </div>
    """

    # 解析HTML
    soup = BeautifulSoup(html_content, "html.parser")

    # 创建解析器实例并进行解析
    parser = HTMLContentParser()
    parser.parse(soup)

    # 测试结果输出(实际生产中可使用assert进行自动化测试)
    logging.info(f"Markdown List: {parser.md_list}")
    logging.info(f"Video List: {parser.video_list}")
    logging.info(f"Image List: {parser.img_list}")

