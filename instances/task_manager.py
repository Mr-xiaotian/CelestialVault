# -*- coding: utf-8 -*-
#版本 2.30
#作者：晓天, GPT-4
#时间：4/9/2024
#Github: https://github.com/Mr-xiaotian


import asyncio
from queue import Queue as ThreadQueue
from multiprocessing import Queue as MPQueue
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from tqdm import tqdm
from time import time, strftime, localtime
from loguru import logger
from tqdm.asyncio import tqdm as tqdm_asy


logger.remove()  # remove the default handler
now_time = strftime("%Y-%m-%d", localtime())
logger.add(f"logs/thread_manager({now_time}).log",
           format="{time:YYYY-MM-DD HH:mm:ss} {level} {message}", 
           level="INFO")


class TaskManager:
    def __init__(self, func, process_mode = 'serial',
                 thread_num=50, max_retries=3, max_info=50,
                 tqdm_desc="Processing", show_progress=False):
        """
        初始化 TaskManager

        参数:
        func: 可调用对象
        thread_num: 线程数量
        max_retries: 任务的最大重试次数
        tqdm_desc: 进度条显示名称
        show_progress: 进度条显示与否
        """
        self.func = func
        self.process_mode = process_mode
        self.thread_num = thread_num
        self.max_retries = max_retries
        self.max_info = max_info

        self.tqdm_desc = tqdm_desc
        self.show_progress = show_progress

    def init_env(self):
        if self.process_mode == "async":
            self.task_queue = asyncio.Queue()
        elif self.process_mode == "multiprocessing":
            self.task_queue = MPQueue()
        else:
            self.task_queue = ThreadQueue()

        self.result_queue = ThreadQueue()
        self.result_dict = {}
        self.error_dict = {}
        self.retry_time_dict = {}

        self.thread_pool = None
        self.process_pool = None

        # 可以复用的线程池或进程池
        if self.process_mode == 'parallel':
            self.thread_pool = ThreadPoolExecutor(max_workers=self.thread_num)
        elif self.process_mode == 'multiprocessing':
            self.process_pool = ProcessPoolExecutor(max_workers=self.thread_num)

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
        
    def handle_task_exception(self, task, exception):
        """
        统一处理任务异常

        参数:
        task: 发生异常的任务
        exception: 捕获的异常
        """
        if self.retry_time_dict[task] < self.max_retries:
            self.task_queue.put(task)
            self.retry_time_dict[task] += 1
            logger.warning(f"Task {self.get_task_info(task)} failed {self.retry_time_dict[task]} times and will retry.")
        else:
            self.error_dict[task] = exception
            logger.error(f"Task {self.get_task_info(task)} failed and reached the retry limit: {exception}")
        
    def start(self, dictory):
        """
        根据 start_type 的值，选择串行、并行、异步或多进程执行任务

        参数:
        dictory: 任务列表
        """
        self.init_env(self.process_mode)
        logger.info(f"'{self.func.__name__}' start {len(dictory)} tasks by {self.process_mode}.")

        for item in dictory:
            self.task_queue.put(item)
            self.retry_time_dict[item] = 0

        # 根据模式运行对应的任务处理函数
        while not self.task_queue.empty():
            if self.process_mode == "parallel":
                self.run_in_parallel()
            elif self.process_mode == "multiprocessing":
                self.run_in_multiprocessing()
            elif self.process_mode == "async":
                asyncio.run(self.run_in_async())
            else:
                self.run_in_serial()

        self.shutdown_pools()

    async def start_async(self, dictory):
        """
        异步地执行任务

        参数:
        dictory: 任务列表
        """
        self.init_env('async')
        logger.info(f"'{self.func.__name__}' start {len(dictory)} tasks by async(await).")

        for item in dictory:
            await self.task_queue.put(item)
            self.retry_time_dict[item] = 0

        self.chunk_index = 0
        while not self.task_queue.empty():
            chunk = []
            for _ in range(min(self.thread_num, self.task_queue.qsize())):
                chunk.append(await self.task_queue.get())  # 使用 await 从队列获取任务
            await self.run_in_async(chunk)
            self.chunk_index += 1
 
    def run_in_serial(self, task_list):
        """
        串行地执行任务

        参数:
        task_list: 任务列表
        """
        progress_bar = tqdm(total=len(task_list), desc=f'{self.tqdm_desc}(serial)_{self.chunk_index}') if self.show_progress else None
        for task in task_list:
            try:
                start_time = time()
                result = self.func(*self.get_args(task))
                self.result_dict[task] = result
            except Exception as error:
                self.handle_task_exception(task, error)
            else:
                logger.success(f"Task {self.get_task_info(task)} completed by serial. Result is {self.get_result_info(result)}. Used {time() - start_time: .2f} seconds.")
            progress_bar.update(1) if self.show_progress else None

        progress_bar.close() if self.show_progress else None
    
    def run_in_parallel(self):
        """
        并行地执行任务
        """
        start_time = time()
        
        # 使用已经存在的线程池 self.thread_pool
        futures = {}
        progress_bar = tqdm(total=self.task_queue.qsize(), desc=f'{self.tqdm_desc}(parallel)_{self.chunk_index+1}') if self.show_progress else None

        # 从任务队列中提交任务到线程池
        while not self.task_queue.empty():
            task = self.task_queue.get()
            futures[self.thread_pool.submit(self.func, *self.get_args(task))] = task

        # 处理已完成的任务
        for future in as_completed(futures):
            task = futures[future]
            try:
                result = future.result()  # 获取任务结果
                self.result_dict[task] = result
                logger.success(f"Task {self.get_task_info(task)} completed by parallel. Result is {self.get_result_info(result)}. Used {time() - start_time: .2f} seconds.")
            except Exception as error:
                self.handle_task_exception(task, error)
            progress_bar.update(1) if self.show_progress else None

        progress_bar.close() if self.show_progress else None

    def run_in_multiprocessing(self):
        """
        多进程地执行任务
        """
        start_time = time()

        # 使用已经存在的进程池 self.process_pool
        futures = {}
        progress_bar = tqdm(total=self.task_queue.qsize(), desc=f'{self.tqdm_desc}(multiprocessing)_{self.chunk_index+1}') if self.show_progress else None

        # 从任务队列中提交任务到进程池
        while not self.task_queue.empty():
            task = self.task_queue.get()
            futures[self.process_pool.submit(self.func, *self.get_args(task))] = task

        # 处理已完成的任务
        for future in as_completed(futures):
            task = futures[future]
            try:
                result = future.result()  # 获取任务结果
                self.result_dict[task] = result
                logger.success(f"Task {self.get_task_info(task)} completed by multiprocessing. Result is {self.get_result_info(result)}. Used {time() - start_time: .2f} seconds.")
            except Exception as error:
                self.handle_task_exception(task, error)
            progress_bar.update(1) if self.show_progress else None

        progress_bar.close() if self.show_progress else None
                
    async def run_in_async(self, tasks_list):
        """
        异步地执行任务

        参数:
        tasks_list: 任务列表
        """
        start_time = time()

        # 使用 asyncio.gather 并发执行任务
        async_tasks = [self.func(*self.get_args(task_data)) for task_data in tasks_list]

        # 创建异步进度条
        progress_bar = tqdm_asy(total=len(tasks_list), desc=f'{self.tqdm_desc}(async)_{self.chunk_index}') if self.show_progress else None

        # 运行所有任务并处理结果
        for task_data, result in zip(tasks_list, await asyncio.gather(*async_tasks, return_exceptions=True)):
            if isinstance(result, Exception):
                self.handle_task_exception(task_data, result)
            else:
                self.result_dict[task_data] = result
                logger.success(f"Task {task_data} completed by async. Result is {self.get_result_info(result)}. Used {time() - start_time: .2f} seconds.")
            progress_bar.update(1) if self.show_progress else None

        progress_bar.close() if self.show_progress else None
            
    def get_result_dict(self):
        """
        获取结果字典
        """
        while not self.result_queue.empty():
            self.result_dict.update(self.result_queue.get())
        return self.result_dict
    
    def get_error_dict(self):
        """
        获取错误字典
        """
        return self.error_dict
    
    def shutdown_pools(self):
        """
        关闭线程池和进程池，释放资源
        """
        try:
            if self.thread_pool:
                self.thread_pool.shutdown(wait=True)
        except Exception as e:
            logger.error(f"Error during thread pool shutdown: {e}")

        try:
            if self.process_pool:
                self.process_pool.shutdown(wait=True)
        except Exception as e:
            logger.error(f"Error during process pool shutdown: {e}")
    
    def test_methods(self, dictory):
        # Prepare the results dictionary
        results = {}

        # Test run_in_serial
        start = time()
        self.start(dictory, 'serial')
        results['run_in_serial'] = time() - start

        # Test run_in_parallel
        start = time()
        self.start(dictory, 'parallel')
        results['run_in_parallel'] = time() - start

        # Test run_in_multiprocessing
        start = time()
        self.start(dictory, 'multiprocessing')
        results['run_in_multiprocessing'] = time() - start

        # # Test run_in_async
        # start = time()
        # self.start(dictory, 'async')
        # results['run_in_async'] = time() - start

        return results


# As an example of use, we redefine the subclass of TaskManager
class ExampleTaskManager(TaskManager):
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
            logger.info(f"Task {self.get_task_info(task)}: {self.get_result_info(result)}")

    def handle_error(self):
        """
        处理错误

        在这个示例中，我们只是简单地打印错误信息
        """
        if not self.get_error_dict():
            return
        error_dict = self.get_error_dict()
        error_len = len(error_dict)
        for num,(task, error) in enumerate(error_dict.items()):
            logger.error(f"Task {self.get_task_info(task)}(index:{num+1}/{error_len}): {error}")
