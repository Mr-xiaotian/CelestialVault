# pyright: reportGeneralTypeIssues=false

import base64
import re
import math
import string
import zlib
import struct
import reedsolo
from itertools import zip_longest
from pathlib import Path
from pprint import pprint
from typing import Dict, List, Tuple, Union

import charset_normalizer
# import jieba
# from jieba import analyse
from tqdm import tqdm
from wcwidth import wcswidth


def pro_slash(input_str: str) -> str:
    """
    移除字符串中多余的转义符。

    :param input_str (str): 要处理的字符串。
    :return str: 移除多余转义符后的字符串。

    old:
    re_strs = repr(strs)
    while '\\\\' in re_strs:
        re_strs = re_strs.replace('\\\\', '\\')
    if re_strs[-2] == '\\':
        print(re_strs[1:-2])
        re_strs = re_strs[1:-2]

    try:
        pro_strs = eval(re_strs)
        return pro_strs
    except Exception as e:
        print(e)
        return strs
    """
    if not input_str:
        return input_str

    # 替换多余的转义符
    result_str = input_str.replace("\\\\", "\\")

    # 替换其他转义符
    result_str = result_str.replace(r"\/", "/")

    return result_str


def str_to_dict(
    string: str, line_delimiter: str = "\n", key_value_delimiter: str = ":"
) -> Dict[str, str]:
    """
    将字符串转化为字典，每行格式为 `key:value`，以指定的分隔符分隔行。

    :param string: 包含键值对的字符串，每行一个键值对。
    :param line_delimiter: 用于分隔行的字符串，默认是换行符。
    :param key_value_delimiter: 用于分隔键和值的字符，默认是冒号。
    :return: 转化后的字典。
    """
    # 去除空行并分割成列表
    lines = [line for line in string.split(line_delimiter) if line.strip()]

    parsed_dict = {}

    for line in lines:
        # 去掉行首的冒号
        if line.startswith(key_value_delimiter):
            line = line[1:]

        # 分割键和值
        key, _, value = line.partition(key_value_delimiter)
        parsed_dict[key.strip()] = value.strip()

    return parsed_dict


def str_removes(strs: str, _remove: str) -> str:
    """
    从字符串中移除指定的子串。

    :param strs (str): 原始字符串。
    :param _remove (str): 需要从原始字符串中移除的子串。
    :return str: 移除指定子串后的新字符串。
    """
    return strs.replace(_remove, "")


def str_replaces(strs: str, replace_list: list[Tuple[str, str]]) -> str:
    """
    从字符串中替换指定的子串。

    :param strs (str): 原始字符串。
    :param replace_list (list[Tuple[str, str]]): 需要替换的子串列表。
    :return str: 替换指定子串后的新字符串。
    """
    for r in replace_list:
        strs = strs.replace(r[0], r[1])
    return strs


def iprint(obj: Union[List, Dict], start="", end=""):
    """
    根据对象的大小选择打印方式。
    如果对象的长度小于16，那么就打印整个对象，否则只打印前10个和后5个元素。

    :param obj (Union[List, Dict]): 需要打印的对象，可以是列表或字典。
    """
    print(start, end="")
    length = len(obj)
    if length < 16:
        pprint(obj)
    else:
        pprint(obj[:10])
        print(f"(此处省略{length-15}项)")
        pprint(obj[-5:])
    print(end, end="")


def string_split(string: str, split_str: str = "\n") -> list[str]:
    """
    将字符串按指定分隔符分割，返回一个列表，每个元素是分割后非空的子字符串。
    """
    return [s for s in string.split(split_str) if s]


def language_fingerprint(text: str) -> dict:
    """
    根据文本生成语言指纹字典。
    """
    return
    # 将文本分词
    words = list(jieba.cut(text))

    # 计算单词和字符的数量
    num_words = len(words)
    num_chars = len(text)

    # 计算单词长度分布
    word_lengths = [len(w) for w in words]
    avg_word_length = sum(word_lengths) / num_words
    max_word_length = max(word_lengths)

    # 计算停用词比例
    stopwords = set(["的", "了", "是", "在", "我", "有", "和", "就", "不"])
    num_stopwords = len([w for w in words if w in stopwords])
    stopwords_ratio = num_stopwords / num_words

    # 计算词频分布
    freq_dist = dict(analyse.extract_tags(text, topK=10, withWeight=True))
    top_10_words = {word: freq_dist[word] for word in list(freq_dist.keys())}

    # 构建语言指纹字典
    fingerprint = {
        "num_words": num_words,
        "num_chars": num_chars,
        "avg_word_length": avg_word_length,
        "max_word_length": max_word_length,
        "stopwords_ratio": stopwords_ratio,
        "top_10_words": top_10_words,
    }

    return fingerprint


