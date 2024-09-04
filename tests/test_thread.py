import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest, logging
from instances.my_thread import ThreadManager, ExampleThreadManager


async def fibonacci_async(n):
    if n <= 0:
        raise ValueError("n must be a positive integer")
    elif n == 1:
        return 0
    elif n == 2:
        return 1
    else:
        await fibonacci_async(n-1) + fibonacci_async(n-2)

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
    manager = ExampleThreadManager(fibonacci, thread_num=50, 
                                   show_progress=True)

    # Assuming dictory is the list of tasks you want to test
    results = manager.test_methods([30]*100)
    logging.info(results)

# def test_multiprocessing():
#     manager = ExampleThreadManager(generate_new_tasks, thread_num=6, 
#                                    show_progress=False)

#     start_time = time()
#     manager.start(range(100), 'multiprocessing')
#     logging.info(time() - start_time)