import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import logging
from src.tools.TextTools import pro_slash, str_to_dict

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
    test_string = "key1:value1\nkey2:value2\n\n:key3:value3"
    result_dict = str_to_dict(test_string)
    logging.info(f"{'Test input':<15}:\n{test_string}")
    logging.info(f"{'Expected output':<15}: {{'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}}")
    logging.info(f"{'Actual output':<15}: {result_dict}")