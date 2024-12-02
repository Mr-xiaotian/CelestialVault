import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest, logging
from tools.Utilities import get_total_size, bytes_to_human_readable

def test_get_total_size():
    data = {
        'key1': [1, 2, 3],
        'key2': (4, 5),
        'key3': {6, 7, 8},
        'key4': {'nested_key': [9, 10]}
    }

    size = get_total_size(data)  # 输出对象总内存大小
    reable_size = bytes_to_human_readable(size)

    logging.info(f"{'Input':<15}:\n{data}")
    logging.info(f"{'Expected output':<15}: 1KB 423B")
    logging.info(f"{'Actual output':<15}: {reable_size}\n")