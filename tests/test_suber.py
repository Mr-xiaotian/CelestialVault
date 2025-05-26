import pytest, logging
from time import time
from celestialvault.instances.inst_sub import Suber

def test_suber():
    test_text_0 = '''# 测试文本开始
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

    test_text_1 = """
    作者：张三
    字数：12345

    <p>这是一个HTML段落。<br>有换行<br></p>
    <code>print("Hello World")</code>

    ◆测试文本◆
    第1章 这是第一章
    【摘要】这是摘要部分。

    有些换行符
    不在需要的地方
    会被合并。

     　\t\r\f\v\x1e 空白和特殊符号会被删除。

    """

    suber = Suber()
    sub_text_0 = suber.clear_text(test_text_0)
    sub_text_1 = suber.clear_text(test_text_1)

    logging.info(f"Sun Text 0:\n{sub_text_0}")
    # logging.info(f"Sun Text 1:\n{sub_text_1}")
    # print(list(sub_text_1))

if __name__ == '__main__':
    test_suber()

