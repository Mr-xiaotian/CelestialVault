import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest, logging, asyncio
from time import time
from instances.my_thread import ThreadManager, ExampleThreadManager


async def fibonacci_async(n):
    if n <= 0:
        raise ValueError("n must be a positive integer")
    elif n == 1:
        return 0
    elif n == 2:
        return 1
    else:
        # 并发执行两个异步递归调用
        result_0 = await fibonacci_async(n-1)
        result_1 = await fibonacci_async(n-2)
        return result_0 + result_1

def fibonacci(n):
    if n <= 0:
        raise ValueError("n must be a positive integer")
    elif n == 1:
        return 0
    elif n == 2:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)

def test_thread_manager():
    # We instantiate the ThreadManager
    manager = ExampleThreadManager(fibonacci, thread_num=6, 
                                   show_progress=True)

    # Assuming dictory is the list of tasks you want to test
    results = manager.test_methods([30]*12)
    logging.info(results)

@pytest.mark.asyncio
async def test_thread_manager_async():
    # We instantiate the ThreadManager
    manager = ExampleThreadManager(fibonacci_async, thread_num=6,
                                   show_progress=True)

    # Assuming dictory is the list of tasks you want to test
    start = time()
    await manager.start_async([30]*12)
    logging.info(f'run_in_serial: {time() - start}')