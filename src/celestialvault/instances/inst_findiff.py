# -*- coding: utf-8 -*-
# 版本 2.10
# 作者：晓天

from typing import List

from ..tools.ListDictTools import dictkey_mix
from ..tools.TextTools import calculate_similarity, get_lcs, string_split


class Findiffer:
    def __init__(
        self, norm_end: str = "[", diff_end: str = "]", split_part_str: str = "[]"
    ) -> None:
        """
        :param norm_end: can use '\033[0m' '_' '[' or others.
        :param diff_end: can use '\033[1m' '_' ']' or others.
        :param split_part_str: can use '-' '_' '[]'or others.
        """
        self.norm_end = norm_end
        self.diff_end = diff_end
        self.split_part_str = split_part_str

    def fd_str(self, string_a: str, string_b: str, split_str: str = None):
        # 以split_str为分割符将a和b分割
        list_a = string_split(string_a, split_str=split_str)
        list_b = string_split(string_b, split_str=split_str)
        part_len = min(len(list_a), len(list_b))

        # 比较a和b的每一部分
        for i in range(part_len):
            if list_a[i] == list_b[i]:
                continue

            # 如果a和b的每一行不同，则调用compare_strings()方法比较
            lcs_part = get_lcs(list_a[i], list_b[i])
            self.compare_strings(list_a[i], list_b[i], lcs_part)

            # print(f"(LCS: {self.split_part_str.join(lcs_part)})")
            similarity = calculate_similarity(list_a[i], list_b[i], lcs_part)
            if part_len > 1:
                print(f"(第{i+1}行, 相似度：{similarity})\n")
            else:
                print(f"(相似度：{similarity})\n")

    def fd_dict(self, dict_a: dict, dict_b: dict):
        _, key_min, dif_key_a, dif_key_b = dictkey_mix(dict_a, dict_b)

        print("a b的共有标签值为:")
        for key in key_min:
            if dict_a[key] == dict_b[key]:
                continue

            print(f"{key}:")
            lcs_part = get_lcs(dict_a[key], dict_b[key])
            self.compare_strings(dict_a[key], dict_b[key], lcs_part)
            similarity = calculate_similarity(dict_a[key], dict_b[key], lcs_part)
            # print(f"(LCS: {self.split_part_str.join(lcs_part)})")
            print(f"(相似度：{similarity})\n")

        if dif_key_a:
            print("a中的特有标签值为:")
            for key in dif_key_a:
                print(f"{key}:{dict_a[key]}")
            print()

        if dif_key_b:
            print("b中的特有标签值为:")
            for key in dif_key_b:
                print(f"{key}:{dict_b[key]}")

    def compare_strings(self, str1: str, str2: str, lcs_part: List[str] = None) -> None:
        lcs_part = get_lcs(str1, str2, lcs_part) if lcs_part is None else lcs_part

        diff_ranges_1 = self.get_diff_ranges(str1, lcs_part[:])
        diff_ranges_2 = self.get_diff_ranges(str2, lcs_part[:])

        self.print_diffs(str1, diff_ranges_1)
        self.print_diffs(str2, diff_ranges_2)

    def get_diff_ranges(self, origin_str: str, lcs_part: List[str]) -> List[List[int]]:
        """
        根据get_lcs返回的相似部分，计算字符串中不同区域的位置

        :param origin_str: 原始字符串
        :param lcs_part: 相似部分列表
        :return: 不同区域的位置列表
        """
        if len(lcs_part) == 1 and lcs_part[0] == "":
            return [[0, len(origin_str)]]

        diff_ranges_reverse = []
        start_index = -1
        end_index = 0
        str_len = len(origin_str)

        # 反转字符串和相似部分列表
        str_reverse = origin_str[::-1]
        lcs_part_reverse = [similar_str[::-1] for similar_str in lcs_part[::-1]]

        for num, similar_str_reverse in enumerate(lcs_part_reverse):
            if not similar_str_reverse:
                if num == 0:
                    start_index = 0
                elif num == len(lcs_part) - 1:
                    end_index = str_len
                    diff_ranges_reverse.append([start_index, end_index])
                continue

            if start_index != -1:
                end_index = (
                    str_reverse[start_index:].find(similar_str_reverse) + start_index
                )
                diff_ranges_reverse.append([start_index, end_index])

            start_index = end_index + len(similar_str_reverse)

        # 将位置转换回正序
        diff_ranges = [
            [str_len - dr[1], str_len - dr[0]] for dr in diff_ranges_reverse[::-1]
        ]

        return diff_ranges

    def print_diffs(self, input_str: str, diff_ranges: list) -> None:
        """
        Print differences to stderr.

        :param input_str: The input string to print.
        :param diff_ranges: The ranges of differences to print.
        """
        prev_end_index = 0
        for start_index, end_index in diff_ranges:
            end_index = min(end_index, len(input_str))
            print(input_str[prev_end_index:start_index], end=self.norm_end)
            print(input_str[start_index:end_index], end=self.diff_end)
            prev_end_index = end_index
        print(input_str[prev_end_index:])