def calculate_valid_chinese_text(text: str):
    """
    计算文本中中文字符的比例。
    """
    # 定义一个正则表达式来匹配中文字符
    chinese_char_pattern = re.compile(
        r"[\u4e00-\u9fff" r"。，、？！《》“”‘’：（）【】" r"0-9a-zA-Z]"
    )

    # 计算中文字符的数量
    chinese_char_count = len(chinese_char_pattern.findall(text))

    # 计算文本中中文字符的比例
    return chinese_char_count / len(text)


def calculate_valid_text(text: str):
    """
    计算文本中有效字符的比例。
    """
    # 定义一个正则表达式来匹配所有常见语言字符和标点符号
    valid_char_pattern = re.compile(
        r"[\u4e00-\u9fff" r"。，、？！《》“”‘’：（）【】" f"{string.printable}]"
    )

    # 计算有效字符的数量
    valid_char_count = len(valid_char_pattern.findall(text))

    # 计算文本中有效字符的比例
    return valid_char_count / len(text)


def is_valid_chinese_text(text: str, threshold: int = 0.8):
    """
    判断文本是否为有效文本，即文本中有效字符的比例是否大于阈值。
    """
    return calculate_valid_chinese_text(text) > threshold


def is_valid_text(text: str, threshold: int = 0.8):
    """
    判断文本是否为有效文本，即文本中有效字符的比例是否大于阈值。
    """
    return calculate_valid_text(text) > threshold


def crc_encode_text(actual_text: str) -> str:
    """
    在文本开头添加CRC32校验和。
    """
    # 计算CRC32校验和
    crc = zlib.crc32(actual_text.encode("utf-8"))
    crc_bytes = crc.to_bytes(4, "big")  # 4字节的CRC32

    # 将校验和附加到文本开头
    crc_text = crc_bytes.decode("latin1") + actual_text

    return crc_text


def crc_decode_text(crc_text: str) -> str:
    """
    从文本中提取CRC32校验和并验证。
    """
    # 提取校验和和实际文本
    crc_received = int.from_bytes(crc_text[:4].encode("latin1"), "big")
    actual_text = crc_text[4:]

    # 计算校验和并验证
    crc_calculated = zlib.crc32(actual_text.encode("utf-8"))
    if crc_received != crc_calculated:
        raise ValueError("校验和验证失败！")

    return actual_text


def crc_encode_bytes(data: bytes) -> bytes:
    """
    在字节串前附加 4 字节 big-endian CRC32。
    """
    crc = zlib.crc32(data)
    crc_bytes = crc.to_bytes(4, "big")
    return crc_bytes + data


def crc_decode_bytes(crc_data: bytes) -> bytes:
    """
    分离并验证前置 CRC32，返回原始字节。
    """
    if len(crc_data) < 4:
        raise ValueError("数据长度不足，没有包含 CRC32。")

    crc_received = int.from_bytes(crc_data[:4], "big")
    actual_data = crc_data[4:]

    crc_calculated = zlib.crc32(actual_data)
    if crc_received != crc_calculated:
        raise ValueError("CRC32 校验失败。")

    return actual_data


def add_length_header_to_text(text: str) -> str:
    """
    将文本前加 4 字节长度头（注意：长度为“UTF-8字节长度”），并返回 str。
    头部使用 latin1 解码，保证无损保留二进制。
    """
    raw = text.encode("utf-8")
    length_prefix = struct.pack(">I", len(raw))  # 必须是 UTF-8 字节长度
    return length_prefix.decode("latin1") + text


def restore_text_from_length_header(data: str) -> str:
    """
    从带长度头的文本恢复原始 UTF-8 文本。
    """
    data_bytes = data.encode("latin1")  # 先无损转回 bytes

    if len(data_bytes) < 4:
        raise ValueError("数据不足 4 字节，缺少长度头")

    true_len = struct.unpack(">I", data_bytes[:4])[0]

    if len(data_bytes) < 4 + true_len:
        raise ValueError("数据不完整，无法按长度头读取")

    raw = data_bytes[4 : 4 + true_len]
    return raw.decode("utf-8")


