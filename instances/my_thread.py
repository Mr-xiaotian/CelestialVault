# -*- coding: utf-8 -*-
#版本 2.10
#作者：晓天, GPT-4
#时间：30/7/2023

# We import the necessary modules
import sys
import asyncio
import traceback
from queue import Queue
from threading import Thread
from multiprocessing import Process, Queue as MPQueue
from tqdm import tqdm
from time import time, strftime, localtime
from loguru import logger
from tqdm.asyncio import tqdm as tqdm_asy

# Configure logging
logger.remove()  # remove the default handler
now_time = strftime("%Y-%m-%d", localtime())
logger.add(f"logs/thread_manager({now_time}).log", 
           format="{time:YYYY-MM-DD HH:mm:ss} {level} {message}", 
           level="INFO")

# We redefine the ThreadWorker class
class ThreadWorker(Thread):
    def __init__(self, func, args, result_queue=None, task=None):
        """
        初始化 ThreadWorker

        参数:
        func: 可调用对象
        args: 可调用对象的参数
        result_queue: 存储处理结果的队列
        task: 任务对象
        """
        super().__init__()
        self.func = func
        self.args = args
        self.result_queue = result_queue
        self.task = task
        self.exception = None
        self.exc_traceback = ""

    def run(self):
        """
        运行线程，并将结果存储在结果队列中
        """
        try:
            self.result = self.func(*self.args)
            if self.result_queue is not None:
                self.result_queue.put({self.task: self.result})
        except Exception as e:
            self.exception = e
            self.exc_traceback = "".join(
                traceback.format_exception(*sys.exc_info())
                )
            
    def get_result(self):
        """
        获取结果
        """
        return self.result

    def get_exception(self):
        """
        获取异常信息
        """
        return self.exception
    
    def get_exc_traceback(self):
        """
        获取异常堆栈信息
        """
        return self.exc_traceback
    

class ProcessWorker(Process):
    def __init__(self, func, args, result_queue=None, task=None):
        """
        初始化 ProcessWorker
        
        参数:
        func: 可调用对象
        args: 可调用对象的参数
        result_queue: 存储处理结果的队列
        task: 任务对象
        """
        super().__init__()
        self.func = func
        self.args = args
        self.result_queue = result_queue
        self.task = task
        self.result = None  # Explicitly define the result attribute
        self.exception = None
        self.exc_traceback = ""

    def run(self):
        """
        运行进程，并将结果存储在结果队列中
        """
        try:
            self.result = self.func(*self.args)
            if self.result_queue is not None:
                self.result_queue.put({self.task: self.result})
        except Exception as e:
            self.exception = e
            self.exc_traceback = "".join(traceback.format_exception(*sys.exc_info()))

    def get_result(self):
        return self.result

    def get_exception(self):
        return self.exception

    def get_exc_traceback(self):
        return self.exc_traceback


