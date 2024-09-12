# -*- coding: utf-8 -*-
#版本 2.10
#作者：晓天

from tools.TextTools import strings_split
from tools.ListDictTools import dictkey_mix

class Findiffer:
    def __init__(self) -> None:
        pass

    def fd_str(self, string_a, string_b, split_str = '\n'):
        # 打印出a和b的长度
        print(f'len(a):{len(string_a)}, len(b):{len(string_b)}\n')
        # 打印出a和b不同的地方
        print(f'a与b不同的地方为(以{split_str}为划分):\n')

        # 以split_str为分割符将a和b分割成多行
        a,b = strings_split([string_a, string_b], split_str=split_str)
        
        # 比较a和b的每一行
        for i in range(min(len(a),len(b))):
            if a[i] != b[i]:
                # 如果a和b的每一行不同，则调用compare_strings()方法比较
                self.compare_strings(a[i],b[i])
                # 打印出每一行的行号
                print('(第%d行)\n'%(i+1))


    def fd_dict(self, dict_a, dict_b):
        # a_keys_values = [list(i) for i in zip(*dict_a.items())]    
        key_max,key_min,dif_key_a,dif_key_b = dictkey_mix(
            dict_a,dict_b
            )
    
        for key in key_min:
            if dict_a[key] == dict_b[key]:
                pass
            else:
                print(key, ':')
                self.compare_strings(dict_a[key],dict_b[key])
                print()
                
        if dif_key_a != []:
            print('a中的特有标签值为：')
            for key in dif_key_a:
                print(f'{key} :\n{dict_a[key]}')
        print()
                
        if dif_key_b != []:
            print('b中的特有标签值为')
            for key in dif_key_b:
                print(f'{key} :\n{dict_b[key]}')
                
    def compare_strings(self, str1: str, str2: str) -> None:
        """
        Compare two strings and print differences to stderr.
        
        Args:
        str1: The first string to compare.
        str2: The second string to compare.
        """
        diff_start_index = -1
        diff_ranges = []
        longer_str = str1[:] if len(str1) >= len(str2) else str2[:]
        shorter_str = str2[:] if len(str1) >= len(str2) else str1[:]

        if str1 == str2:
            print('完全一致')
            return
        
        for idx in range(len(shorter_str)):
            if str1[idx] == str2[idx]: 
                if diff_start_index == -1:
                    continue
                diff_ranges.append((diff_start_index, idx))
                # 重置diff_start_index 表示我们目前没有在记录差异区间
                diff_start_index = -1
            elif str1[idx] != str2[idx]:
                if diff_start_index == -1:
                    diff_start_index = idx

        if diff_start_index != -1:
            diff_ranges.append((diff_start_index, len(longer_str)))
        elif not diff_ranges:
            diff_ranges.append((len(shorter_str), len(longer_str)))
                    
        self.print_diffs(str1, diff_ranges)
        self.print_diffs(str2, diff_ranges)

    def print_diffs(self, input_str: str, diff_ranges: list, 
                norm_end = '\033[0m', diff_end = '\033[1m') -> None:
        """
        Print differences to stderr.
        
        :param input_str: The input string to print.
        :param diff_ranges: The ranges of differences to print.
        :param norm_end: can use '\033[0m' '_' or others.
        :param diff_end: can use '\033[1m' '_' or others.
        """
        prev_end_index = 0
        for start_index, end_index in diff_ranges:
            end_index = min(end_index, len(input_str))
            print(input_str[prev_end_index:start_index], end = norm_end)
            print(input_str[start_index:end_index], end = diff_end)
            prev_end_index = end_index
        print(input_str[prev_end_index:])