def add_length_header_to_bytes(raw: bytes) -> bytes:
    """
    为 bytes 加上 4 字节长度头（big-endian）。
    返回值为： [4字节长度] + [原始bytes]
    """
    length_prefix = struct.pack(">I", len(raw))
    return length_prefix + raw


def restore_bytes_from_length_header(data: bytes) -> bytes:
    """
    从带长度头的字节串中恢复原始 bytes。
    """
    if len(data) < 4:
        raise ValueError("数据不足 4 字节，缺少长度头")

    true_len = struct.unpack(">I", data[:4])[0]

    if len(data) < 4 + true_len:
        raise ValueError("数据不完整，无法按长度头读取")

    return data[4 : 4 + true_len]


def encode_bytes_to_base64(data: bytes) -> str:
    """
    将字节串编码为 Base64 文本，并在前方加上 4 字节长度头（真实二进制长度）。
    返回值为 UTF-8 文本。
    """
    length_prefix = struct.pack(">I", len(data))  # 4 字节长度头
    payload = length_prefix + data
    return base64.b64encode(payload).decode("utf-8")


def decode_bytes_from_base64(text: str) -> bytes:
    """
    从 Base64 文本解码为字节串，解析前 4 字节长度头，截取真实数据。
    """
    raw = base64.b64decode(text.encode("utf-8"))

    if len(raw) < 4:
        raise ValueError("数据不足 4 字节，缺少长度头")

    true_len = struct.unpack(">I", raw[:4])[0]

    if len(raw) < 4 + true_len:
        raise ValueError("数据不完整或损坏")

    return raw[4 : 4 + true_len]


def compress_text_to_bytes(text: str) -> bytes:
    """
    压缩文本并返回字节流，前 4 字节存储真实压缩长度。
    """
    compressed_data = zlib.compress(text.encode("utf-8"))
    length_prefix = struct.pack(">I", len(compressed_data))  # 4 字节长度头
    return length_prefix + compressed_data


def decompress_text_from_bytes(compressed_data: bytes) -> str:
    """
    从字节流中解压缩文本，利用前 4 字节长度头截取真实压缩数据。
    """
    if len(compressed_data) < 4:
        raise ValueError("压缩数据过短，缺少长度头")

    true_len = struct.unpack(">I", compressed_data[:4])[0]
    if len(compressed_data) < 4 + true_len:
        raise ValueError("数据不完整或损坏，无法解压")

    compressed_part = compressed_data[4 : 4 + true_len]

    return zlib.decompress(compressed_part).decode("utf-8")


def rs_encode(data: bytes, nsym: int) -> bytes:
    """
    把 data 分成 n 份，每份添加 nsym/n 个冗余，
    保证 (len(data)/n + nsym/n) < 255。
    """
    if nsym < 1:
        raise ValueError("nsym 必须 >= 1")

    # 计算最小分块数 n
    n = 1
    while True:
        data_per_block = math.ceil(len(data) / n)
        ecc_per_block = math.ceil(nsym / n)
        if data_per_block + ecc_per_block < 255:
            break
        n += 1

    # 平均分配数据和冗余
    q_dat, r_dat = divmod(len(data), n)
    q_sym, r_sym = divmod(nsym, n)

    encoded_blocks = []
    start = 0
    for i in range(n):
        block_size = q_dat + (1 if i < r_dat else 0)
        nsym_block = q_sym + (1 if i < r_sym else 0)
        chunk = data[start : start + block_size]
        start += block_size

        rs = reedsolo.RSCodec(nsym_block)
        encoded_blocks.append(rs.encode(chunk))

    return b"".join(encoded_blocks)


def rs_decode(encoded: bytes, nsym: int) -> bytes:
    """
    解码由 rs_encode 生成的数据。
    输入: encoded (编码数据), nsym (总冗余字节数)
    输出: 原始 data
    """
    if nsym < 1:
        raise ValueError("nsym 必须 >= 1")

    total_len = len(encoded)
    data_len = total_len - nsym
    if data_len < 0:
        raise ValueError("encoded 长度比 nsym 还小，数据非法")

    # 计算最小分块数 n
    n = 1
    while True:
        data_per_block = math.ceil(data_len / n)
        ecc_per_block = math.ceil(nsym / n)
        if data_per_block + ecc_per_block < 255:
            break
        n += 1

    # 平均分配数据和冗余
    q_dat, r_dat = divmod(data_len, n)
    q_sym, r_sym = divmod(nsym, n)

    decoded_chunks = []
    start = 0
    for i in range(n):
        block_size = q_dat + (1 if i < r_dat else 0)
        nsym_block = q_sym + (1 if i < r_sym else 0)
        encoded_block_size = block_size + nsym_block
        block = encoded[start : start + encoded_block_size]
        start += encoded_block_size

        rs = reedsolo.RSCodec(nsym_block)
        decoded, _, _ = rs.decode(block)
        decoded_chunks.append(bytes(decoded))

    return b"".join(decoded_chunks)


