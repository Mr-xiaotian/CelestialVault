# -*- coding: utf-8 -*-
#版本 2.40
#作者：晓天, GPT-4
#时间：6/9/2024
#Github: https://github.com/Mr-xiaotian


import asyncio, multiprocessing
from queue import Queue as ThreadQueue
from multiprocessing import Queue as MPQueue
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import List
from time import time, strftime, localtime, sleep
from loguru import logger
from instances.inst_progress import ProgressManager


class TerminationSignal:
    """用于标记任务队列终止的哨兵对象"""
    pass
TERMINATION_SIGNAL = TerminationSignal()

class TaskLogger:
    def __init__(self, logger):
        self.logger = logger

        self.logger.remove()  # remove the default handler
        now_time = strftime("%Y-%m-%d", localtime())
        self.logger.add(f"logs/thread_manager({now_time}).log",
                format="{time:YYYY-MM-DD HH:mm:ss} {level} {message}", 
                level="INFO")
        
    def start_task(self, func_name, task_num, execution_mode):
        self.logger.info(f"'{func_name}' start {task_num} tasks by {execution_mode}.")

    def start_stage(self, stage_index, func_name, execution_mode):
        self.logger.info(f"The {stage_index} stage '{func_name}' start tasks by {execution_mode}. ")

    def end_task(self, func_name, execution_mode, use_time, success_num, failed_num, duplicated_num):
        self.logger.info(f"'{func_name}' end tasks by {execution_mode}. Use {use_time: .2f} second. {success_num} tasks successed, {failed_num} tasks failed, {duplicated_num} tasks duplicated.")

    def end_stage(self, stage_index, func_name, execution_mode, use_time, success_num, failed_num, duplicated_num):
        self.logger.info(f"The {stage_index} stage '{func_name}' end tasks by {execution_mode}. Use {use_time: .2f} second. {success_num} tasks successed, {failed_num} tasks failed, {duplicated_num} tasks duplicated.")
    
    def task_success(self, func_name, task_info, execution_mode, result_info, use_time):
        self.logger.success(f"In '{func_name}', Task {task_info} completed by {execution_mode}. Result is {result_info}. Used {use_time: .2f} seconds.")

    def task_retry(self, task_info, retry_times, delay_time):
        self.logger.warning(f"Task {task_info} failed {retry_times} times and will retry after {delay_time} seconds.")

    def task_fail(self, task_info, exception):
        self.logger.error(f"Task {task_info} failed and reached the retry limit: {exception}")
        
task_logger = TaskLogger(logger)

