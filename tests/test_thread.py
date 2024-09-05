import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest, logging, asyncio
from time import time
from instances.task_manager import TaskManager, ExampleTaskManager, TaskChain


def square(n):
    return n * n

async def fibonacci_async(n):
    if n <= 0:
        raise ValueError("n must be a positive integer")
    elif n == 1:
        return 1
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
        return 1
    elif n == 2:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)

# 测试 TaskManager 的同步任务
def test_thread_manager():
    manager = ExampleTaskManager(fibonacci, thread_num=6, show_progress=True)
    results = manager.test_methods([30]*12)
    logging.info(results)

# 测试 TaskManager 的异步任务
@pytest.mark.asyncio
async def test_thread_manager_async():
    manager = ExampleTaskManager(fibonacci_async, thread_num=6, show_progress=True)
    start = time()
    await manager.start_async([30]*12)
    logging.info(f'run_in_async: {time() - start}')

# 测试 TaskChain 的功能
def test_task_chain():
    # 定义多个阶段的 TaskManager 实例，假设我们使用 Fibonacci 作为每个阶段的任务
    stage1 = ExampleTaskManager(fibonacci, process_mode='parallel', thread_num=4, show_progress=False)
    stage2 = ExampleTaskManager(square, process_mode='serial', thread_num=4, show_progress=False)

    # 初始化 TaskChain
    chain = TaskChain([stage1, stage2])

    # 要测试的任务列表
    tasks = range(25,31)

    # 开始任务链
    start_time = time()
    chain.start_chain(tasks)
    logging.info(f'TaskChain completed in {time() - start_time} seconds')

    # 打印结果
    final_result_dict = chain.get_final_result_dict()
    logging.info(f"Task result: {final_result_dict}")