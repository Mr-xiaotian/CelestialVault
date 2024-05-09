# -*- coding: utf-8 -*-
#版本 2.10
#作者：晓天, GPT-4
#时间：30/7/2023

# We import the necessary modules
import sys
import asyncio
import traceback
from time import time
from loguru import logger
from queue import Queue
from threading import Thread
from tqdm import tqdm
from tqdm.asyncio import tqdm as tqdm_asy

# Configure logging
logger.remove()  # remove the default handler
logger.add("thread_manager.log", format="{time} {level} {message}")

# We redefine the ThreadWorker class
class ThreadWorker(Thread):
    def __init__(self, func, args, result_queue=None, task=None, new_task_queue=None):
        """
        初始化 ThreadWorker

        参数:
        func: 可调用对象
        args: 可调用对象的参数
        result_queue: 存储处理结果的队列
        task: 任务对象
        new_task_queue: 存储新任务的队列
        """
        super().__init__()
        self.func = func
        self.args = args
        self.result_queue = result_queue
        self.task = task
        self.new_task_queue = new_task_queue
        self.exception = None
        self.exc_traceback = ""

    def run(self):
        """
        运行线程，并将结果存储在结果队列中
        """
        try:
            result = self.func(*self.args)
            if self.result_queue is not None:
                self.result_queue.put({self.task: result})
            # if isinstance(result, list) and self.new_task_queue is not None:
            #     for new_task in result:
            #         self.new_task_queue.put(new_task)
        except Exception as e:
            self.exception = e
            self.exc_traceback = "".join(
                traceback.format_exception(*sys.exc_info())
                )


    def get_exception(self):
        """
        获取异常信息
        """
        return self.exception, self.exc_traceback


