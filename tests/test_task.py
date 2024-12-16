import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest, logging, asyncio
import cProfile, subprocess
from time import time, strftime, localtime, sleep
from instances.inst_task import ExampleTaskManager, TaskChain


def square(n):
    if n == 317811:
        raise ValueError("Test error in 317811")
    return n * n

def half(n):
    return n / 2

def sleep_1(n):
    sleep(1)
    return n

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
def _test_task_manager():
    test_task_0 = range(25, 37)
    test_task_1 = list(range(25,32)) + [0, 27, None, 0, '']

    manager = ExampleTaskManager(fibonacci, worker_limit=6, max_retries = 1, show_progress=True)
    manager.add_retry_exceptions(TypeError)
    results = manager.test_methods(test_task_1)
    logging.info(results)

# 测试 TaskManager 的异步任务
@pytest.mark.asyncio
async def _test_task_manager_async():
    test_task_0 = range(25, 37)
    test_task_1 = list(range(25,32)) + [0, 27, None, 0, '']

    manager = ExampleTaskManager(fibonacci_async, worker_limit=6, max_retries = 1, show_progress=True)
    manager.add_retry_exceptions(ValueError)
    start = time()
    await manager.start_async(test_task_1)
    logging.info(f'run_in_async: {time() - start}')

# 测试 TaskChain 的功能
def test_task_chain():
    # 定义多个阶段的 TaskManager 实例，假设我们使用 Fibonacci 作为每个阶段的任务
    stage1 = ExampleTaskManager(fibonacci, execution_mode='thread', worker_limit=4, max_retries = 1, show_progress=False)
    stage2 = ExampleTaskManager(square, execution_mode='thread', worker_limit=4, max_retries = 1, show_progress=False)
    stage3 = ExampleTaskManager(half, execution_mode='thread', worker_limit=4, show_progress=False)
    stage4 = ExampleTaskManager(sleep_1, execution_mode='thread', worker_limit=4, show_progress=False)

    stage1.set_chain_context([stage2, stage4], 'process', stage_name='satge1')
    stage2.set_chain_context([stage3], 'process', stage_name='satge2')
    stage3.set_chain_context([], 'process', stage_name='satge3')
    stage4.set_chain_context([], 'process', stage_name='satge4')

    stage1.add_retry_exceptions(TypeError)
    stage2.add_retry_exceptions(ValueError)

    # 初始化 TaskChain
    chain = TaskChain(root_stage = stage1)

    # 要测试的任务列表
    tasks_0 = range(25, 37)
    tasks_1 = list(range(25, 32)) + [0, 27, None, 0, '']

    # 开始任务链
    result = chain.test_methods(tasks_1)
    logging.info(f"{'serial chain':<17}: {result['serial chain']}")
    logging.info(f"{'process chain':<17}: {result['process chain']}")
    logging.info(f"{'Final result dict':<17}: {result['Final result dict']}")
    logging.info(f"{'Final error dict':<17}: {result['Final error dict']}")

def profile_task_chain():
    target_func = 'test_task_manager'
    now_time = strftime("%m-%d-%H-%M", localtime())
    output_file = f'profile/{target_func}({now_time}).prof'
    cProfile.run(target_func + '()', output_file)

    subprocess.run(['snakeviz', output_file])

# 在主函数或脚本中调用此函数，而不是在测试中
if __name__ == "__main__":
    profile_task_chain()