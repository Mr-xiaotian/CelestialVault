import pytest, logging, asyncio, pprint
import cProfile, subprocess, random
from time import time, strftime, localtime, sleep
from celestialvault.tools.TextTools import format_table
from celestialvault.instances.inst_task import TaskManager, TaskTree, TaskSplitter

def sleep_1(n):
    sleep(1)
    return n

def sleep_random_02(n):
    sleep(random.randint(0, 2))
    return n

def sleep_random_46(n):
    sleep(random.randint(4, 6))
    return n

def sleep_random_A(n):
    return sleep_random_02(n)
def sleep_random_B(n):
    return sleep_random_02(n)
def sleep_random_C(n):
    return sleep_random_02(n)
def sleep_random_D(n):
    return sleep_random_02(n)
def sleep_random_E(n):
    return sleep_random_02(n)
def sleep_random_F(n):
    return sleep_random_02(n)

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

def add_one(x):
    return x + 1

def subtract_one(x):
    return x - 1

def multiply_by_two(x):
    return x * 2

def divide_by_two(x):
    return x / 2

def square(x):
    if x == 317811:
        raise ValueError("Test error in 317811")
    return x ** 2

def square_root(x):
    return x ** 0.5

def generate_urls(x):
    return tuple([f"url_{x}_{i}" for i in range(random.randint(1, 4))])

def log_urls(data):
    if data == ('url_1_0', 'url_1_1'):
        raise ValueError("Test error in ('url_1_0', 'url_1_1')")
    return f"Logged({data})"

def download(url):
    if "url_3" in url:
        raise ValueError("Test error in url_3_*")
    return f"Downloaded({url})"

def parse(url):
    return f"Parsed({url})"

def generate_urls_sleep(x):
    sleep_random_46(5)
    return tuple([f"url_{x}_{i}" for i in range(random.randint(1, 4))])

def log_urls_sleep(url):
    sleep_random_46(5)
    if url == ('url_1_0', 'url_1_1'):
        raise ValueError("Test error in ('url_1_0', 'url_1_1')")
    return f"Logged({url})"

def download_sleep(url):
    sleep_random_46(5)
    if "url_3" in url:
        raise ValueError("Test error in url_3_*")
    return f"Downloaded({url})"

def parse_sleep(url):
    sleep_random_46(5)
    return f"Parsed({url})"

# 测试 TaskManager 的同步任务
def _test_task_manager():
    test_task_0 = range(25, 37)
    test_task_1 = list(range(25,32)) + [0, 27, None, 0, '']
    test_task_2 = (item for item in test_task_1)

    manager = TaskManager(fibonacci, worker_limit=6, max_retries = 1, show_progress=True)
    manager.add_retry_exceptions(ValueError)
    results = manager.test_methods(test_task_1)
    logging.info(results)
    # manager.start(test_task_1)

# 测试 TaskManager 的异步任务
@pytest.mark.asyncio
async def _test_task_manager_async():
    test_task_0 = range(25, 37)
    test_task_1 = list(range(25,32)) + [0, 27, None, 0, '']
    test_task_2 = (item for item in test_task_1)

    manager = TaskManager(fibonacci_async, worker_limit=6, max_retries = 1, show_progress=True)
    manager.add_retry_exceptions(ValueError)
    start = time()
    await manager.start_async(test_task_1)
    logging.info(f'run_in_async: {time() - start}')

# 测试 TaskTree 的功能
def _test_task_tree_0():
    # 定义多个阶段的 TaskManager 实例
    stage1 = TaskManager(fibonacci, execution_mode='thread', worker_limit=4, max_retries=1, show_progress=False)
    stage2 = TaskManager(square, execution_mode='thread', worker_limit=4, max_retries=1, show_progress=False)
    stage3 = TaskManager(divide_by_two, execution_mode='thread', worker_limit=4, show_progress=False)
    stage4 = TaskManager(sleep_1, execution_mode='thread', worker_limit=4, show_progress=False)

    stage1.set_tree_context([stage2, stage4], 'process', stage_name='stage1')
    stage2.set_tree_context([stage3], 'process', stage_name='stage2')
    stage3.set_tree_context([], 'process', stage_name='stage3')
    stage4.set_tree_context([], 'process', stage_name='stage4')

    stage1.add_retry_exceptions(TypeError)
    stage2.add_retry_exceptions(ValueError)

    # 初始化 TaskTree
    tree = TaskTree(root_stage = stage1)
    tree.set_reporter(True, host="127.0.0.1", port=5005)

    # 要测试的任务列表
    test_task_0 = range(25, 37)
    test_task_1 = list(range(25, 32)) + [0, 27, None, 0, '']
    # test_task_2 = (item for item in test_task_1)

    # 开始任务链
    result = tree.test_methods({
        stage1.get_stage_tag(): test_task_0,
    })
    test_table_list, execution_modes, stage_modes, index_header = result["Time table"]
    result["Time table"] = format_table(test_table_list, column_names = execution_modes, row_names = stage_modes, index_header = index_header)
    for key, value in result.items():
        if isinstance(value, dict):
            value = pprint.pformat(value)
        logging.info(f"{key}: \n{value}")

