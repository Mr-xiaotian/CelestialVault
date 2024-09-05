# -*- coding: utf-8 -*-
#版本 2.30
#作者：晓天, GPT-4
#时间：4/9/2024
#Github: https://github.com/Mr-xiaotian


import asyncio, multiprocessing
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

    def set_process_mode(self, process_mode):
        self.process_mode = process_mode

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
        self.init_env()
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
        self.set_process_mode('async')
        self.init_env()
        logger.info(f"'{self.func.__name__}' start {len(dictory)} tasks by async(await).")

        for item in dictory:
            await self.task_queue.put(item)
            self.retry_time_dict[item] = 0

        while not self.task_queue.empty():
            await self.run_in_async()

    def start_stage(self, input_queue, output_queue, error_dict):
        """
        根据 start_type 的值，选择串行、并行、异步或多进程执行任务

        参数:
        dictory: 任务列表
        """
        self.init_env()
        logger.info(f"'{self.func.__name__}' start {input_queue.qsize()} tasks by {self.process_mode}.")

        self.task_queue = input_queue
        self.result_queue = output_queue
        self.error_dict = error_dict

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
 
    def run_in_serial(self):
        """
        串行地执行任务
        """
        progress_bar = tqdm(total=self.task_queue.qsize(), desc=f'{self.tqdm_desc}(serial)') if self.show_progress else None
        start_time = time()

        # 从队列中依次获取任务并执行
        while not self.task_queue.empty():
            task = self.task_queue.get()
            try:
                result = self.func(*self.get_args(task))
                self.result_dict[task] = result
                self.result_queue.put(result)
                logger.success(f"Task {self.get_task_info(task)} completed by serial. Result is {self.get_result_info(result)}. Used {time() - start_time: .2f} seconds.")
            except Exception as error:
                self.handle_task_exception(task, error)
            progress_bar.update(1) if self.show_progress else None

        progress_bar.close() if self.show_progress else None
    
    def run_in_parallel(self):
        """
        并行地执行任务
        """
        start_time = time()
        
        # 使用已经存在的线程池 self.thread_pool
        futures = {}
        progress_bar = tqdm(total=self.task_queue.qsize(), desc=f'{self.tqdm_desc}(parallel)') if self.show_progress else None

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
                self.result_queue.put(result)
                logger.success(f"Task {self.get_task_info(task)} completed by parallel. Result is {self.get_result_info(result)}. Used {time() - start_time: .2f} seconds.")
            except Exception as error:
                self.handle_task_exception(task, error)
                # 动态更新进度条总数
                if self.show_progress:
                    progress_bar.total += 1
                    progress_bar.refresh()
            progress_bar.update(1) if self.show_progress else None

        progress_bar.close() if self.show_progress else None

    def run_in_multiprocessing(self):
        """
        多进程地执行任务
        """
        start_time = time()

        # 使用已经存在的进程池 self.process_pool
        futures = {}
        progress_bar = tqdm(total=self.task_queue.qsize(), desc=f'{self.tqdm_desc}(multiprocessing)') if self.show_progress else None

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
                self.result_queue.put(result)
                logger.success(f"Task {self.get_task_info(task)} completed by multiprocessing. Result is {self.get_result_info(result)}. Used {time() - start_time: .2f} seconds.")
            except Exception as error:
                self.handle_task_exception(task, error)
            progress_bar.update(1) if self.show_progress else None

        progress_bar.close() if self.show_progress else None
                
    async def run_in_async(self):
        """
        异步地执行任务
        """
        start_time = time()

        # 创建异步任务列表
        async_tasks = []
        progress_bar = tqdm_asy(total=self.task_queue.qsize(), desc=f'{self.tqdm_desc}(async)') if self.show_progress else None

        # 从任务队列中获取任务并加入异步任务列表
        while not self.task_queue.empty():
            task = await self.task_queue.get()  # 从异步队列获取任务
            async_tasks.append(self.func(*self.get_args(task)))

        # 并发运行所有任务
        for task_data, result in zip(async_tasks, await asyncio.gather(*async_tasks, return_exceptions=True)):
            if isinstance(result, Exception):
                self.handle_task_exception(task_data, result)
            else:
                self.result_dict[task_data] = result
                self.result_queue.put(result)
                logger.success(f"Task {task_data} completed by async. Result is {self.get_result_info(result)}. Used {time() - start_time: .2f} seconds.")
            progress_bar.update(1) if self.show_progress else None

        progress_bar.close() if self.show_progress else None
            
    def get_result_dict(self):
        """
        获取结果字典
        """
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
        self.set_process_mode('serial')
        self.start(dictory)
        results['run_in_serial'] = time() - start

        # Test run_in_parallel
        start = time()
        self.set_process_mode('parallel')
        self.start(dictory)
        results['run_in_parallel'] = time() - start

        # Test run_in_multiprocessing
        start = time()
        self.set_process_mode('multiprocessing')
        self.start(dictory)
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

class TaskChain:
    def __init__(self, stages):
        """
        stages: 一个包含 StageManager 实例的列表，表示执行链
        """
        self.stages: TaskManager = stages

    def start_chain(self, tasks):
        # 创建进程间的队列和一个共享的字典来记录错误
        queues = [MPQueue() for _ in range(len(self.stages) + 1)]
        manager = multiprocessing .Manager()
        error_dict = manager.dict()
        
        # 向第一个队列添加初始任务
        for task in tasks:
            queues[0].put(task)
        
        # 创建多进程来运行每个环节
        processes = []
        for i, stage in enumerate(self.stages):
            p = multiprocessing.Process(target=self.run_stage, args=(stage, queues[i], queues[i + 1], error_dict))
            p.start()
            processes.append(p)
        
        # 等待所有进程结束
        for p in processes:
            p.join()
        
        # 从最后的队列中收集结果
        results = []
        while not queues[-1].empty():
            results.append(queues[-1].get())
        
        # 检查是否有错误
        if error_dict:
            logger.error(f"Errors encountered in TaskChain: {error_dict}")
        
        return results

    def run_stage(self, stage, input_queue, output_queue, error_dict):
        try:
            stage.start_stage(input_queue, output_queue)
        except Exception as e:
            error_dict[stage] = str(e)