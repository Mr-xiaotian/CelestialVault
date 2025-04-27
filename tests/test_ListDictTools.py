import pytest, logging
from celestialvault.tools.ListDictTools import list_removes, list_replace, dictkey_mix, batch_generator

def test_list_removes():
    input_list = [1, 2, 3, 2, 4, 2]
    result = list_removes(input_list, 2)

    logging.info(f"{'Test input':<15}: {input_list}")
    logging.info(f"{'Expected output':<15}: [1, 3, 4]")
    logging.info(f"{'Actual output':<15}: {result}")

def test_list_replace():
    input_list = [1, 2, '123456', 'dfg3', [51, 'a'], lambda x: x]
    replace_rules = [(2, 5), ('123', '321'), ('dfg3', 6), (lambda x: x, 'def'), ([51, 'a'], [15, 'b'])]
    result = list_replace(input_list, replace_rules)
    
    logging.info(f"{'Test input':<15}: {input_list}")
    logging.info(f"{'Replace rules':<15}: {replace_rules}")
    logging.info(f"{'Expected output':<15}: [1, 5, '321456', 6, [15, 'b'], 'def']")
    logging.info(f"{'Actual output':<15}: {result}")

def test_dictkey_mix():
    dict_a = {'a': 1, 'b': 2, 'c': 3}
    dict_b = {'b': 2, 'c': 4, 'd': 5}
    key_max, key_min, dif_key_a, dif_key_b = dictkey_mix(dict_a, dict_b)

    logging.info(f"{'Test input':<15}: {dict_a}, {dict_b}")
    logging.info(f"{'Expected output':<15}: (['a', 'b', 'c', 'd'], ['b', 'c'], ['a'], ['d'])")
    logging.info(f"{'Actual output':<15}: ({key_max}, {key_min}, {dif_key_a}, {dif_key_b})")

def test_batch_generator():
    # 测试输入数据
    input_generator = iter(range(1, 11))
    batch_size = 3

    # 实际输出
    actual_batches = list(batch_generator(input_generator, batch_size))

    # 日志输出
    logging.info(f"{'Input generator':<16}: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]")
    logging.info(f"{'Batch size':<16}: {batch_size}")
    logging.info(f"{'Expected batches':<16}: [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]]")
    logging.info(f"{'Actual batches':<16}: {actual_batches}")