def pad_bytes(data: bytes, target_len: int) -> bytes:
    """
    在 data 前加 4 字节长度头，并用 0xEC, 0x11 循环补齐到 target_len
    """
    header = len(data).to_bytes(4, "big")
    data_with_header = header + data

    if target_len < len(data_with_header):
        raise ValueError("target_len 不能小于 原始长度+4")

    pad_len = target_len - len(data_with_header)
    pad_pattern = (0xEC, 0x11)
    padding = bytes(pad_pattern[i % 2] for i in range(pad_len))
    return data_with_header + padding


def unpad_bytes(data: bytes) -> bytes:
    """
    去掉补位并根据头部恢复原始数据
    """
    if len(data) < 4:
        raise ValueError("数据太短，缺少长度头")

    orig_len = int.from_bytes(data[:4], "big")
    raw = data[4 : 4 + orig_len]

    if len(raw) != orig_len:
        raise ValueError("数据长度不匹配，可能损坏")

    return raw


def pad_to_align(data: bytes, align: int) -> bytes:
    """
    把字节流补齐到 align 的倍数。
    """
    if align <= 1:
        return data
    pad = (align - (len(data) % align)) % align
    pad_pattern = (0xEC, 0x11)
    padding = bytes(pad_pattern[i % 2] for i in range(pad))

    return data + padding


def compress_to_base64(text: str) -> str:
    """
    压缩文本并转换为Base64编码, 长度为4的倍数。

    :param text: 要压缩并转换为 Base64 的文本
    :return: 压缩后并转换为 Base64 的字符串
    """
    # 每三字节(3×8-bit)映射到四位Base64字符(4×6-bit)进制字符，所以需要填充以避免出现 "="
    compressed_data = compress_text_to_bytes(text)
    pad_data = pad_to_align(compressed_data, 3)

    # 转为Base64码时由于以字节码存储, 体积会变为bytes的4/3
    base64_text = base64.b64encode(pad_data).decode("utf-8")

    return base64_text


def decode_from_base64(base64_text: str) -> str:
    """
    从Base64编码中解码并解压缩文本。
    """
    # Decode the Base64 text to get the compressed data
    compressed_data = base64.b64decode(base64_text.encode("utf-8"))

    # Decompress the data to get the original text
    original_text = decompress_text_from_bytes(compressed_data)

    return original_text


def safe_open_txt(file_path: str | Path) -> str:
    """
    尝试使用多种编码打开文本文件，并返回解码后的文本。

    :param file_path: 文件路径，可以是字符串或 Path 对象
    :return: 解码后的文本内容
    :raises ValueError: 如果无法用任何编码解码文件，抛出异常
    """
    # 读取整个文件以进行编码检测
    file_path = Path(file_path)
    raw = file_path.read_bytes()

    # 使用 charset-normalizer 检测文件的最佳编码
    results = charset_normalizer.from_bytes(raw)
    encoding_list = [results.best().encoding] if results else []

    # 添加其他常见编码供尝试：GB18030, Big5, UTF-8, UTF-16 和 Latin-1
    encoding_list += ["gb18030", "big5", "utf-8", "utf-16", "latin-1"]

    book_text = None
    for encoding in encoding_list:
        try:
            # 尝试使用当前编码解码文本, 并验证解码后的文本是否合理
            decoded_text = file_path.read_text(encoding, errors="replace")

            if is_valid_text(decoded_text):
                book_text = decoded_text
                break
        except (UnicodeDecodeError, TypeError):
            continue  # 如果解码失败，尝试下一个编码

    if book_text is None:
        raise ValueError("无法使用检测到的编码解码文件")

    return book_text


