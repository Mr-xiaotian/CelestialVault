import jieba, re, string, zlib, base64, charset_normalizer
from tqdm import tqdm
from pathlib import Path
from jieba import analyse
from pprint import pprint
from typing import List, Dict, Union, Tuple


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
    result_str = input_str.replace('\\\\', '\\')
    
    # 替换其他转义符
    result_str = result_str.replace(r'\/', '/')
    
    return result_str

def str_to_dict(string: str, line_delimiter: str = "\n", key_value_delimiter: str = ":") -> Dict[str, str]:
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
    return strs.replace(_remove, '')

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

def iprint(obj: Union[List, Dict], start='', end=''):
    """
    根据对象的大小选择打印方式。
    如果对象的长度小于16，那么就打印整个对象，否则只打印前10个和后5个元素。

    :param obj (Union[List, Dict]): 需要打印的对象，可以是列表或字典。
    """
    print(start, end='')
    length = len(obj)
    if length < 16:
        pprint(obj)
    else:
        pprint(obj[:10])
        print(f'(此处省略{length-15}项)')
        pprint(obj[-5:])
    print(end, end='')

def string_split(string: str, split_str: str='\n') -> list[str]:
    """
    将字符串按指定分隔符分割，返回一个列表，每个元素是分割后非空的子字符串。
    """
    return [s for s in string.split(split_str) if s]

def language_fingerprint(text: str) -> dict:
    """
    根据文本生成语言指纹字典。
    """
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
    stopwords = set(['的', '了', '是', '在', '我', '有', '和', '就', '不'])
    num_stopwords = len([w for w in words if w in stopwords])
    stopwords_ratio = num_stopwords / num_words
    
    # 计算词频分布
    freq_dist = dict(analyse.extract_tags(text, topK=10, withWeight=True))
    top_10_words = {word: freq_dist[word] for word in list(freq_dist.keys())}
    
    # 构建语言指纹字典
    fingerprint = {
        'num_words': num_words,
        'num_chars': num_chars,
        'avg_word_length': avg_word_length,
        'max_word_length': max_word_length,
        'stopwords_ratio': stopwords_ratio,
        'top_10_words': top_10_words
    }
    
    return fingerprint

def calculate_valid_chinese_text(text: str):
    """
    计算文本中中文字符的比例。
    """
    # 定义一个正则表达式来匹配中文字符
    chinese_char_pattern = re.compile(r'[\u4e00-\u9fff'
                                      r'。，、？！《》“”‘’：（）【】'
                                      r'0-9a-zA-Z]')
    
    # 计算中文字符的数量
    chinese_char_count = len(chinese_char_pattern.findall(text))
    
    # 计算文本中中文字符的比例
    return chinese_char_count / len(text)

def calculate_valid_text(text: str):
    """
    计算文本中有效字符的比例。
    """
    # 定义一个正则表达式来匹配所有常见语言字符和标点符号
    valid_char_pattern = re.compile(r'[\u4e00-\u9fff'
                                    r'。，、？！《》“”‘’：（）【】'
                                    f'{string.printable}]')
    
    # 计算有效字符的数量
    valid_char_count = len(valid_char_pattern.findall(text))
    
    # 计算文本中有效字符的比例
    return valid_char_count / len(text)

def is_valid_chinese_text(text: str, threshold: int=0.8):
    """
    判断文本是否为有效文本，即文本中有效字符的比例是否大于阈值。
    """
    return calculate_valid_chinese_text(text) > threshold

def is_valid_text(text: str, threshold: int=0.8):
    """
    判断文本是否为有效文本，即文本中有效字符的比例是否大于阈值。
    """
    return calculate_valid_text(text) > threshold

def encode_crc(text: str) -> str:
    """
    在文本开头添加CRC32校验和。
    """
    # 计算CRC32校验和
    crc = zlib.crc32(text.encode('utf-8'))
    crc_bytes = crc.to_bytes(4, 'big')  # 4字节的CRC32

    # 将校验和附加到文本开头
    text = crc_bytes.decode('latin1') + text

    return text
    
def decode_crc(decoded_text: str) -> str:
    """
    从文本中提取CRC32校验和并验证。
    """
    # 提取校验和和实际文本
    crc_received = int.from_bytes(decoded_text[:4].encode('latin1'), 'big')
    actual_text = decoded_text[4:]

    # 计算校验和并验证
    crc_calculated = zlib.crc32(actual_text.encode('utf-8'))
    if crc_received != crc_calculated:
        print("校验和验证失败！")
    
    return actual_text

def compress_text_to_bytes(text: str, padding_length: int = 1) -> bytes:
    """
    压缩文本并返回字节流，确保字节流长度是指定的 padding_length 的倍数。
    
    :param text: 要压缩的文本
    :param padding_length: 填充长度，使压缩结果的字节长度为此参数的倍数
    :return: 压缩后的字节流
    """
    # 使用 zlib 压缩文本，先将文本编码为 UTF-8
    compressed_data = zlib.compress(text.encode('utf-8'))
    
    # 计算需要填充的字节数，以使字节流长度为 padding_length 的倍数
    padding_length = (padding_length - len(compressed_data) % padding_length) % padding_length
    compressed_data += b'\0' * padding_length  # 添加零字节作为填充

    return compressed_data

def decompress_text_from_bytes(compressed_data: bytes) -> str:
    """
    从字节流中解压缩文本。
    """
    original_text = zlib.decompress(compressed_data.rstrip(b'\0')).decode('utf-8')

    return original_text
    