class ThreadManager:
    def __init__(self, func, pool=None, thread_num=50, max_retries=3, max_info=50,
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
        self.max_info = max_info

        self.set_start()

        self.tqdm_desc = tqdm_desc
        self.show_progress = show_progress

    def set_start(self):
        self.result_queue = Queue()
        self.dictory_queue = Queue()

        self.result_dict = {}
        self.error_list = []
        self.error_dict = {}
        self.retry_time_dict = {}

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
    
    def get_task_info(self, task):
        """
        获取任务信息
        """
        info_list = []
        for arg in self.get_args(task):
            arg = f'{arg}'
            if len(arg) < self.max_info:
                info_list.append(f"{arg}")
            else:
                info_list.append(f"{arg[:self.max_info]}...")
        return "(" + ", ".join(info_list) + ")"
    
    def get_result_info(self, result):
        """
        获取结果信息
        """
        result = f"{result}"
        if len(result) < self.max_info:
            return result
        else:
            return f"{result[:self.max_info]}..."
        
    def start(self, dictory, start_type="serial"):
        """
        根据 start_type 的值，选择串行、并行、异步或多进程执行任务

        参数:
        dictory: 任务列表
        start_type: 启动类型，可以是 'serial'、'parallel' 'async' 或 'multiprocessing'
        """
        self.set_start()
        logger.info(f"'{self.func.__name__}' start {len(dictory)} tasks by {start_type}.")

        # Convert dictory to a Queue
        for item in dictory:
            self.dictory_queue.put(item)
            self.retry_time_dict[item] = 0
    
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
            elif start_type == "multiprocessing":
                self.run_in_multiprocessing(chunk)
            else:
                self.run_in_serial(chunk)

    async def start_async(self, dictory):
        """
        异步地执行任务

        参数:
        dictory: 任务列表
        """
        self.set_start()
        logger.info(f"'{self.func.__name__}' start {len(dictory)} tasks by async(await).")

        # Convert dictory to a Queue
        for item in dictory:
            self.dictory_queue.put(item)
            self.retry_time_dict[item] = 0

        while not self.dictory_queue.empty():
            chunk = []
            for _ in range(
                min(self.thread_num, self.dictory_queue.qsize())
                ):
                chunk.append(self.dictory_queue.get())
            await self.run_in_async(chunk)
 
    def run_in_serial(self, dictory):
        """
        串行地执行任务

        参数:
        dictory: 任务列表
        """
        progress_bar = tqdm(total=len(dictory), desc=self.tqdm_desc) if self.show_progress else None
        for num,d in enumerate(dictory):
            try:
                start_time = time.time()
                result = self.func(*self.get_args(d))
                self.result_dict[d] = result
            except Exception as e:
                if self.retry_time_dict[d] < self.max_retries:
                    self.dictory_queue.put(d)
                    self.retry_time_dict[d] += 1
                    logger.warning(f"Task {self.get_task_info(d)} failed {self.retry_time_dict[d]} times and try again.")
                else:
                    self.error_list.append(d)
                    self.error_dict[d] = e
                    logger.error(f"Task {self.get_task_info(d)} failed and reached the retry limit.")
            else:
                logger.success(f"Task {self.get_task_info(d)} completed by serial. Result is {self.get_result_info(result)}. Used {time.time() - start_time: .2f} seconds.")
            progress_bar.update(1) if self.show_progress else None

        progress_bar.close() if self.show_progress else None
    
    def run_in_parallel(self, dictory):
        """
        并行地执行任务

        参数:
        dictory: 任务列表
        """
        threads = []
        start_time = time.time()
        for d in dictory:
            thread = ThreadWorker(self.func, self.get_args(d), 
                                  self.result_queue, d)
            threads.append(thread)
            thread.start()

        progress_bar = tqdm(total=len(dictory), desc=self.tqdm_desc) if self.show_progress else None
        for thread, d in zip(threads, dictory):
            thread.join()
            if thread.get_exception() is not None:
                if self.retry_time_dict[d] < self.max_retries:
                    self.dictory_queue.put(d)
                    self.retry_time_dict[d] += 1
                    logger.warning(f"Task {self.get_task_info(d)} failed {self.retry_time_dict[d]} times and try again.")
                else:
                    self.error_list.append(d)
                    self.error_dict[d] = thread.get_exception()
                    logger.error(f"Task {self.get_task_info(d)} failed and reached the retry limit.")
            else:
                result = thread.get_result()
                logger.success(f"Task {self.get_task_info(d)} completed by parallel. Result is {self.get_result_info(result)}. Used {time.time() - start_time: .2f} seconds.")
            progress_bar.update(1) if self.show_progress else None

        progress_bar.close() if self.show_progress else None
                
    async def run_in_async(self, dictory):
        """
        异步地执行任务

        参数:
        dictory: 任务列表
        """
        tasks = []
        start_time = time.time()
        for d in dictory:
            task = asyncio.create_task(self.func(*self.get_args(d)))
            tasks.append(task)

        progress_bar = tqdm_asy(total=len(dictory), desc=self.tqdm_desc) if self.show_progress else None
        for task, d in zip(tasks, dictory):
            try:
                result = await task
                self.result_dict[d] = result
            except Exception as e:
                if self.retry_time_dict[d] < self.max_retries:
                    self.dictory_queue.put(d)
                    self.retry_time_dict[d] += 1
                    logger.warning(f"Task {task} failed {self.retry_time_dict[d]} times and try again.")
                else:
                    self.error_list.append(d)
                    self.error_dict[d] = e
                    logger.error(f"Task {task} failed and reached the retry limit.")
            else:
                logger.success(f"Task {task} completed by async. Result is {self.get_result_info(result)}. Used {time.time() - start_time: .2f} seconds.")
            progress_bar.update(1) if self.show_progress else None

        progress_bar.close() if self.show_progress else None

    def run_in_multiprocessing(self, dictory):
        """
        多进程地执行任务
        
        参数:
        dictory: 任务列表
        """
        processes = []
        result_queue = MPQueue()
        start_time = time.time()

        for d in dictory:
            process = ProcessWorker(self.func, self.get_args(d), result_queue, d)
            processes.append(process)
            process.start()

        progress_bar = tqdm(total=len(dictory), desc=self.tqdm_desc) if self.show_progress else None
        for process in processes:
            process.join()
            progress_bar.update(1) if self.show_progress else None
        progress_bar.close() if self.show_progress else None

        while not result_queue.empty():
            result = result_queue.get()
            for task, output in result.items():
                if isinstance(output, Exception):
                    if self.retry_time_dict[task] < self.max_retries:
                        self.dictory_queue.put(task)
                        self.retry_time_dict[task] += 1
                        logger.warning(f"Task {self.get_task_info(task)} failed {self.retry_time_dict[task]} times and try again.")
                    else:
                        self.error_list.append(task)
                        self.error_dict[task] = output
                        logger.error(f"Task {self.get_task_info(task)} failed and reached the retry limit.")
                else:
                    logger.success(f"Task {self.get_task_info(task)} completed by multiprocessing. Result is {self.get_result_info(output)}. Used {time.time() - start_time: .2f} seconds.")
                    self.result_dict[task] = output
            
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
        获取错误字典
        """
        return self.error_dict
    
    def test_methods(self, dictory):
        # Prepare the results dictionary
        results = {}

        # Test run_in_serial
        start = time()
        self.start(dictory, 'serial')
        results['run_in_serial  '] = time() - start

        # Test run_in_parallel
        start = time()
        self.start(dictory, 'parallel')
        results['run_in_parallel'] = time() - start

        # # Test run_in_async
        # start = time()
        # self.start(dictory, 'async')
        # results['run_in_async   '] = time() - start

        # Test run_in_multiprocessing
        start = time()
        self.start(dictory, 'multiprocessing')
        results['run_in_multiprocessing'] = time() - start

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
            # print(f"Task {self.get_task_info(task)}: {self.get_result_info(result)}")
            logger.info(f"Task {self.get_task_info(task)}: {self.get_result_info(result)}")

    def handle_error(self):
        """
        处理错误

        在这个示例中，我们只是简单地打印错误信息
        """
        if not self.get_error_list():
            return
        error_dict = self.get_error_dict()
        error_len = len(error_dict)
        for num,(task, error) in enumerate(error_dict.items()):
            # print(f"Error in Task {self.get_task_info(task)}(index:{num}/{error_len}):\n{error}\n")
            logger.error(f"Task {self.get_task_info(task)}(index:{num+1}/{error_len}): {error}")