def combine_txt_files(source_dir: str | Path, target_file: str | Path):
    """
    将指定文件夹内的所有txt文件按文件名中的数字排序，合并为一个新的txt文件。
    合并时每个文件的内容前面加入该文件的名字，合并文件名为文件夹名。

    :param source_dir: 包含txt文件的文件夹路径。
    :param target_file: 合并后的txt文件路径。
    """

    def extract_number(file_name: Path) -> int:
        """
        从文件名中提取数字，用于排序。
        """
        matches = re.findall(r"\d+", file_name.name)
        return int("".join(matches)) if matches else float("inf")

    # 转换路径为 Path 对象
    source_dir = Path(source_dir)

    if not source_dir.is_dir():
        raise ValueError(f"The provided path {source_dir} is not a directory.")

    # 获取所有txt文件路径，并按文件名中的数字排序
    txt_files = sorted(source_dir.glob("*.txt"), key=extract_number)

    if not txt_files:
        raise ValueError(f"No txt files found in {source_dir}.")

    # 合并文件
    with open(target_file, "w", encoding="utf-8") as outfile:
        for txt_file in tqdm(txt_files):
            with open(txt_file, "r", encoding="utf-8") as infile:
                content = infile.read()
                # 写入文件名和内容
                outfile.write(f"== {txt_file.name} ==\n\n")
                outfile.write(content + "\n\n")


def character_ratio(target_str: str) -> Dict[str, float]:
    """
    统计字符串中各个字符的出现比率

    :param target_str: 目标字符串
    :return: 各个字符及其出现比率的字典
    """
    total_length = len(target_str)
    frequency = {}

    for char in target_str:
        frequency[char] = frequency.get(char, 0) + 1

    # 将频率转换为比率
    ratio = {char: count / total_length for char, count in frequency.items()}

    return ratio


def get_lcs(str1: str, str2: str) -> List[str]:
    """
    找出两个字符串的最大相似部分。
    返回一个包含最大相似部分的字符串，如 "1-234-6"。
    """

    def update_common(common_parts: list, current_part):
        if current_part:
            common_parts.append("".join(reversed(current_part)))
        return common_parts, []  # 重置 current_part 为一个空列表

    # 获取两个字符串的长度
    len1, len2 = len(str1), len(str2)

    # 创建一个二维数组 dp，用于存储最长公共子序列的长度
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]

    # 填充 DP 表，找出最长公共子序列长度
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if str1[i - 1] == str2[j - 1]:  # 如果两个字符串当前字符相等
                dp[i][j] = dp[i - 1][j - 1] + 1  # 当前格子的值为左上格子值加 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])  # 否则为上方或左方的较大值

    # 从右下角开始回溯，寻找最长公共子序列的字符
    i, j = len1, len2
    common_parts = []  # 用于存储找到的相似部分
    current_part = []  # 存储当前连续相似的字符部分

    # 回溯寻找最长公共子序列，并分段记录
    while i > 0 and j > 0:
        if str1[i - 1] == str2[j - 1]:  # 如果当前字符相同
            current_part.append(str1[i - 1])  # 将字符加入当前部分

            if i == 1 or j == 1:
                common_parts, current_part = update_common(common_parts, current_part)
                common_parts.append("") if i != j else None

            i -= 1  # 移动到左上格子
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1] or (
            dp[i - 1][j] == dp[i][j - 1] and str1[i - 1] != str1[0]
        ):  # 如果上方格子值较大
            common_parts, current_part = update_common(common_parts, current_part)
            if i == len1 or j == len2 or i == 1:
                if not (common_parts and common_parts[-1] == ""):
                    common_parts.append("")
            i -= 1  # 移动到上方格子
        else:  # 左方格子值较大
            common_parts, current_part = update_common(common_parts, current_part)
            if i == len1 or j == len2 or j == 1:
                if not (common_parts and common_parts[-1] == ""):
                    common_parts.append("")
            j -= 1  # 移动到左方格子

    # 反转整个 common_parts 列表，因为回溯是从字符串的末尾开始
    common_parts.reverse()

    return common_parts


def calculate_similarity(str1: str, str2: str, lcs_parts: list = None) -> float:
    """
    计算两个字符串的相似度。

    :param str1: 第一个字符串
    :param str2: 第二个字符串
    :param lcs_parts: 最长公共子序列的字符部分列表
    :return: 相似度，范围在 0 到 1 之间
    """
    lcs_parts = get_lcs(str1, str2) if not lcs_parts else lcs_parts
    lcs_length = len("".join(lcs_parts))

    max_length = max(len(str1), len(str2))
    similarity = lcs_length / max_length if max_length > 0 else 0

    return similarity


