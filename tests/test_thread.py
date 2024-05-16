import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest, logging
from src.instances import ThreadManager, ExampleThreadManager


async def generate_new_tasks(n):
    return [i for i in range(n, n+5)]

def test_thread_manager():
    # We instantiate the ThreadManager
    manager = ExampleThreadManager(generate_new_tasks, thread_num=10, 
                                   show_progress=False)

    # We start the threads
    # manager.start(range(100), start_type="parallel")

    # # We process the results
    # manager.process_result()

    # # We handle the errors
    # manager.handle_error()

    # Assuming dictory is the list of tasks you want to test
    results = manager.test_methods(range(100))
    logging.info(results)


