import pytest
import logging
import os, random
from celestialvault.tools.TextTools import (
    pro_slash, str_to_dict, language_fingerprint, 
    calculate_valid_chinese_text, calculate_valid_text, 
    format_table, string_split,
    rs_encode, rs_decode,
    pad_bytes, unpad_bytes,
)
from celestialvault.tools.NumberUtils import (
    choose_square_container,
    redundancy_from_container,
)

def test_pro_slash():
    string_a = '(W//R\S/H\\U)'
    string_b = "https:\/\/m10.music.126.net\/20211221203525\/cb633fbb6fd0423417ef492e2225ba45\/ymusic\/7dbe\/b17e\/1937\/9982bb924f5c3adc6f85679fcf221418.mp3"
    string_c = r"this\\is\a\\test\\\\string"
    slash_a = pro_slash(string_a)
    slash_b = pro_slash(string_b)
    slash_c = pro_slash(string_c)

    logging.info(f"{'Test input0':<16}: {string_a}")
    logging.info(f"{'Expected output0':<16}: (W//R\S/H\\U)")
    logging.info(f"{'Actual output0':<16}: {slash_a}")

    logging.info(f"{'Test input1':<16}: {string_b}")
    logging.info(f"{'Expected output1':<16}: https://m10.music.126.net/20211221203525/cb633fbb6fd0423417ef492e2225ba45/ymusic/7dbe/b17e/1937/9982bb924f5c3adc6f85679fcf221418.mp3")
    logging.info(f"{'Actual output1':<16}: {slash_b}")

    logging.info(f"{'Test input2':<16}: {string_c}")
    logging.info(f"{'Expected output2':<16}: this\\is\\a\\test\\\\string")
    logging.info(f"{'Actual output2':<16}: {slash_c}")

def test_str_to_dict():
    test_str_0 = "key1:value1\nkey2:value2\n\n:key3:value3"
    test_str_1 = "key1=value1; key2=value2; key3= ; key4=value4"

    result_dict_0 = str_to_dict(test_str_0)
    logging.info(f"{'Test 0 input':<15}:\n{test_str_0}")
    logging.info(f"{'Expected output':<15}: {{'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}}")
    logging.info(f"{'Actual output':<15}: {result_dict_0}\n")
    
    result_dict_1 = str_to_dict(test_str_1, line_delimiter=';', key_value_delimiter='=')
    logging.info(f"{'Test 1 input':<15}:\n{test_str_1}")
    logging.info(f"{'Expected output':<15}: {{'key1': 'value1', 'key2': 'value2', 'key3': '', 'key4': 'value4'}}")
    logging.info(f"{'Actual output':<15}: {result_dict_1}")

def _test_language_fingerprint():
    with open(r'G:\Project\test\寻找走丢的舰娘(34653).txt', 'r', encoding = 'utf-8') as f:
        text = f.read()
    fingerprint = language_fingerprint(text)
    logging.info(f"{'fingerprint':<15}:\n{fingerprint}")