# We redefine the ThreadManager class
class ThreadManager:
    def __init__(self, func, pool=None, thread_num=50, max_retries=3, 
                 tqdm_desc="Processing", show_progress=False):
        """
        初始化 ThreadManager

        参数:
        func: 可调用对象
        pool: 线程池（未在代码中使用）
        thread_num: 线程数量
        max_retries: 任务的最大重试次数
        tqdm_desc: 进度条显示名称
        show_progress: 进度条显示与否
        """
        self.func = func
        self.pool = pool
        self.thread_num = thread_num
        self.max_retries = max_retries

        self.set_start()

        self.tqdm_desc = tqdm_desc
        self.show_progress = show_progress

    def set_start(self):
        self.result_queue = Queue()
        self.new_task_queue = Queue()
        self.dictory_queue = Queue()

        self.result_dict = {}
        self.error_list = []
        self.error_dict = {}
        self.retries_dict = {}

    def get_args(self, obj):
        """
        从 obj 中获取参数

        这是一个抽象方法，需要由子类实现
        """
        raise NotImplementedError("This method should be overridden")

    def process_result(self):
        """
        从结果队列中获取结果，并进行处理

        这是一个抽象方法，需要由子类实现
        """
        raise NotImplementedError("This method should be overridden")

    def handle_error(self):
        """
        处理错误

        这是一个抽象方法，需要由子类实现
        """
        raise NotImplementedError("This method should be overridden")

    def start(self, dictory, start_type="serial"):
        """
        根据 start_type 的值，选择串行、并行或异步执行任务

        参数:
        dictory: 任务列表
        start_type: 启动类型，可以是 'serial'、'parallel' 或 'async'
        """
        self.set_start()
        logger.info(f"{__name__} desk prepare start by {start_type}.")

        # Convert dictory to a Queue
        for item in dictory:
            self.dictory_queue.put(item)
            self.retries_dict[item] = 0
    
        while not self.dictory_queue.empty():
            chunk = []
            for _ in range(
                min(self.thread_num, self.dictory_queue.qsize())
                ):
                chunk.append(self.dictory_queue.get())
            if start_type == "parallel":
                self.run_in_parallel(chunk)
            elif start_type == "async":
                # 建议直接使用start_async
                asyncio.run(self.run_in_async(chunk))
            else:
                self.run_in_serial(chunk)

    async def start_async(self, dictory):
        """
        异步地执行任务

        参数:
        dictory: 任务列表
        """
        self.set_start()
        logger.info(f"{__name__} desk prepare start by async(await).")

        # Convert dictory to a Queue
        for item in dictory:
            self.dictory_queue.put(item)
            self.retries_dict[item] = 0

        while not self.dictory_queue.empty():
            chunk = []
            for _ in range(
                min(self.thread_num, self.dictory_queue.qsize())
                ):
                chunk.append(self.dictory_queue.get())
            await self.run_in_async(chunk)
 
    def run_in_parallel(self, dictory):
        """
        并行地执行任务

        参数:
        dictory: 任务列表
        """
        threads = []
        for d in dictory:
            thread = ThreadWorker(self.func, self.get_args(d), 
                                  self.result_queue, d, self.new_task_queue)
            threads.append(thread)
            thread.start()

        progress_bar = tqdm(total=len(dictory), desc=self.tqdm_desc) if self.show_progress else None
        for thread, d in zip(threads, dictory):
            thread.join()
            if thread.get_exception()[0] is not None:
                if self.retries_dict[d] < self.max_retries:
                    self.dictory_queue.put(d)
                    self.retries_dict[d] += 1
                    logger.info(f"Task {thread} failed and has been requeued.")
                else:
                    self.error_list.append(d)
                    self.error_dict[d] = thread.get_exception()
                    logger.info(f"Task {thread} failed and reached the retry limit.")
            else:
                logger.info(f"Task {thread} completed successfully.")
            progress_bar.update(1) if self.show_progress else None

        progress_bar.close() if self.show_progress else None

    def run_in_serial(self, dictory):
        """
        串行地执行任务

        参数:
        dictory: 任务列表
        """
        progress_bar = tqdm(total=len(dictory), desc=self.tqdm_desc) if self.show_progress else None
        for d in dictory:
            try:
                result = self.func(*self.get_args(d))
                self.result_dict[d] = result
                # if isinstance(result, list):
                #     for new_task in result:
                #         self.new_task_queue.put(new_task)
            except Exception as e:
                if self.retries_dict[d] < self.max_retries:
                    self.dictory_queue.put(d)
                    self.retries_dict[d] += 1
                    logger.info(f"Task failed and has been requeued.")
                else:
                    self.error_list.append(d)
                    self.error_dict[d] = "".join(
                        traceback.format_exception(*sys.exc_info())
                        )
                    logger.info(f"Task failed and reached the retry limit.")
            else:
                logger.info(f"Task completed successfully.")
            progress_bar.update(1) if self.show_progress else None

        progress_bar.close() if self.show_progress else None
                

    async def run_in_async(self, dictory):
        """
        异步地执行任务

        参数:
        dictory: 任务列表
        """
        tasks = []
        for d in dictory:
            task = asyncio.create_task(self.func(*self.get_args(d)))
            tasks.append(task)

        progress_bar = tqdm_asy(total=len(dictory), desc=self.tqdm_desc) if self.show_progress else None
        for task, d in zip(tasks, dictory):
            try:
                result = await task
                self.result_dict[d] = result
                # if isinstance(result, list):
                #     for new_task in result:
                #         self.new_task_queue.put(new_task)
            except Exception as e:
                if self.retries_dict[d] < self.max_retries:
                    self.dictory_queue.put(d)
                    self.retries_dict[d] += 1
                    logger.info(f"Task {task} failed and has been requeued.")
                else:
                    self.error_list.append(d)
                    self.error_dict[d] = "".join(
                        traceback.format_exception(*sys.exc_info())
                        )
                    logger.info(f"Task {task} failed and reached the retry limit.")
            else:
                logger.info(f"Task {task} completed successfully.")
            progress_bar.update(1) if self.show_progress else None

        progress_bar.close() if self.show_progress else None

    def get_result_dict(self):
        """
        获取结果字典
        """
        while not self.result_queue.empty():
            self.result_dict.update(self.result_queue.get())
        return self.result_dict

    def get_error_list(self):
        """
        获取错误列表
        """
        return self.error_list
    
    def get_error_dict(self):
        """
        获取错误列表
        """
        return self.error_dict
    
    def test_methods(self, dictory):
        # Prepare the results dictionary
        results = {}

        # Test run_in_serial
        start = time()
        self.run_in_serial(dictory)
        results['run_in_serial  '] = time() - start

        # Test run_in_parallel
        start = time()
        self.run_in_parallel(dictory)
        results['run_in_parallel'] = time() - start

        # Test run_in_async
        start = time()
        asyncio.run(self.run_in_async(dictory))
        results['run_in_async   '] = time() - start

        # Return the results
        return results


# As an example of use, we redefine the subclass of ThreadManager
class ExampleThreadManager(ThreadManager):
    def get_args(self, obj):
        """
        从 obj 中获取参数

        在这个示例中，我们假设 obj 是一个整数，并将其作为参数返回
        """
        return (obj,)

    def process_result(self):
        """
        从结果队列中获取结果，并进行处理

        在这个示例中，我们只是简单地打印结果
        """
        result_dict = self.get_result_dict()
        for task, result in result_dict.items():
            print(f"Task {task}: {result}")

    def handle_error(self):
        """
        处理错误

        在这个示例中，我们只是简单地打印错误信息
        """
        if not self.get_error_list():
            return
        error_dict = self.error_dict
        for num,(d, error) in enumerate(error_dict.items()):
            print(f"Error in task {num}:\n{error}\nTask: {d[0]}")
            self.result_dict[d] = 'None'

async def generate_new_tasks(n):
    return [i for i in range(n, n+5)]


if __name__ == "__main__":
    # We instantiate the ThreadManager
    manager = ExampleThreadManager(generate_new_tasks, thread_num=10, 
                                   show_progress=False)

    # We start the threads
    manager.start(range(100), start_type="parallel")

    # # We process the results
    # manager.process_result()

    # # We handle the errors
    # manager.handle_error()

    # Assuming dictory is the list of tasks you want to test
    from pprint import pprint
    results = manager.test_methods(range(10))
    pprint(results)