def find_nth_occurrence(target_str: str, similar_str: str, occurrence: int) -> tuple:
    """
    查找目标字符串中指定第n次出现的子字符串位置，并返回其起始和结束索引。

    :param target_str: 目标字符串
    :param similar_str: 待查找的子字符串
    :param occurrence: 查找的第几次出现（从 1 开始计数）
    :return: 子字符串在目标字符串中的起始和结束索引位置，若不存在则返回 (-1, -1)
    """
    start_index = -1  # 初始值，表示尚未找到
    count = 0  # 用于计数找到的相同子字符串的次数

    # 迭代查找目标字符串中的子字符串
    while True:
        start_index = target_str.find(similar_str, start_index + 1)
        if start_index == -1:  # 如果没有找到
            return (-1, -1)

        count += 1  # 增加找到的次数
        if count == occurrence:  # 如果找到了指定次数的匹配
            return (start_index, start_index + len(similar_str))  # 返回坐标


def format_table(
    data: list,
    column_names: list = None,
    row_names: list = None,
    index_header: str = "#",
    fill_value: str = "N/A",
    align: str = "left",
) -> str:
    """
    格式化并打印表格。

    :param data: 表格数据，二维列表，每行代表一行数据
    :param column_names: 自定义的列名，如果为None则使用默认列名（"A", "B", "C", ...）
    :param row_names: 自定义的行号，如果为None则使用默认行号（0, 1, 2, 3...）
    :param index_header: 左上角的名称，默认为 "#"
    :param fill_value: 当数据为空时填充的值
    :param align: 对齐方式，默认为 "left"
    :return: 格式化后的表格字符串
    """

    def _generate_excel_column_names(n: int, start_index: int = 0) -> list[str]:
        """
        生成 Excel 风格列名（A, B, ..., Z, AA, AB, ...）
        支持从指定起始索引开始生成。
        """
        names = []
        for i in range(start_index, start_index + n):
            name = ""
            x = i
            while True:
                name = chr(ord("A") + (x % 26)) + name
                x = x // 26 - 1
                if x < 0:
                    break
            names.append(name)
        return names

    if not data:
        return "表格数据为空！"

    # 计算列数
    max_cols = max(map(len, data))

    # 生成列名
    if column_names is None:
        column_names = _generate_excel_column_names(max_cols)
    elif len(column_names) < max_cols:
        start = len(column_names)  # 从当前列名数量继续命名
        column_names.extend(
            _generate_excel_column_names(max_cols - len(column_names), start)
        )

    # 生成行名
    if row_names is None:
        row_names = range(len(data))
    elif len(row_names) < len(data):
        row_names.extend([i for i in range(len(row_names), len(data))])

    # 添加行号列
    column_names = [index_header] + column_names
    num_columns = len(column_names)

    # 处理行号
    formatted_data = []
    for i, row in enumerate(data):
        row_label = row_names[i] if row_names else i
        formatted_data.append([row_label] + list(row))

    # 统一填充数据行，确保所有行长度一致
    formatted_data = zip_longest(*formatted_data, fillvalue=fill_value)
    formatted_data = list(zip(*formatted_data))  # 转置回来

    # 计算每列的最大宽度
    col_widths = [
        max(wcswidth(str(item)) for item in col)
        for col in zip(column_names, *formatted_data)
    ]

    # 选择对齐方式
    align_funcs = {
        "left": lambda text, width: f"{text:<{width - (wcswidth(text) - len(text))}}",
        "right": lambda text, width: f"{text:>{width - (wcswidth(text) - len(text))}}",
        "center": lambda text, width: f"{text:^{width - (wcswidth(text) - len(text))}}",
    }
    align_func = align_funcs.get(align, align_funcs["left"])  # 默认左对齐

    # 生成表格
    separator = "+" + "+".join(["-" * (width + 2) for width in col_widths]) + "+"
    header = (
        "| "
        + " | ".join(
            [
                f"{align_func(name, col_widths[i])}"
                for i, name in enumerate(column_names)
            ]
        )
        + " |"
    )

    # 生成行
    rows_list = []
    for row in formatted_data:
        rows_list.append(
            "| "
            + " | ".join(
                [
                    f"{align_func(str(row[i]), col_widths[i])}"
                    for i in range(num_columns)
                ]
            )
            + " |"
        )
    rows = "\n".join(rows_list)

    # 拼接表格
    table = f"{separator}\n{header}\n{separator}\n{rows}\n{separator}"
    return table
