import pytest, logging
import time
from celestialvault.tools.Utilities import get_total_size, log_time

def test_get_total_size():
    data = {
        'key1': [1, 2, 3],
        'key2': (4, 5),
        'key3': {6, 7, 8},
        'key4': {'nested_key': [9, 10]}
    }

    size = get_total_size(data)  # 输出对象总内存大小

    logging.info(f"{'Input':<15}:\n{data}")
    logging.info(f"{'Expected output':<15}: 1KB 423B")
    logging.info(f"{'Actual output':<15}: {size}\n")

def test_log_time():
    @log_time
    def print_num(num):
        time.sleep(num)
        print(num)

    print_num(5)