def _test_task_tree_1():
    # 定义任务节点
    A = TaskManager(func=sleep_random_A, execution_mode='thread')
    B = TaskManager(func=sleep_random_B, execution_mode='serial')
    C = TaskManager(func=sleep_random_C, execution_mode='serial')
    D = TaskManager(func=sleep_random_D, execution_mode='thread')
    E = TaskManager(func=sleep_random_E, execution_mode='thread')
    F = TaskManager(func=sleep_random_F, execution_mode='serial')

    # 设置链式上下文
    A.set_tree_context(next_stages=[B, C], stage_mode='process', stage_name="Stage_A")
    B.set_tree_context(next_stages=[D, F], stage_mode='process', stage_name="Stage_B")
    C.set_tree_context(next_stages=[], stage_mode='process', stage_name="Stage_C")
    D.set_tree_context(next_stages=[E], stage_mode='process', stage_name="Stage_D")
    E.set_tree_context(next_stages=[], stage_mode='process', stage_name="Stage_E")
    F.set_tree_context(next_stages=[], stage_mode='process', stage_name="Stage_F")

    # 初始化 TaskTree, 并设置根节点
    tree = TaskTree(A)
    tree.set_reporter(True, host="127.0.0.1", port=5005)

    input_tasks = {
        A.get_stage_tag(): range(10),
    }

    # 开始任务链
    result = tree.test_methods(input_tasks)
    test_table_list, execution_modes, stage_modes, index_header = result["Time table"]
    result["Time table"] = format_table(test_table_list, column_names = execution_modes, row_names = stage_modes, index_header = index_header)
    for key, value in result.items():
        if isinstance(value, dict):
            value = pprint.pformat(value)
        logging.info(f"{key}: \n{value}")

def _test_task_tree_2():    
    # 定义任务节点
    generate_stage = TaskManager(func=generate_urls, execution_mode='thread', worker_limit=4)
    logr_stage = TaskManager(func=log_urls, execution_mode='thread', worker_limit=4)
    splitter = TaskSplitter()
    download_stage = TaskManager(func=download, execution_mode='thread', worker_limit=4)
    parse_stage = TaskManager(func=parse, execution_mode='thread', worker_limit=4)

    # 设置链关系
    generate_stage.set_tree_context([logr_stage, splitter], stage_mode='process', stage_name='GenURLs')
    logr_stage.set_tree_context([], stage_mode='process', stage_name='Loger')
    splitter.set_tree_context([download_stage, parse_stage], stage_mode='process', stage_name='Splitter')
    download_stage.set_tree_context([], stage_mode='process', stage_name='Downloader')
    parse_stage.set_tree_context([], stage_mode='process', stage_name='Parser')

    # 初始化 TaskTree
    tree = TaskTree(generate_stage)

    # 测试输入：生成不同 URL 的任务
    input_tasks = {
        generate_stage.get_stage_tag(): range(10),
    }
    stage_modes = ['serial', 'process']
    execution_modes = ['serial', 'thread']

    result = tree.test_methods(input_tasks, stage_modes, execution_modes)
    test_table_list, execution_modes, stage_modes, index_header = result["Time table"]
    result["Time table"] = format_table(test_table_list, column_names = execution_modes, row_names = stage_modes, index_header = index_header)

    for key, value in result.items():
        if isinstance(value, dict):
            value = pprint.pformat(value)
        logging.info(f"{key}: \n{value}")

def test_task_web_3():
    # 定义任务节点
    generate_stage = TaskManager(func=generate_urls_sleep, execution_mode='thread', worker_limit=4)
    logr_stage = TaskManager(func=log_urls_sleep, execution_mode='thread', worker_limit=4)
    splitter = TaskSplitter()
    download_stage = TaskManager(func=download_sleep, execution_mode='thread', worker_limit=4)
    parse_stage = TaskManager(func=parse_sleep, execution_mode='thread', worker_limit=4)

    # 设置链关系
    generate_stage.set_tree_context([logr_stage, splitter], stage_mode='process', stage_name='GenURLs')
    logr_stage.set_tree_context([], stage_mode='process', stage_name='Loger')
    splitter.set_tree_context([download_stage, parse_stage], stage_mode='process', stage_name='Splitter')
    download_stage.set_tree_context([], stage_mode='process', stage_name='Downloader')
    parse_stage.set_tree_context([], stage_mode='process', stage_name='Parser')

    # download_stage.add_retry_exceptions(ValueError)

    # 初始化 TaskTree
    tree = TaskTree(generate_stage)
    tree.set_reporter(True, host="127.0.0.1", port=5005)

    tree.start_tree({
        generate_stage.get_stage_tag(): range(10),
        # logr_stage.get_stage_tag(): tuple([f"url_{x}_{i}" for i in range(random.randint(1, 4)) for x in range(10, 15)]),
        # splitter.get_stage_tag(): tuple([f"url_{x}_{i}" for i in range(random.randint(1, 4)) for x in range(10, 15)]),
        download_stage.get_stage_tag(): [f"url_{x}_5" for x in range(10, 20)],
        parse_stage.get_stage_tag(): [f"url_{x}_5" for x in range(10, 20)],
    }, False)
    
def profile_task_tree():
    target_func = 'test_task_tree_1'
    now_time = strftime("%m-%d-%H-%M", localtime())
    output_file = f'profile/{target_func}({now_time}).prof'
    cProfile.run(target_func + '()', output_file)

    subprocess.run(['snakeviz', output_file])

# 在主函数或脚本中调用此函数，而不是在测试中
if __name__ == "__main__":
    # test_task_tree_2()
    # _test_task_web_3()
    pass