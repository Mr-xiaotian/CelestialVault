import jieba, re, string
from jieba import analyse 
from pprint import pprint
from typing import List, Dict, Union, Tuple


def pro_slash(input_str: str) -> str:
    """
    移除字符串中多余的转义符。

    参数:
    input_str (str): 要处理的字符串。

    返回值:
    str: 移除多余转义符后的字符串。
    """
    '''
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
    '''
    if not input_str:
        return input_str
    
    # 替换多余的转义符
    result_str = input_str.replace('\\\\', '\\')
    
    # 替换其他转义符
    result_str = result_str.replace(r'\/', '/')
    
    return result_str

def str_to_dict(string: str, spli_str: str = "\n") -> Dict[str, str]:
    """
    将字符串转化为字典，每行格式为 `key:value`，以指定的分隔符分隔行。

    参数:
    string (str): 包含键值对的字符串，每行一个键值对。
    spli_str (str): 用于分隔行的字符串，默认是换行符。

    返回值:
    Dict[str, str]: 转化后的字典。
    """
    # 使用列表推导式去除空字符串
    string_list = [line for line in string.split(spli_str) if line.strip()]

    headers = {}

    for line in string_list:
        # 去掉行首的冒号
        if line.startswith(':'):
            line = line[1:]
        
        # 分割键和值
        key, _, value = line.partition(':')
        headers[key.strip()] = value.strip()

    return headers

def str_removes(strs: str, _remove: str) -> str:
    """
    从字符串中移除指定的子串。
    
    Args:
        strs (str): 原始字符串。
        _remove (str): 需要从原始字符串中移除的子串。
    
    Returns:
        str: 移除指定子串后的新字符串。
    """
    return strs.replace(_remove, '')

def str_replaces(strs: str, replace_list: list[Tuple[str, str]]) -> str:
    for r in replace_list:
        strs = strs.replace(r[0], r[1])
    return strs

def iprint(obj: Union[List, Dict], start='', end=''):
    """
    根据对象的大小选择打印方式。
    如果对象的长度小于16，那么就打印整个对象，否则只打印前10个和后5个元素。

    Args:
        obj (Union[List, Dict]): 需要打印的对象，可以是列表或字典。
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

def deal_cookie(*cookies):
    """
    处理cookie，将cookie字符串转化为字典。
    """
    cookie_dicts = []
    for cookie in cookies:
        #cookie += '; '

        cookie_list = cookie.split('; ')
        cookie_dict = {}
        for c_l in cookie_list:
            #print(c_l)
            key,_,value = c_l.partition('=')
            cookie_dict[key] = value
        cookie_dicts.append(cookie_dict)

    return cookie_dicts

def string_split(string: str, split_str: str='\n') -> list[str]:
    """
    将字符串按指定分隔符分割，返回一个列表，每个元素是分割后非空的子字符串。
    """
    return [s for s in string.split(split_str) if s]

def strings_split(string_list: list[str], split_str: str='\n') -> list[list[str]]:
    """
    将多个字符串按指定分隔符分割，返回一个列表，每个元素是分割后非空的子字符串列表。
    """
    return [string_split(st, split_str) for st in string_list]

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
    # print(chinese_char_count / len(text))
    
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
    # print(valid_char_count / len(text))
    
    # 计算文本中有效字符的比例
    return valid_char_count / len(text)

def is_valid_chinese_text(text: str, threshold: int=0.8):
    """
    判断文本是否为有效文本，即文本中有效字符的比例是否大于阈值。
    """
    return calculate_valid_chinese_text(text) > threshold

def is_valid_text(text: str, threshold: int=0.9):
    """
    判断文本是否为有效文本，即文本中有效字符的比例是否大于阈值。
    """
    return calculate_valid_text(text) > threshold