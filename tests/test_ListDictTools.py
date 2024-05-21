import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import logging
from src.tools.ListDictTools import list_removes, list_replace, dictkey_mix

def test_list_removes():
    input_list = [1, 2, 3, 2, 4, 2]
    result = list_removes(input_list, 2)
    logging.info(f"{'Test input':<15}: {input_list}")
    logging.info(f"{'Expected output':<15}: [1, 3, 4]")
    logging.info(f"{'Actual output':<15}: {result}")
    assert result == [1, 3, 4], "Should remove all 2s from the list"

def test_list_replace():
    input_list = [1, 2, 'dfg3', [51, 'a'], 4, lambda x: x]
    replace_list = [(2, 5), ('dfg3', 6), (lambda x: x, 'def'), ([51, 'a'], [15, 'b'])]
    result = list_replace(input_list, replace_list)
    logging.info(f"{'Test input':<15}: {input_list}")
    logging.info(f"{'Expected output':<15}: [1, 5, 6, [15, 'b'], 4, 'def']")
    logging.info(f"{'Actual output':<15}: {result}")

def test_dictkey_mix():
    dict_a = {'a': 1, 'b': 2, 'c': 3}
    dict_b = {'b': 2, 'c': 4, 'd': 5}

    key_max, key_min, dif_key_a, dif_key_b = dictkey_mix(dict_a, dict_b)
    logging.info(f"{'Test input':<15}: {dict_a}, {dict_b}")
    logging.info(f"{'Expected output':<15}: (['a', 'b', 'c', 'd'], ['b', 'c'], ['a'], ['d'])")
    logging.info(f"{'Actual output':<15}: ({key_max}, {key_min}, {dif_key_a}, {dif_key_b})")