def compress_to_base64(text: str) -> str:
    """
    压缩文本并转换为Base64编码, 长度为4的倍数。

    :param text: 要压缩并转换为 Base64 的文本
    :return: 压缩后并转换为 Base64 的字符串
    """
    # 每三字节(3×8-bit)映射到四位Base64字符(4×6-bit)进制字符，所以需要填充以避免出现 "="
    compressed_data = compress_text_to_bytes(text, 3)
    
    # 转为Base64码时由于以字节码存储, 体积会变为bytes的4/3
    base64_text = base64.b64encode(compressed_data).decode('utf-8')
    
    return base64_text

def decode_from_base64(base64_text: str) -> str:
    """
    从Base64编码中解码并解压缩文本。
    """
    # Decode the Base64 text to get the compressed data
    compressed_data = base64.b64decode(base64_text.encode('utf-8'))
    
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
    encoding_list += ['gb18030', 'big5', 'utf-8', 'utf-16', 'latin-1']

    book_text = None
    for encoding in encoding_list:
        try:
            # 尝试使用当前编码解码文本, 并验证解码后的文本是否合理
            decoded_text = file_path.read_text(encoding, errors='replace')

            if is_valid_text(decoded_text):
                book_text = decoded_text
                break
        except (UnicodeDecodeError, TypeError):
            continue  # 如果解码失败，尝试下一个编码

    if book_text is None:
        raise ValueError("无法使用检测到的编码解码文件")
    
    return book_text

def combine_txt_files(folder_path: str | Path):
    """
    将指定文件夹内的所有txt文件按文件名中的数字排序，合并为一个新的txt文件。
    合并时每个文件的内容前面加入该文件的名字，合并文件名为文件夹名。

    :param folder_path: 包含txt文件的文件夹路径。
    :return: None
    """
    def extract_number(file_name: Path) -> int:
        """
        从文件名中提取数字，用于排序。
        """
        matches = re.findall(r'\d+', file_name.name)
        return int(''.join(matches)) if matches else float('inf')

    # 转换路径为 Path 对象
    folder_path = Path(folder_path)

    if not folder_path.is_dir():
        raise ValueError(f"The provided path {folder_path} is not a directory.")

    # 获取文件夹名称作为输出文件名
    output_file_name = f"{folder_path.name}.txt"
    output_file_path = folder_path / output_file_name

    # 获取所有txt文件路径，并按文件名中的数字排序
    txt_files = sorted(folder_path.glob('*.txt'), key=extract_number)

    if not txt_files:
        raise ValueError(f"No txt files found in {folder_path}.")

    # 合并文件
    with open(output_file_path, 'w', encoding='utf-8') as outfile:
        for txt_file in tqdm(txt_files):
            with open(txt_file, 'r', encoding='utf-8') as infile:
                content = infile.read()
                # 写入文件名和内容
                outfile.write(f"== {txt_file.name} ==\n\n")
                outfile.write(content + "\n\n")

    print(f"All files have been combined into {output_file_path}")

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
    def update_common(common_parts, current_part):
        if current_part:
            common_parts.append(''.join(reversed(current_part)))
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

            if (i == 1 or j == 1):
                common_parts, current_part = update_common(common_parts, current_part)
                common_parts.append('') if i != j else None
            
            i -= 1  # 移动到左上格子
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1] or (dp[i - 1][j] == dp[i][j - 1] and str1[i - 1] != str1[0]):  # 如果上方格子值较大
            common_parts, current_part = update_common(common_parts, current_part)
            if (i == len1 or j == len2 or i == 1):
                if not (common_parts and common_parts[-1] == ''): 
                    common_parts.append('')
            i -= 1  # 移动到上方格子
        else:  # 左方格子值较大
            common_parts, current_part = update_common(common_parts, current_part)
            if (i == len1 or j == len2 or j == 1):
                if not (common_parts and common_parts[-1] == ''): 
                    common_parts.append('')
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
    lcs_length = len(''.join(lcs_parts))
    
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

def format_table(data: list, column_names: list = None, row_names: list = None, fill_value: str = 'N/A') -> str:
    """
    格式化并打印表格。

    :param data: 表格数据，二维列表，每行代表一行数据
    :param column_names: 列名，列表，每列的名称
    :param row_names: 自定义的行号，列表，如果为None则使用默认行号（0, 1, 2, 3...）
    :param fill_value: 当数据为空时填充的值
    :return: 格式化后的表格字符串
    """
    for num, row in enumerate(data):
        add_colnum = row_names[num] if row_names else num
        data[num] = [add_colnum, ] + list(row)

    # 获取列数
    num_columns = len(column_names) if column_names else max(len(row) for row in data)
    num_columns += 1

    # 如果未提供列名，则自动生成
    if column_names is None:
        column_names = [f"Column {i+1}" for i in range(num_columns-1)]

    # 为表格添加序列列标题
    column_names = ["#"] + column_names

    # 计算每列的最大宽度（包括列名和数据）
    col_widths = [max(len(str(row[i])) if i < len(row) else len(fill_value) for row in data) for i in range(num_columns)]
    col_widths = [max(len(name), width) for name, width in zip(column_names, col_widths)]

    # 创建表格的顶部
    table = "+" + "+".join(["-" * (width + 2) for width in col_widths]) + "+"
    table += "\n"

    # 添加列名行
    table += "| " + " | ".join([f"{name:<{col_widths[i]}}" for i, name in enumerate(column_names)]) + " |"
    table += "\n"

    # 添加分隔行
    table += "+" + "+".join(["-" * (width + 2) for width in col_widths]) + "+"
    table += "\n"

    # 添加数据行
    for row in data:
        table += "| " + " | ".join([
            f"{str(row[i]) if i < len(row) else fill_value:<{col_widths[i]}}"
            for i in range(num_columns)
        ]) + " |"
        table += "\n"

    # 添加底部分隔行
    table += "+" + "+".join(["-" * (width + 2) for width in col_widths]) + "+"

    return table