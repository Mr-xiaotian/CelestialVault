import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest, logging
from tools.ListDictTools import list_removes, list_replace, multi_loop_generator, dictkey_mix, batch_generator

def test_list_removes():
    input_list = [1, 2, 3, 2, 4, 2]
    result = list_removes(input_list, 2)

    logging.info(f"{'Test input':<15}: {input_list}")
    logging.info(f"{'Expected output':<15}: [1, 3, 4]")
    logging.info(f"{'Actual output':<15}: {result}")
    assert result == [1, 3, 4], "Should remove all 2s from the list"

def test_list_replace():
    input_list = [1, 2, '123456', 'dfg3', [51, 'a'], lambda x: x]
    replace_rules = [(2, 5), ('123', '321'), ('dfg3', 6), (lambda x: x, 'def'), ([51, 'a'], [15, 'b'])]
    result = list_replace(input_list, replace_rules)
    
    logging.info(f"{'Test input':<15}: {input_list}")
    logging.info(f"{'Replace rules':<15}: {replace_rules}")
    logging.info(f"{'Expected output':<15}: [1, 5, '321456', 6, [15, 'b'], 'def']")
    logging.info(f"{'Actual output':<15}: {result}")

def test_multi_loop_generator():
    input_list = [1, 2, 3]
    for i in multi_loop_generator(input_list, [88, 99]):
        logging.info(f"{'Generator output':<16}: {i}")

def test_dictkey_mix():
    dict_a = {'a': 1, 'b': 2, 'c': 3}
    dict_b = {'b': 2, 'c': 4, 'd': 5}
    key_max, key_min, dif_key_a, dif_key_b = dictkey_mix(dict_a, dict_b)

    logging.info(f"{'Test input':<15}: {dict_a}, {dict_b}")
    logging.info(f"{'Expected output':<15}: (['a', 'b', 'c', 'd'], ['b', 'c'], ['a'], ['d'])")
    logging.info(f"{'Actual output':<15}: ({key_max}, {key_min}, {dif_key_a}, {dif_key_b})")

def test_batch_generator():
    # 测试用生成器
    def simple_generator():
        for i in range(1, 11):
            yield i

    # 测试输入数据
    input_generator = simple_generator()
    batch_size = 3
    expected_batches = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]]

    # 实际输出
    actual_batches = list(batch_generator(input_generator, batch_size))

    # 日志输出
    logging.info(f"{'Input generator':<20}: simple_generator()")
    logging.info(f"{'Batch size':<20}: {batch_size}")
    logging.info(f"{'Expected batches':<20}: {expected_batches}")
    logging.info(f"{'Actual batches':<20}: {actual_batches}")