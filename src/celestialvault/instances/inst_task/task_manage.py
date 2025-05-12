from __future__ import annotations

import asyncio
from asyncio import Queue as AsyncQueue
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import Queue as MPQueue
from queue import Queue as ThreadQueue
from threading import Event, Lock
from time import time
from typing import List

from httpx import (ConnectError, ConnectTimeout, PoolTimeout, ProtocolError,
                   ReadError, ReadTimeout, RequestError)

from .task_progress import ProgressManager
from .task_support import TERMINATION_SIGNAL, TerminationSignal, task_logger


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

        self.retry_exceptions = (ConnectTimeout, ProtocolError, ReadError, ConnectError, PoolTimeout, ReadTimeout) # 需要重试的异常类型

        self.init_dict()

    def init_dict(self, success_dict=None, error_dict=None):
        """
        初始化结果字典
        """
        self.success_dict = success_dict if success_dict is not None else {}
        self.error_dict = error_dict if error_dict is not None else {} 

    def init_env(self, task_queue=None, result_queues=None, fail_queue=None):
        """
        初始化环境
        """
        self.init_queue(task_queue, result_queues, fail_queue)
        self.init_pool()

        self.retry_time_dict = {}
        self.duplicates_num = 0

    def init_queue(self, task_queue=None, result_queues=None, fail_queue=None):
        """
        初始化队列
        """
        queue_map = {
            "process": MPQueue,
            "async": AsyncQueue,
            "thread": ThreadQueue,
            "serial": ThreadQueue,
        }
        self.task_queue = task_queue or queue_map[self.execution_mode]()
        self.result_queues = result_queues or [ThreadQueue(),]
        self.fail_queue = fail_queue or ThreadQueue()

    def init_pool(self):
        """
        初始化线程池或进程池
        """
        # 可以复用的线程池或进程池
        if self.execution_mode == 'thread' and self.thread_pool is None:
            self.thread_pool = ThreadPoolExecutor(max_workers=self.worker_limit)
        elif self.execution_mode == 'process' and self.process_pool is None:
            self.process_pool = ProcessPoolExecutor(max_workers=self.worker_limit)

    def set_execution_mode(self, execution_mode):
        """
        设置执行模式
        :param execution_mode: 执行模式，可以是 'thread'（线程）, 'process'（进程）, 'async'（异步）, 'serial'（串行）
        """
        self.execution_mode = execution_mode if execution_mode in ['thread', 'process', 'async', 'serial'] else 'serial'

    def set_tree_context(self, next_stages: List[TaskManager] = None, stage_mode: str = None, stage_name: str = None):
        """
        设置链式上下文(仅限组成tree时)
        :param next_stages: 后续节点列表
        :param stage_mode: 当前节点执行模式, 可以是 'serial'（串行）或 'process'（并行）
        :param name: 当前节点名称
        """
        self.set_next_stages(next_stages)
        self.set_stage_mode(stage_mode)
        self.set_stage_name(stage_name)

    def set_next_stages(self, next_stages: List[TaskManager]):
        """
        设置后续节点列表
        """
        self.next_stages = next_stages or []  # 默认为空列表

    def set_stage_mode(self, stage_mode: str):
        """
        设置当前节点在tree中的执行模式, 可以是 'serial'（串行）或 'process'（并行）
        """
        self.stage_mode = stage_mode if stage_mode == 'process' else 'serial'

    def set_stage_name(self, name: str):
        """
        设置当前节点名称
        """
        self.stage_name = name or id(self)

    def get_stage_tag(self):
        """
        获取当前节点在tree中的标签
        """
        return f"{self.stage_name}[{self.func.__name__}]"

    def add_retry_exceptions(self, *exceptions):
        """
        添加需要重试的异常类型
        """
        self.retry_exceptions = self.retry_exceptions + tuple(exceptions)

    def put_task_queue(self, task_source):
        """
        将任务放入任务队列
        """
        for item in task_source:
            self.task_queue.put(item)
        self.task_queue.put(TERMINATION_SIGNAL)  # 添加一个哨兵任务，用于结束任务队列

    async def put_task_queue_async(self, task_source):
        """
        将任务放入任务队列(async模式)
        """
        for item in task_source:
            await self.task_queue.put(item)
        await self.task_queue.put(TERMINATION_SIGNAL)  # 添加一个哨兵任务，用于结束任务队列

    def put_result_queues(self, result):
        """
        将结果放入所有结果队列
        """
        for result_queue in self.result_queues:
            result_queue.put(result)

    def is_duplicate(self, task):
        """
        判断任务是否重复
        """
        return task in self.get_success_dict() or task in self.get_error_dict()

    def get_args(self, task):
        """
        从 obj 中获取参数S

        在这个示例中，我们假设 obj 是一个整数，并将其作为参数返回
        """
        return (task,)

    def process_result(self, task, result):
        """
        从结果队列中获取结果，并进行处理

        在这个示例中，我们只是简单地返回结果
        """
        return result

    def process_result_dict(self):
        """
        处理结果字典

        在这个示例中，我们合并了字典并返回
        """
        success_dict = self.get_success_dict()
        error_dict = self.get_error_dict()

        return {**success_dict, **error_dict}
    
    def handle_error_dict(self):
        """
        处理错误字典

        在这个示例中，我们将列表合并为错误组
        """
        error_dict = self.get_error_dict()

        error_groups = defaultdict(list)
        for task, error in error_dict.items():
            error_groups[error].append(task)

        return dict(error_groups)  # 转换回普通字典
    
    def get_task_info(self, task):
        """
        获取任务信息
        """
        info_list = []
        args = self.get_args(task)

        def format_arg(arg):
            arg_str = f'{arg}'.replace("\\", "\\\\").replace("\n", "\\n")
            if len(arg_str) < self.max_info or not self.max_info:
                return arg_str
            else:
                first_info = arg_str[:int(self.max_info * 2 // 3)]
                second_info = arg_str[-int(self.max_info * 1 // 3):]
                return f"{first_info}...{second_info}"

        if len(args) <= 3:
            info_list = [format_arg(arg) for arg in args]
        else:
            info_list = [format_arg(arg) for arg in args[:2]]
            info_list.append("...")  # 表示中间省略
            info_list.append(format_arg(args[-1]))

        return "(" + ", ".join(info_list) + ")"
    
    def get_result_info(self, result):
        """
        获取结果信息
        """
        result = f"{result}".replace("\\", "\\\\").replace("\n", "\\n")
        if len(result) < self.max_info:
            return result
        else:
            first_info = result[:int(self.max_info*2//3)]
            second_info = result[-int(self.max_info*1//3):]
            return f"{first_info}...{second_info}"
        
    def process_task_success(self, task, result, start_time):
        """
        统一处理成功任务

        :param task: 完成的任务
        :param result: 任务的结果
        :param start_time: 任务开始时间
        """
        processed_result = self.process_result(task, result)
        self.success_dict[task] = processed_result
        self.put_result_queues(processed_result)
        task_logger.task_success(self.func.__name__, self.get_task_info(task), self.execution_mode,
                                 self.get_result_info(result), time() - start_time)
        
    def handle_task_error(self, task, exception: Exception):
        """
        统一处理异常任务

        :param task: 发生异常的任务
        :param exception: 捕获的异常
        :return 是否需要重试
        """
        retry_time = self.retry_time_dict.setdefault(task, 0)

        # 基于异常类型决定重试策略
        if isinstance(exception, self.retry_exceptions) and retry_time < self.max_retries: 
            self.task_queue.put(task)
            self.retry_time_dict[task] += 1
            # delay_time = 2 ** retry_time
            # sleep(delay_time)  # 指数退避
            task_logger.task_retry(self.func.__name__, self.get_task_info(task), self.retry_time_dict[task])
        else:
            # 如果不是可重试的异常，直接将任务标记为失败
            self.error_dict[task] = exception
            self.fail_queue.put(task)
            task_logger.task_error(self.func.__name__, self.get_task_info(task), exception)
    
    async def handle_task_error_async(self, task, exception: Exception):
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
        else:
            # 如果不是可重试的异常，直接将任务标记为失败
            self.error_dict[task] = exception
            task_logger.task_error(self.func.__name__, self.get_task_info(task), exception)

        return will_try

    def start(self, task_source):
        """
        根据 start_type 的值，选择串行、并行、异步或多进程执行任务

        :param task_source: 任务迭代器或者生成器
        """
        start_time = time()
        self.init_env()

        try:
            total_tasks = len(task_source)
        except TypeError:
            total_tasks = 'Generator'
        task_logger.start_manager(self.func.__name__, total_tasks, self.execution_mode, self.worker_limit)

        self.put_task_queue(task_source)

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

        task_logger.end_manager(self.func.__name__, self.execution_mode, time() - start_time,
                             len(self.success_dict), len(self.error_dict), self.duplicates_num)

    async def start_async(self, task_source):
        """
        异步地执行任务

        :param task_source: 任务迭代器或者生成器
        """
        start_time = time()
        self.set_execution_mode('async')
        self.init_env()

        try:
            total_tasks = len(task_source)
        except TypeError:
            total_tasks = 'Generator'
        task_logger.start_manager(self.func.__name__, total_tasks, 'async(await)', self.worker_limit)

        await self.put_task_queue_async(task_source)
        await self.run_in_async()

        task_logger.end_manager(self.func.__name__, self.execution_mode, time() - start_time, 
                             len(self.success_dict), len(self.error_dict), self.duplicates_num)
        
    def start_stage(self, input_queue, output_queues, fail_queue):
        """
        根据 start_type 的值，选择串行、并行执行任务

        :param input_queue: 输入队列
        :param output_queue: 输出队列
        :param fail_queue: 失败队列
        """
        start_time = time()
        self.init_env(input_queue, output_queues, fail_queue)
        task_logger.start_stage(self.stage_name, self.func.__name__, self.execution_mode, self.worker_limit)

        # 根据模式运行对应的任务处理函数
        if self.execution_mode == "thread":
            self.run_with_executor(self.thread_pool)
        elif self.execution_mode == "process":
            self.run_with_executor(self.process_pool)
        elif self.execution_mode == "async":
            asyncio.run(self.run_in_async())
        else:
            self.run_in_serial()

        self.put_result_queues(TERMINATION_SIGNAL)
        self.fail_queue.put(TERMINATION_SIGNAL)
        task_logger.end_stage(self.stage_name, self.func.__name__, self.execution_mode, time() - start_time,
                              len(self.success_dict), len(self.error_dict), self.duplicates_num)
 
    def run_in_serial(self):
        """
        串行地执行任务
        """
        progress_manager = ProgressManager(
            total_tasks=self.task_queue.qsize(),
            desc=f'{self.progress_desc}(serial)',
            mode="normal",
            show_progress=self.show_progress
        )

        # 从队列中依次获取任务并执行
        while True:
            task = self.task_queue.get()
            task_logger.logger.trace(f"Task {task} is submitted to {self.func.__name__}")
            if isinstance(task, TerminationSignal):
                progress_manager.update(1)
                break
            elif self.is_duplicate(task):
                self.duplicates_num += 1
                progress_manager.update(1)
                task_logger.task_duplicate(self.func.__name__, self.get_task_info(task))
                continue
            try:
                start_time = time()
                result = self.func(*self.get_args(task))
                self.process_task_success(task, result, start_time)
            except Exception as error:
                self.handle_task_error(task, error)
            progress_manager.update(1)

        progress_manager.close()

        if self.task_queue.qsize():
            task_logger.logger.trace(f"Retrying tasks for {self.func.__name__}")
            # self.task_queue = self.retry_queue
            self.task_queue.put(TERMINATION_SIGNAL)
            self.run_in_serial()
    
    def run_with_executor(self, executor: ThreadPoolExecutor|ProcessPoolExecutor):
        """
        使用指定的执行池（线程池或进程池）来并行执行任务。

        :param executor: 线程池或进程池
        """
        task_start_dict = {}  # 用于存储任务开始时间

        # 用于追踪进行中任务数的计数器和事件
        in_flight = 0
        in_flight_lock = Lock()
        all_done_event = Event()
        all_done_event.set()  # 初始为无任务状态，设为完成状态
        
        progress_manager = ProgressManager(
            total_tasks=self.task_queue.qsize(),
            desc=f'{self.progress_desc}({self.execution_mode}-{self.worker_limit})',
            mode="normal",
            show_progress=self.show_progress
        )

        def on_task_done(future, task, progress_manager: ProgressManager):
            # 回调函数中处理任务结果
            progress_manager.update(1)
            try:
                result = future.result()
                start_time = task_start_dict[task]
                self.process_task_success(task, result, start_time)
            except Exception as error:
                self.handle_task_error(task, error)
            # 任务完成后减少in_flight计数
            with in_flight_lock:
                nonlocal in_flight
                in_flight -= 1
                if in_flight == 0:
                    all_done_event.set()

        # 从任务队列中提交任务到执行池
        while True:
            task = self.task_queue.get()
            task_logger.logger.trace(f"Task {task} is submitted to {self.func.__name__}")
            
            if isinstance(task, TerminationSignal):
                # 收到终止信号后不再提交新任务
                progress_manager.update(1)
                break
            elif self.is_duplicate(task):
                self.duplicates_num += 1
                progress_manager.update(1)
                task_logger.task_duplicate(self.func.__name__, self.get_task_info(task))
                continue

            # 提交新任务时增加in_flight计数，并清除完成事件
            with in_flight_lock:
                in_flight += 1
                all_done_event.clear()

            task_start_dict[task] = time()
            future = executor.submit(self.func, *self.get_args(task))
            future.add_done_callback(lambda f, t=task: on_task_done(f, t, progress_manager))

        # 等待所有已提交任务完成（包括回调）
        all_done_event.wait()

        # 所有任务和回调都完成了，现在可以安全关闭进度条
        progress_manager.close()

        if self.task_queue.qsize():
            task_logger.logger.trace(f"Retrying tasks for {self.func.__name__}")
            # self.task_queue = self.retry_queue
            self.task_queue.put(TERMINATION_SIGNAL)
            self.run_with_executor(executor)

    async def run_in_async(self):
        """
        异步地执行任务，限制并发数量
        """
        semaphore = asyncio.Semaphore(self.worker_limit)  # 限制并发数量

        async def sem_task(task):
            start_time = time()  # 记录任务开始时间
            async with semaphore:  # 使用信号量限制并发
                result = await self._run_single_task(task)
                return task, result, start_time  # 返回 task, result 和 start_time

        # 创建异步任务列表
        async_tasks = []
        progress_manager = ProgressManager(
            total_tasks=self.task_queue.qsize(),
            desc=f'{self.progress_desc}(async-{self.worker_limit})',
            mode="async",
            show_progress=self.show_progress
        )

        while True:
            task = await self.task_queue.get()
            task_logger.logger.trace(f"Task {task} is submitted to {self.func.__name__}")
            if isinstance(task, TerminationSignal):
                progress_manager.update(1)
                break
            elif self.is_duplicate(task):
                self.duplicates_num += 1
                progress_manager.update(1)
                task_logger.task_duplicate(self.func.__name__, self.get_task_info(task))
                continue
            async_tasks.append(sem_task(task))  # 使用信号量包裹的任务

        # 并发运行所有任务
        for task, result, start_time in await asyncio.gather(*async_tasks, return_exceptions=True):
            if not isinstance(result, Exception):
                self.process_task_success(task, result, start_time)
            else:
                await self.handle_task_error_async(task, result)
            progress_manager.update(1)

        progress_manager.close()

        if self.task_queue.qsize():
            task_logger.logger.trace(f"Retrying tasks for {self.func.__name__}")
            # self.task_queue = self.retry_queue
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
            
    def get_success_dict(self) -> dict:
        """
        获取成功任务的字典
        """
        return self.success_dict
    
    def get_error_dict(self) -> dict:
        """
        获取出错任务的字典
        """
        return self.error_dict

    def clean_env(self):
        """
        清理环境
        """
        self.release_resources()
        
        self.task_queue = None
        self.result_queues = None
        self.fail_queue = None
        
        self.thread_pool = None
        self.process_pool = None
    
    def release_resources(self):
        """
        关闭线程池和进程池，释放资源
        """
        for pool in [self.thread_pool, self.process_pool]:
            if pool:
                pool.shutdown(wait=True)
    
    def test_method(self, execution_mode: str, task_list: list) -> float:
        """
        测试方法
        """
        start = time()
        self.set_execution_mode(execution_mode)
        self.init_dict()
        self.start(task_list)
        return time() - start

    def test_methods(self, task_source: list|tuple|set) -> dict:
        """
        测试多种方法
        """
        # 如果 task_source 是生成器或一次性可迭代对象，需要提前转化成列表
        # 确保对不同模式的测试使用同一批任务数据
        task_list = list(task_source)

        results = {}
        for mode in ['serial', 'thread', 'process']:
            results[f'run_in_{mode}'] = self.test_method(mode, task_list)
        return results
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clean_env()
 
        