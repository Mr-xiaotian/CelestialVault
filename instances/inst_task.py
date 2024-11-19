# -*- coding: utf-8 -*-
#版本 2.40
#作者：晓天, GPT-4
#时间：6/9/2024
#Github: https://github.com/Mr-xiaotian


import asyncio, multiprocessing
from queue import Queue as ThreadQueue
from multiprocessing import Process, Queue as MPQueue
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from httpx import ConnectTimeout, ProtocolError, ReadError, ConnectError, RequestError, PoolTimeout, ReadTimeout
from typing import List
from loguru import logger as loguru_logger
from time import time, strftime, localtime, sleep
from collections import defaultdict
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
        self.logger.add(f"logs/task_manager({now_time}).log",
                format="{time:YYYY-MM-DD HH:mm:ss} {level} {message}", 
                level="INFO")
        
    def start_task(self, func_name, task_num, execution_mode, worker_limit):
        start_text = f"'{func_name}' start {task_num} tasks by {execution_mode}"
        start_text += f"({worker_limit} workers)." if execution_mode != 'serial' else "."
        self.logger.info(start_text)

    def start_stage(self, stage_index, func_name, execution_mode):
        self.logger.info(f"The {stage_index} stage '{func_name}' start tasks by {execution_mode}.")

    def start_chain(self, stage_num, chain_mode):
        self.logger.info(f"Starting TaskChain with {stage_num} stages by {chain_mode}.")

    def end_task(self, func_name, execution_mode, use_time, success_num, failed_num, duplicated_num):
        self.logger.info(f"'{func_name}' end tasks by {execution_mode}. Use {use_time:.2f} second. {success_num} tasks successed, {failed_num} tasks failed, {duplicated_num} tasks duplicated.")

    def end_stage(self, stage_index, func_name, execution_mode, use_time, success_num, failed_num, duplicated_num):
        self.logger.info(f"The {stage_index} stage '{func_name}' end tasks by {execution_mode}. Use {use_time:.2f} second. {success_num} tasks successed, {failed_num} tasks failed, {duplicated_num} tasks duplicated.")
    
    def end_chain(self, use_time):
        self.logger.info(f"TaskChain end. Use {use_time:.2f} second.")

    def task_success(self, func_name, task_info, execution_mode, result_info, use_time):
        self.logger.success(f"In '{func_name}', Task {task_info} completed by {execution_mode}. Result is {result_info}. Used {use_time:.2f} seconds.")

    def task_retry(self, func_name, task_info, retry_times):
        self.logger.warning(f"In '{func_name}' Task {task_info} failed {retry_times} times and will retry.")

    def task_fail(self, func_name, task_info, exception):
        self.logger.error(f"In '{func_name}', Task {task_info} failed and can't retry: ({type(exception).__name__}){exception}")

    def task_duplicate(self, func_name, task_info):
        self.logger.success(f"In '{func_name}', Task {task_info} has been duplicated.")
task_logger = TaskLogger(loguru_logger)

