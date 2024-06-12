import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest, logging
from time import time
from instances import ThreadManager, ExampleThreadManager


async def generate_new_tasks_async(n):
    return [i for i in range(n, n+5)]

def generate_new_tasks(n):
    return [i for i in range(n, n+5)]

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
                                   show_progress=False)

    # Assuming dictory is the list of tasks you want to test
    results = manager.test_methods(range(10, 16))
    logging.info(results)

# def test_multiprocessing():
#     manager = ExampleThreadManager(generate_new_tasks, thread_num=6, 
#                                    show_progress=False)

#     start_time = time()
#     manager.start(range(100), 'multiprocessing')
#     logging.info(time() - start_time)