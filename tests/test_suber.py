import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest, logging
from time import time
from instances.inst_sub import Suber

def test_suber():
    test_text = '''# 测试文本开始
    这是一段普通的文本。它应该被处理。
    这是第二段文本，包含多个换行符

    第三段文本开始于“第”字

    章节一
    内容开始：

    1. 第一项内容：
    - 详情描述

    ◆ 重点内容：
    注意事项！

    ◆◆ 进一步的说明：
    这部分内容需要特别关注。

    * 列表项：
    - 未正确格式化的列表项。
    - 正确格式化的列表项。

    代码开始：
    int main() {
        printf("Hello, world!\n");
    }
    代码结束。

    # 末尾注释
    # 这应该在新的一行。
    '''

    suber = Suber()
    sub_text = suber.clear_text(test_text)

    logging.info(f"Sun Text: {sub_text}.")