class TaskManager:
    def __init__(self, func, execution_mode = 'serial',
                 worker_limit=50, max_retries=3, max_info=50,
                 tqdm_desc="Processing", show_progress=False):
        """
        初始化 TaskManager

        参数:
        func: 可调用对象
        execution_mode: 执行模式，可选 'serial', 'thread', 'process', 'async'
        worker_limit: 同时处理数量
        max_retries: 任务的最大重试次数
        tqdm_desc: 进度条显示名称
        show_progress: 进度条显示与否
        """
        self.func = func
        self.execution_mode = execution_mode
        self.worker_limit = worker_limit
        self.max_retries = max_retries
        self.max_info = max_info

        self.tqdm_desc = tqdm_desc
        self.show_progress = show_progress

        self.thread_pool = None
        self.process_pool = None

        self.init_result_error_dict()
        
    def init_result_error_dict(self, result_dict=None, error_dict=None):
        self.result_dict = result_dict if result_dict is not None else {}
        self.error_dict = error_dict if error_dict is not None else {} 

    def init_env(self):
        if self.execution_mode == "async":
            self.task_queue = asyncio.Queue()
        elif self.execution_mode == "process":
            self.task_queue = MPQueue()
        else:
            self.task_queue = ThreadQueue()
        self.result_queue = ThreadQueue()

        self.retry_time_dict = {}
        self.duplicates_num = 0

        # 可以复用的线程池或进程池
        if self.execution_mode == 'thread' and self.thread_pool is None:
            self.thread_pool = ThreadPoolExecutor(max_workers=self.worker_limit)
        elif self.execution_mode == 'process' and self.process_pool is None:
            self.process_pool = ProcessPoolExecutor(max_workers=self.worker_limit)

    def set_execution_mode(self, execution_mode):
        self.execution_mode = execution_mode

    def is_duplicate(self, task):
        return task in self.result_dict or task in self.error_dict

    def get_args(self, task):
        """
        从任务对象中提取执行函数的参数。

        参数:
        task: 任务对象

        返回:
        包含执行函数所需参数的元组或列表。
        
        说明:
        这个方法必须在子类中实现。task 的具体结构依赖于子类的任务类型。
        """
        raise NotImplementedError("This method should be overridden")

    def process_result(self, task, result):
        """
        处理任务的结果。

        参数:
        task: 已完成的任务对象
        result: 任务的执行结果

        返回:
        处理后的结果。

        说明:
        这个方法必须在子类中实现。可以对结果进行格式化、存储或其他处理。
        """
        raise NotImplementedError("This method should be overridden")

    def handle_error(self):
        """
        处理任务执行后的所有错误
        """
        if not self.get_error_dict():
            return
        error_dict = self.get_error_dict()
        error_len = len(error_dict)
        # for num,(task, error) in enumerate(error_dict.items()):
        #     logger.error(f"Task {self.get_task_info(task)}(index:{num+1}/{error_len})")
        logger.error(f'There are total {error_len} errors.')
    
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
        
    def process_task_success(self, task, result, start_time):
        """
        统一处理任务成功

        参数:
        task: 完成的任务
        result: 任务的结果
        start_time: 任务开始时间
        """
        process_result = self.process_result(task, result)
        self.result_dict[task] = process_result
        self.result_queue.put(process_result)
        task_logger.task_success(self.func.__name__, self.get_task_info(task), self.execution_mode,
                                 self.get_result_info(result), time() - start_time)
        
    def handle_task_exception(self, task, exception: Exception):
        """
        统一处理任务异常

        参数:
        task: 发生异常的任务
        exception: 捕获的异常
        """
        retry_time = self.retry_time_dict.setdefault(task, 0)
        # 基于异常类型决定重试策略
        if retry_time < self.max_retries:
            self.task_queue.put(task)
            self.retry_time_dict[task] += 1
            delay_time = 2 ** retry_time
            task_logger.task_retry(self.get_task_info(task), self.retry_time_dict[task], delay_time)
            sleep(delay_time)  # 指数退避
        else:
            self.error_dict[task] = exception
            task_logger.task_fail(self.get_task_info(task), exception)

    def start(self, task_list):
        """
        根据 start_type 的值，选择串行、并行、异步或多进程执行任务

        参数:
        task_list: 任务列表
        """
        start_time = time()
        self.init_env()
        task_logger.start_task(self.func.__name__, len(task_list), self.execution_mode)

        for item in task_list:
            self.task_queue.put(item)

        self.task_queue.put(TERMINATION_SIGNAL)  # 添加一个哨兵任务，用于结束任务队列

        # 根据模式运行对应的任务处理函数
        if self.execution_mode == "thread":
            self.run_with_executor(self.thread_pool)
        elif self.execution_mode == "process":
            self.run_with_executor(self.process_pool)
        elif self.execution_mode == "async":
            asyncio.run(self.run_in_async())
        else:
            self.set_execution_mode('serial')
            self.run_in_serial()

        task_logger.end_task(self.func.__name__, self.execution_mode, time() - start_time, 
                        len(self.result_dict), len(self.error_dict), self.duplicates_num)

    async def start_async(self, task_list):
        """
        异步地执行任务

        参数:
        task_list: 任务列表
        """
        start_time = time()
        self.set_execution_mode('async')
        self.init_env()
        task_logger.start_task(self.func.__name__, len(task_list), 'async(await)')

        for item in task_list:
            await self.task_queue.put(item)

        await self.task_queue.put(TERMINATION_SIGNAL)  # 添加一个哨兵任务，用于结束任务队列
        await self.run_in_async()

        task_logger.end_task(self.func.__name__, self.execution_mode, time() - start_time, 
                        len(self.result_dict), len(self.error_dict), self.duplicates_num)
        
    def start_stage(self, input_queue: MPQueue, output_queue: MPQueue, stage_index):
        """
        根据 start_type 的值，选择串行、并行执行任务

        参数:
        task_list: 任务列表
        """
        start_time = time()
        self.init_env()
        task_logger.start_stage(stage_index+1, self.func.__name__, self.execution_mode)

        self.task_queue = input_queue
        self.result_queue = output_queue

        # 根据模式运行对应的任务处理函数
        if self.execution_mode == "thread":
            self.run_with_executor(self.thread_pool)
        elif self.execution_mode == "process":
            self.run_with_executor(self.process_pool)
        elif self.execution_mode == "async":
            asyncio.run(self.run_in_async())
        else:
            self.run_in_serial()

        self.result_queue.put(TERMINATION_SIGNAL)
        task_logger.end_stage(stage_index+1, self.func.__name__, self.execution_mode, time() - start_time,
                              len(self.result_dict), len(self.error_dict), self.duplicates_num)
 
    def run_in_serial(self):
        """
        串行地执行任务
        """
        progress_manager = ProgressManager(
            total_tasks=self.task_queue.qsize(),
            desc=f'{self.tqdm_desc}(serial)',
            mode="sync",
            show_progress=self.show_progress
        )
        start_time = time()
        will_retry = False

        # 从队列中依次获取任务并执行
        while True:
            task = self.task_queue.get()
            if isinstance(task, TerminationSignal):
                progress_manager.update(1)
                break
            elif self.is_duplicate(task):
                self.duplicates_num += 1
                progress_manager.update(1)
                continue
            try:
                result = self.func(*self.get_args(task))
                self.process_task_success(task, result, start_time)
            except Exception as error:
                self.handle_task_exception(task, error)
                will_retry = True
            progress_manager.update(1)

        progress_manager.close()

        if will_retry:
            self.task_queue.put(TERMINATION_SIGNAL)
            self.run_in_serial()
    
    def run_with_executor(self, executor):
        """
        使用指定的执行池（线程池或进程池）来并行执行任务。

        参数:
        executor: 线程池或进程池
        pool_type: "thread" 表示线程池, "process" 表示进程池, 用于日志记录和进度条显示
        """
        start_time = time()
        futures = {}
        will_retry = False
        
        progress_manager = ProgressManager(
            total_tasks=self.task_queue.qsize(),
            desc=f'{self.tqdm_desc}({self.execution_mode})',
            mode=self.execution_mode,
            show_progress=self.show_progress
        )

        # 从任务队列中提交任务到执行池
        while True:
            task = self.task_queue.get()
            if isinstance(task, TerminationSignal):
                progress_manager.update(1)
                break
            elif self.is_duplicate(task):
                self.duplicates_num += 1
                progress_manager.update(1)
                continue
            futures[executor.submit(self.func, *self.get_args(task))] = task

        # 处理已完成的任务
        for future in as_completed(futures):
            task = futures[future]
            try:
                result = future.result()  # 获取任务结果
                self.process_task_success(task, result, start_time)
            except Exception as error:
                self.handle_task_exception(task, error)
                will_retry = True
                # 动态更新进度条总数
                # progress_manager.add_total(1)
            progress_manager.update(1)

        progress_manager.close()

        if will_retry:
            self.task_queue.put(TERMINATION_SIGNAL)
            self.run_with_executor(executor)

    async def run_in_async(self):
        """
        异步地执行任务，限制并发数量
        """
        start_time = time()
        semaphore = asyncio.Semaphore(self.worker_limit)  # 限制并发数量
        will_retry = False

        async def sem_task(task):
            async with semaphore:  # 使用信号量限制并发
                result = await self._run_single_task(task)
                return task, result  # 返回 task 和 result

        # 创建异步任务列表
        async_tasks = []
        progress_manager = ProgressManager(
            total_tasks=self.task_queue.qsize(),
            desc=f'{self.tqdm_desc}(async)',
            mode="async",
            show_progress=self.show_progress
        )

        while True:
            task = await self.task_queue.get()
            if isinstance(task, TerminationSignal):
                progress_manager.update(1)
                break
            elif self.is_duplicate(task):
                self.duplicates_num += 1
                progress_manager.update(1)
                continue
            async_tasks.append(sem_task(task))  # 使用信号量包裹的任务

        # 并发运行所有任务
        for task_data, result in await asyncio.gather(*async_tasks, return_exceptions=True):
            if isinstance(result, Exception):
                self.handle_task_exception(task_data, result)
                will_retry = True
            else:
                self.process_task_success(task_data, result, start_time)
            progress_manager.update(1)

        progress_manager.close()

        if will_retry:
            await self.task_queue.put(TERMINATION_SIGNAL)
            await self.run_in_async()

    async def _run_single_task(self, task):
        """
        运行单个任务并捕获异常
        """
        try:
            result = await self.func(*self.get_args(task))
            return result
        except Exception as error:
            self.handle_task_exception(task, error)
            return error
            
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
    
    def test_methods(self, task_list):
        # Prepare the results dictionary
        results = {}

        # Test run_in_serial
        start = time()
        self.init_result_error_dict()
        self.set_execution_mode('serial')
        self.start(task_list)
        results['run_in_serial'] = time() - start

        # Test run_in_thread
        start = time()
        self.init_result_error_dict()
        self.set_execution_mode('thread')
        self.start(task_list)
        results['run_in_thread'] = time() - start

        # Test run_in_process
        start = time()
        self.init_result_error_dict()
        self.set_execution_mode('process')
        self.start(task_list)
        results['run_in_process'] = time() - start

        # # Test run_in_async
        # start = time()
        # self.start(task_list, 'async')
        # results['run_in_async'] = time() - start

        return results
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown_pools()