def test_calculate_valid_text():
    text = """
    ★ 《亚洲周刊》2020年度十大小说
    ★ 豆瓣读书2020年度中国文学（小说类）Top1
    ★ 2021年宝珀理想国文学奖首奖作品
    ★ 2020年单向街书店文学奖年度作品
    ★ 首届pageone文学赏 首赏
    仿佛鸟栖树，鱼潜渊，一切稳妥又安宁，夜晚这才真正地降临。

    《夜晚的潜水艇》 是陈春成的首部小说集。九个故事，游走于旧山河与未知宇宙间，以瑰奇飘扬的想象、温厚清幽的笔法，在现实与幻境间辟开秘密的通道：海底漫游的少年、深山遗落的古碑、弥散入万物的字句、云彩修剪站、铸剑与酿酒、铁幕下的萨克斯、蓝鲸内的演奏厅…… 关于藏匿与寻找、追捕与逃遁，种种无常中的一点确凿，烈日与深渊间的一小片清凉。陈春成的小说世界，是可供藏身的洞窟，悬浮于纸上的宫殿，航向往昔的潜艇。

    【推荐语】

    我非常喜欢《夜晚的潜水艇》，陈春成给了我一个惊喜。在NBA，他们对那些充满潜力的年轻球员有一个形容，天空才是他的极限，这话也可以用在陈春成的身上。他比较厉害的一点是，既飘逸又扎实，想象力非常丰富，写现实的部分又很扎实，转换和衔接都做得非常好，很老练的作品。我觉得他是一个前程无量的作家。

    ——余华（作家）

    读陈春成的小说，能感受到作者在背后把问题全部想得清清楚楚，所以小说才会看起来流畅而有趣。他的语言锤炼已经炉火纯青，不是池中之物。这注定是一位了不起的小说家。

    ——阿乙（作家）

    陈春成是一座傍晚的园林，每句话都值得细看，每句话都即将错过。我相信这个传说：“我是梦中传彩笔，欲书花叶寄朝云”，有一种古老的文字秩序在暗中流传，到他出现时，我才能指给你：快看，就是这个样子。

    ——贾行家（作家）

    初读《裁云记》《竹峰寺》时，只觉得文章虽短但气象非凡，作者笔下处处是奇光异彩。读罢全书，才知道那也只是修竹茂林中隐隐露出的一角飞檐。九篇小说，如九座幽深的宫殿，殿门虚掩，静谧无人，但你侧身进去，缓缓移步，很快就能看到那些足以使人目不暇给的别致格局、精巧构件、璀璨细节。感谢作者以一己之力构筑这些美妙而深邃的宫殿，让我们得以窥见其中那无数动人心魄的奇丽景象。

    ——东东枪（作家）

    陈春成的每一篇文字，甚至每一页每一段，都有一种奇异的空灵感，把人拉拽进一种亦真亦幻的状态里。细致入微的文字后隐藏着很久远的情感，调动出我的记忆与触觉。每一篇看完，总是唏嘘半日。

    ——陆庆屹（导演）

    陈春成的小说很惊艳，语言极好，且有一种整体性、批判性而又狂欢性的想象力。最厉害的是，他能使最荒诞不经的叙述毫不费力地变得可信，这个本事很难。他对自己的生活有尖锐的看法，表达十分华美飞翔。

    ——李静（评论家）

    陈春成是90后作家中非常有个人特色的一位。汪曾祺式的古典故园与博尔赫斯式的现代迷宫拆散重组，变成了他笔下的废园。但只要读完他的作品，又会发现他远比此丰富。他直接越过了写自我的阶段，一出场就以万物为题，在常识之上，就势思接万里。每一篇小说都不尽相同，又在主题上持续变奏。在一个以糙笔写浮心的时代，他反其道而行之，躲在“深山电报站”，以万物为学问，没有功利心地研究又把玩。他笔触老练，用字沉静，想象又纵肆酣快，间杂萌态。浑然一个专心研学又玩心隆盛的老顽童。

    ——古肩（《中华文学选刊》编辑）

    《夜晚的潜水艇》独辟蹊径，把知识与生活、感性与理性、想象力和准确性结合为一体，具有通透缠绵的气质和强烈的幻想性。小说以一种典雅、迷人的语言为我们展现了当代小说的新路径。

    ——第四届宝珀理想国文学奖 授奖词"""

    valid_chinese_rate = calculate_valid_chinese_text(text)
    valid_rate = calculate_valid_text(text)

    # logging.info(f"{'Test input':<15}:\n{text}")
    logging.info(f"{'Valid chinese rate':<18}: {valid_chinese_rate}")
    logging.info(f"{'Valid rate':<18}: {valid_rate}")

def test_format_table():
    data = [
        ["Alice", 24, "Engineer"],
        ["Bob", 27],
        ["Charlie", 22, "设计师", "Berlin"],
        ["大卫", 30, "Doctor", "New York", "USA"]
    ]

    column_names = ["Name", "Age", "Job", "City"]
    row_names = ["A", "B", "C"]

    table_text = format_table(data, column_names, row_names, index_header = r"行数\属性", align="center")
    logging.info(f"{'Test data':<11}: {data}")
    logging.info(f"{'Test output':<11}:\n{table_text}")

def test_string_split():
    input_string = ('dfg4354df6g654dfg585d8gd87fg56df132e1rg8df87f56g4d3s1dg45431', '3')
    result = string_split(*input_string)

    logging.info(result)

def test_rs_encode_decode():
    # 1. 造一段随机数据
    data = os.urandom(1024)  # 1KB 随机数据
    nsym = 600               # 故意设很大，触发分块逻辑

    # 2. 编码
    encoded = rs_encode(data, nsym)
    logging.info(f"原始长度:{len(data)}, 编码后长度:{len(encoded)}")
    assert len(encoded) == len(data) + nsym
    logging.info("✅ 编码成功，数据一致！")

    # 3. 人为损坏一些字节
    encoded_list = bytearray(encoded)
    for _ in range(100):  # 随机破坏100个字节
        pos = random.randint(0, len(encoded_list) - 1)
        encoded_list[pos] ^= 0xFF
    corrupted = bytes(encoded_list)

    # 4. 解码
    decoded = rs_decode(corrupted, nsym)

    # 5. 验证
    assert decoded == data
    logging.info("✅ 解码成功，数据一致！")

def test_rs_workflow():
    raw = b"Hello, Reed-Solomon with container!"
    logging.info("原始数据长度:", len(raw))

    # 1. 选择容器
    side_length, max_payload, nsym = choose_square_container(len(raw), 0.7)
    logging.info("容器大小:", side_length**2, "最大有效载荷:", max_payload, "冗余长度:", nsym)

    # 2. 补位到容器
    padded = pad_bytes(raw, max_payload)
    logging.info("总长度:", len(padded))

    # 3. RS 编码
    encoded = rs_encode(padded, nsym)
    logging.info("编码后:", encoded)
    logging.info("编码后长度:", len(encoded))

    # 4. RS 解码
    decode_nsym = redundancy_from_container(side_length**2, 0.7)
    decoded = rs_decode(encoded, decode_nsym)
    logging.info("解码后:", decoded)

    # 5. 去除补位
    unpadded = unpad_bytes(decoded)
    logging.info("去补位后:", unpadded)

    if unpadded == raw:
        logging.info("数据完整，无错误")