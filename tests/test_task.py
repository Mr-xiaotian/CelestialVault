import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest, logging, asyncio
import cProfile, subprocess
from time import time, strftime, localtime
from instances.inst_task import ExampleTaskManager, TaskChain


def square(n):
    return n * n

def fibonacci(n):
    if n <= 0:
        raise ValueError("n must be a positive integer")
    elif n == 1:
        return 1
    elif n == 2:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)

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

# 测试 TaskManager 的同步任务
def test_task_manager():
    test_task_0 = range(25, 37)
    test_task_1 = list(range(25,32)) + [0, 27, None, 0, '']

    manager = ExampleTaskManager(fibonacci, worker_limit=6, show_progress=True)
    results = manager.test_methods(test_task_1)
    logging.info(results)

# 测试 TaskManager 的异步任务
@pytest.mark.asyncio
async def test_task_manager_async():
    test_task_0 = range(25, 37)
    test_task_1 = list(range(25,32)) + [0, 27, None, 0, '']

    manager = ExampleTaskManager(fibonacci_async, worker_limit=6, show_progress=True)
    start = time()
    await manager.start_async(test_task_1)
    logging.info(f'run_in_async: {time() - start}')

# 测试 TaskChain 的功能
def test_task_chain():
    # 定义多个阶段的 TaskManager 实例，假设我们使用 Fibonacci 作为每个阶段的任务
    stage1 = ExampleTaskManager(fibonacci, execution_mode='parallel', worker_limit=4, show_progress=False)
    stage2 = ExampleTaskManager(square, execution_mode='serial', worker_limit=4, show_progress=False)

    # 初始化 TaskChain
    chain = TaskChain([stage1, stage2])

    # 要测试的任务列表
    tasks_0 = range(25,31)
    tasks_1 = list(range(25,32)) + [0, 27, None, 0, '']

    # 开始任务链
    result = chain.test_methods(tasks_1)
    logging.info(result)

def profile_task_chain():
    target_func = 'test_task_manager'
    now_time = strftime("%m-%d-%H-%M", localtime())
    output_file = f'profile/{target_func}({now_time}).prof'
    cProfile.run(target_func + '()', output_file)

    subprocess.run(['snakeviz', output_file])

# 在主函数或脚本中调用此函数，而不是在测试中
if __name__ == "__main__":
    profile_task_chain()