# As an example of use, we redefine the subclass of TaskManager
class ExampleTaskManager(TaskManager):
    def get_args(self, task):
        """
        从 obj 中获取参数

        在这个示例中，我们假设 obj 是一个整数，并将其作为参数返回
        """
        return (task,)

    def process_result(self, task, result):
        """
        从结果队列中获取结果，并进行处理

        在这个示例中，我们只是简单地打印结果
        """
        return result

class TaskChain:
    def __init__(self, stages, chain_mode='serial'):
        """
        stages: 一个包含 StageManager 实例的列表，表示执行链
        """
        self.stages: List[TaskManager] = stages
        self.chain_mode = chain_mode

        self.final_result_dict = {}  # 用于保存初始任务到最终结果的映射

    def set_chain_mode(self, chain_mode):
        """
        设置任务链的执行模式
        """
        self.chain_mode = chain_mode

    def add_stage(self, stage: TaskManager):
        self.stages.append(stage)

    def remove_stage(self, index: int):
        if 0 <= index < len(self.stages):
            self.stages.pop(index)

    def start_chain(self, tasks):
        """
        启动任务链
        """
        logger.info(f"Starting TaskChain with {len(self.stages)} stages by {self.chain_mode}.")

        if self.chain_mode == 'process':
            self.run_chain_in_process(tasks)
        else:
            self.set_chain_mode('serial')
            self.run_chain_in_serial(tasks)

    def run_chain_in_serial(self, tasks):
        """
        串行运行任务链
        """
        for stage in self.stages:
            stage.start(tasks)
            tasks = stage.get_result_dict().values()

    def run_chain_in_process(self, tasks):
        """
        并行运行任务链
        """
        # 创建进程间的队列
        queues = [MPQueue() for _ in range(len(self.stages) + 1)]
        
        # 为每个stage创建独立的共享result_dict
        manager = multiprocessing .Manager()
        stage_result_dicts = [manager.dict() for _ in self.stages]
        error_dict = manager.dict()  # 创建共享的 error_dict
        
        # 向第一个队列添加初始任务
        for task in tasks:
            queues[0].put(task)

        # 使用哨兵对象作为终止信号
        queues[0].put(TERMINATION_SIGNAL)
        
        # 创建多进程来运行每个环节
        processes = []
        for stage_index, stage in enumerate(self.stages):
            stage.init_result_error_dict(stage_result_dicts[stage_index], error_dict)
            p = multiprocessing.Process(target=stage.start_stage, args=(queues[stage_index], queues[stage_index + 1], stage_index))
            p.start()
            processes.append(p)
        
        # 等待所有进程结束
        for p in processes:
            p.join()

        for queue in queues:
            queue.close()
        
        # 释放资源
        # manager.shutdown()
            
    def get_final_result_dict(self):
        """
        查找对应的初始任务并更新 final_result_dict
        """
        if len(self.stages) == 1:
            return self.stages[0].get_result_dict()

        for initial_task, initial_result in self.stages[0].get_result_dict().items():
            stage_result = initial_result
            for stage in self.stages[1:]:
                stage_result = stage.get_result_dict().get(stage_result, None)
            self.final_result_dict[initial_task] = stage_result
        return self.final_result_dict