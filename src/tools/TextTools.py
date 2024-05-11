from pprint import pprint
from typing import List, Dict, Union, Tuple
from .ListDictTools import list_removes

def pro_slash(strs: str) -> str:
    """
    消除字符串中多余的转义符。
    """
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

def str_to_dict(strs: str) -> Dict[str, str]:
    """
    将字符串转化为字典。
    """
    header = strs.split('\n')
    headers = {}
    
    while '' in header:
        header.remove('')

    for h in header:
        if h[0] == ':':
            h = h[1:]
        sp = h.partition(':')
        headers[sp[0]] = sp[2].strip()

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

def str_replaces(strs: str, replace_list: list) -> str:
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

def string_split(string, split_str='\n'):
    """
    将字符串按指定分隔符分割，返回一个列表，每个元素是分割后非空的子字符串。
    """
    return [s for s in string.split(split_str) if s]

def strings_split(string_list, split_str='\n'):
    """
    将多个字符串按指定分隔符分割，返回一个列表，每个元素是分割后非空的子字符串列表。
    """
    return [string_split(st, split_str) for st in string_list]