class TaskManager:
    def __init__(self, func, execution_mode = 'serial',
                 worker_limit=50, max_retries=3, max_info=50,
                 progress_desc="Processing", show_progress=False):
        """
        初始化 TaskManager

        :param func: 可调用对象
        :param execution_mode: 执行模式，可选 'serial', 'thread', 'process', 'async'
        :param worker_limit: 同时处理数量
        :param max_retries: 任务的最大重试次数
        :param progress_desc: 进度条显示名称
        :param show_progress: 进度条显示与否
        """
        self.func = func
        self.execution_mode = execution_mode
        self.worker_limit = worker_limit
        self.max_retries = max_retries
        self.max_info = max_info

        self.progress_desc = progress_desc
        self.show_progress = show_progress

        self.thread_pool = None
        self.process_pool = None

        self.retry_exceptions = (ConnectTimeout, ProtocolError, ReadError, ConnectError, PoolTimeout, ReadTimeout, TypeError) # 需要重试的异常类型

        self.init_result_error_dict()
        
    def init_result_error_dict(self, result_dict=None, error_dict=None):
        self.result_dict = result_dict if result_dict is not None else {}
        self.error_dict = error_dict if error_dict is not None else {} 

    def init_env(self):
        if self.execution_mode == "process":
            self.task_queue = MPQueue()
        elif self.execution_mode == "async":
            self.task_queue = asyncio.Queue()
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

    def is_duplicate(self, task, task_set):
        return task in task_set

    def get_args(self, task):
        """
        从任务对象中提取执行函数的参数。

        :param task: 任务对象
        :return 包含执行函数所需参数的元组或列表。
        
        说明:
        这个方法必须在子类中实现。task 的具体结构依赖于子类的任务类型。
        """
        raise NotImplementedError("This method should be overridden")

    def process_result(self, task, result):
        """
        处理任务的结果。

        :param task: 已完成的任务对象
        :param result: 任务的执行结果
        :return 处理后的结果。

        说明:
        这个方法必须在子类中实现。可以记录错误、发送通知或其他错误处理操作。
        """
        raise NotImplementedError("This method should be overridden")
    
    def process_result_dict(self):
        """
        处理任务结果字典，将结果字典中的结果提取出来，并返回一个包含结果的列表。

        说明:
        这个方法必须在子类中实现。可以记录错误、发送通知或其他错误处理操作。
        """
        return NotImplementedError("This method should be overridden")

    def handle_error_dict(self):
        """
        处理任务执行后的所有错误

        说明:
        这个方法必须在子类中实现。可以记录错误、发送通知或其他错误处理操作。
        """
        raise NotImplementedError("This method should be overridden")
    
    def get_task_info(self, task):
        """
        获取任务信息
        """
        info_list = []
        for arg in self.get_args(task):
            arg_str = f'{arg}'.replace("\\", "\\\\").replace("\n", "\\n")
            if len(arg_str) < self.max_info:
                info_list.append(arg_str)
            else:
                info_list.append(f"{arg_str[:self.max_info]}...")
        return "(" + ", ".join(info_list) + ")"
    
    def get_result_info(self, result):
        """
        获取结果信息
        """
        result = f"{result}".replace("\\", "\\\\").replace("\n", "\\n")
        if len(result) < self.max_info:
            return result
        else:
            return f"{result[:self.max_info]}..."
        
    def process_task_success(self, task, result, start_time):
        """
        统一处理任务成功

        :param task: 完成的任务
        :param result: 任务的结果
        :param start_time: 任务开始时间
        """
        process_result = self.process_result(task, result)
        self.result_dict[task] = process_result
        self.result_queue.put(process_result)
        task_logger.task_success(self.func.__name__, self.get_task_info(task), self.execution_mode,
                                 self.get_result_info(result), time() - start_time)
        
    def handle_task_exception(self, task, exception: Exception):
        """
        统一处理任务异常

        :param task: 发生异常的任务
        :param exception: 捕获的异常

        :return 是否需要重试
        """
        retry_time = self.retry_time_dict.setdefault(task, 0)
        will_try = False

        # 基于异常类型决定重试策略
        if isinstance(exception, self.retry_exceptions) and retry_time < self.max_retries: # isinstance(exception, self.retry_exceptions) and
            self.task_queue.put(task)
            self.retry_time_dict[task] += 1
            # delay_time = 2 ** retry_time
            task_logger.task_retry(self.func.__name__, self.get_task_info(task), self.retry_time_dict[task])
            # sleep(delay_time)  # 指数退避
            will_try = True
        else:
            # 如果不是可重试的异常，直接将任务标记为失败
            self.error_dict[task] = exception
            task_logger.task_fail(self.func.__name__, self.get_task_info(task), exception)

        return will_try
    
    async def handle_task_exception_async(self, task, exception: Exception):
        """
        统一处理任务异常, 异步版本

        :param task: 发生异常的任务
        :param exception: 捕获的异常

        :return 是否需要重试
        """
        retry_time = self.retry_time_dict.setdefault(task, 0)
        will_try = False

        # 基于异常类型决定重试策略
        if isinstance(exception, self.retry_exceptions) and retry_time < self.max_retries: # isinstance(exception, self.retry_exceptions) and
            await self.task_queue.put(task)
            self.retry_time_dict[task] += 1
            # delay_time = 2 ** retry_time
            task_logger.task_retry(self.func.__name__, self.get_task_info(task), self.retry_time_dict[task])
            # sleep(delay_time)  # 指数退避
            will_try = True
        else:
            # 如果不是可重试的异常，直接将任务标记为失败
            self.error_dict[task] = exception
            task_logger.task_fail(self.func.__name__, self.get_task_info(task), exception)

        return will_try

    def start(self, task_list):
        """
        根据 start_type 的值，选择串行、并行、异步或多进程执行任务

        :param task_list: 任务列表
        """
        start_time = time()
        self.init_env()
        task_logger.start_task(self.func.__name__, len(task_list), self.execution_mode, self.worker_limit)

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

        :param task_list: 任务列表
        """
        start_time = time()
        self.set_execution_mode('async')
        self.init_env()
        task_logger.start_task(self.func.__name__, len(task_list), 'async(await)', self.worker_limit)

        for item in task_list:
            await self.task_queue.put(item)

        await self.task_queue.put(TERMINATION_SIGNAL)  # 添加一个哨兵任务，用于结束任务队列
        await self.run_in_async()

        task_logger.end_task(self.func.__name__, self.execution_mode, time() - start_time, 
                             len(self.result_dict), len(self.error_dict), self.duplicates_num)
        
    def start_stage(self, input_queue: MPQueue, output_queue: MPQueue, stage_index: int):
        """
        根据 start_type 的值，选择串行、并行执行任务

        :param input_queue: 输入队列
        :param output_queue: 输出队列
        :param stage_index: 阶段索引
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
            desc=f'{self.progress_desc}(serial)',
            mode="sync",
            show_progress=self.show_progress
        )
        will_retry = False
        temp_task_set = set()  # 用于存储临时任务，避免重复执行

        # 从队列中依次获取任务并执行
        while True:
            task = self.task_queue.get()
            if isinstance(task, TerminationSignal):
                progress_manager.update(1)
                break
            elif self.is_duplicate(task, temp_task_set):
                self.duplicates_num += 1
                progress_manager.update(1)
                task_logger.task_duplicate(self.func.__name__, task)
                continue
            try:
                start_time = time()
                result = self.func(*self.get_args(task))
                self.process_task_success(task, result, start_time)
            except Exception as error:
                will_retry = self.handle_task_exception(task, error)
            progress_manager.update(1)
            temp_task_set.add(task)

        progress_manager.close()

        if will_retry:
            self.task_queue.put(TERMINATION_SIGNAL)
            self.run_in_serial()
    
    def run_with_executor(self, executor):
        """
        使用指定的执行池（线程池或进程池）来并行执行任务。

        :param executor: 线程池或进程池
        :param pool_type: "thread" 表示线程池, "process" 表示进程池, 用于日志记录和进度条显示
        """
        start_time = time()
        futures = {}
        will_retry = False
        
        progress_manager = ProgressManager(
            total_tasks=self.task_queue.qsize(),
            desc=f'{self.progress_desc}({self.execution_mode})',
            mode=self.execution_mode,
            show_progress=self.show_progress
        )
        temp_task_set = set()  # 用于存储临时任务，避免重复执行

        # 从任务队列中提交任务到执行池
        while True:
            task = self.task_queue.get()
            if isinstance(task, TerminationSignal):
                progress_manager.update(1)
                break
            elif self.is_duplicate(task, temp_task_set):
                self.duplicates_num += 1
                progress_manager.update(1)
                task_logger.task_duplicate(self.func.__name__, task)
                continue
            futures[executor.submit(self.func, *self.get_args(task))] = task
            temp_task_set.add(task)

        # 处理已完成的任务
        for future in as_completed(futures):
            task = futures[future]
            try:
                result = future.result()  # 获取任务结果
                self.process_task_success(task, result, start_time)
            except Exception as error:
                will_retry = self.handle_task_exception(task, error)
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
        semaphore = asyncio.Semaphore(self.worker_limit)  # 限制并发数量
        will_retry = False
        temp_task_set = set()  # 用于存储临时任务，避免重复执行

        async def sem_task(task):
            start_time = time()  # 记录任务开始时间
            async with semaphore:  # 使用信号量限制并发
                result = await self._run_single_task(task)
                return task, result, start_time  # 返回 task, result 和 start_time

        # 创建异步任务列表
        async_tasks = []
        progress_manager = ProgressManager(
            total_tasks=self.task_queue.qsize(),
            desc=f'{self.progress_desc}(async)',
            mode="async",
            show_progress=self.show_progress
        )

        while True:
            task = await self.task_queue.get()
            if isinstance(task, TerminationSignal):
                progress_manager.update(1)
                break
            elif self.is_duplicate(task, temp_task_set):
                self.duplicates_num += 1
                progress_manager.update(1)
                task_logger.task_duplicate(self.func.__name__, task)
                continue
            async_tasks.append(sem_task(task))  # 使用信号量包裹的任务
            temp_task_set.add(task)

        # 并发运行所有任务
        for task, result, start_time in await asyncio.gather(*async_tasks, return_exceptions=True):
            if not isinstance(result, Exception):
                self.process_task_success(task, result, start_time)
            else:
                will_retry = await self.handle_task_exception_async(task, result)
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
    
    def release_resources(self):
        """
        关闭线程池和进程池，释放资源
        """
        try:
            if self.thread_pool:
                self.thread_pool.shutdown(wait=True)
        except Exception as e:
            task_logger.logger.error(f"Error during thread pool shutdown: {e}")

        try:
            if self.process_pool:
                self.process_pool.shutdown(wait=True)
        except Exception as e:
            task_logger.logger.error(f"Error during process pool shutdown: {e}")

    def clean_env(self):
        self.release_resources()
        
        self.task_queue = None
        self.result_queue = None
        
        self.thread_pool = None
        self.process_pool = None
    
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
        self.clean_env()


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

        在这个示例中，我们只是简单地返回结果
        """
        return result

class TaskChain:
    def __init__(self, stages, chain_mode='serial'):
        """
        stages: 一个包含 StageManager 实例的列表，表示执行链
        """
        self.stages: List[TaskManager] = stages
        self.chain_mode = chain_mode

        self.init_dict()

    def init_dict(self):
        self.final_result_dict = {}  # 用于保存初始任务到最终结果的映射
        self.final_error_dict = defaultdict(list)  # 用于保存初始任务到最终错误的映射

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
        start_time = time()
        task_logger.start_chain(len(self.stages), self.chain_mode)

        if self.chain_mode == 'process':
            self.run_chain_in_process(tasks)
        else:
            self.set_chain_mode('serial')
            self.run_chain_in_serial(tasks)

        task_logger.end_chain(time()-start_time)

    def run_chain_in_serial(self, tasks):
        """
        串行运行任务链
        """
        stage_tasks = tasks
        for stage in self.stages:
            stage.start(stage_tasks)
            stage_tasks = stage.get_result_dict().values()

        self.process_final_result_dict(tasks)
        self.handle_final_error_dict()
        self.release_resources([], None, [])

    def run_chain_in_process(self, tasks):
        """
        并行运行任务链
        """
        # 创建进程间的队列
        queues = [MPQueue() for _ in range(len(self.stages) + 1)]
        
        # 为每个stage创建独立的共享result_dict
        manager = multiprocessing.Manager()
        stage_result_dicts = [manager.dict() for _ in self.stages]
        stage_error_dicts = [manager.dict() for _ in self.stages]
        
        # 向第一个队列添加初始任务
        for task in tasks:
            queues[0].put(task)

        # 使用哨兵对象作为终止信号
        queues[0].put(TERMINATION_SIGNAL)
        
        # 创建多进程来运行每个环节
        processes = []
        for stage_index, stage in enumerate(self.stages):
            stage.init_result_error_dict(stage_result_dicts[stage_index], stage_error_dicts[stage_index])
            p = multiprocessing.Process(target=stage.start_stage, args=(queues[stage_index], queues[stage_index + 1], stage_index))
            p.start()
            processes.append(p)
        
        # 等待所有进程结束
        for p in processes:
            p.join()

        self.process_final_result_dict(tasks)
        self.handle_final_error_dict()
        self.release_resources(queues, manager, processes)

    def release_resources(self, queues: List[MPQueue], manager, processes: List[Process]):
        # 关闭所有队列并确保它们的后台线程被终止
        for queue in queues:
            queue.close()
            queue.join_thread()  # 确保队列的后台线程正确终止

        # 关闭 multiprocessing.Manager
        if manager is not None:
            manager.shutdown()

        # 确保所有进程已被正确终止
        for p in processes:
            if p.is_alive():
                p.terminate()  # 如果进程仍在运行，强制终止
            p.join()  # 确保进程终止

        # 关闭所有stage的线程池
        for stage in self.stages:
            stage.clean_env()
            
    def process_final_result_dict(self, initial_tasks):
        """
        查找对应的初始任务并更新 final_result_dict

        :param initial_tasks: 一个包含初始任务的列表
        """
        for initial_task in initial_tasks:
            stage_task = initial_task
            for stage_index, stage in enumerate(self.stages):
                if stage_task in stage.get_result_dict():
                    stage_task = stage.get_result_dict()[stage_task]
                elif stage_task in stage.get_error_dict():
                    stage_task = (stage.get_error_dict()[stage_task], stage.func.__name__, stage_index)
                    break
                else:
                    stage_task = Exception(f"Task not found in stage {stage_index} dict, stage func is {stage.func.__name__}.")
                    break
            self.final_result_dict[initial_task] = stage_task

    def handle_final_error_dict(self):
        """
        处理最终错误字典
        """
        for stage_index, stage in enumerate(self.stages):
            for task, error in stage.get_error_dict().items():
                self.final_error_dict[(type(error).__name__, str(error), stage_index)].append(task)
    
    def get_final_result_dict(self):
        """
        返回最终结果字典
        """
        return self.final_result_dict
    
    def get_final_error_dict(self):
        """
        返回最终错误字典
        """
        return self.final_error_dict
    
    def test_methods(self, task_list):
        """
        测试 TaskChain 在 'serial' 和 'process' 模式下的执行时间。
        
        :param task_list: 任务列表
        :return: 包含两种执行模式下的执行时间的字典
        """
        results = {}

        # 测试 serial 模式
        start_time = time()
        self.init_dict()
        self.set_chain_mode('serial')
        self.start_chain(task_list)
        results['serial chain'] = time() - start_time
        
        # 测试 process 模式
        start_time = time()
        self.init_dict()
        self.set_chain_mode('process')
        self.start_chain(task_list)
        results['process chain'] = time() - start_time

        results['Final result dict'] = self.get_final_result_dict()
        results['Final error dict'] = self.get_final_error_dict()

        return results