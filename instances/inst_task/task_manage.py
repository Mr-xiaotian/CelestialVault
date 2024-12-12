from __future__ import annotations
import asyncio
from queue import Queue as ThreadQueue
from multiprocessing import Queue as MPQueue
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from httpx import ConnectTimeout, ProtocolError, ReadError, ConnectError, RequestError, PoolTimeout, ReadTimeout
from typing import List
from time import time
from instances.inst_progress import ProgressManager
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

        self.init_result_error_dict()
        
    def init_result_error_dict(self, result_dict=None, error_dict=None):
        self.result_dict = result_dict if result_dict is not None else {}
        self.error_dict = error_dict if error_dict is not None else {} 

    def init_env(self):
        queue_map = {
            "process": MPQueue,
            "async": asyncio.Queue,
            "thread": ThreadQueue,
            "serial": ThreadQueue,
        }
        self.task_queue = queue_map[self.execution_mode]()
        self.result_queue = ThreadQueue()

        self.retry_time_dict = {}
        self.duplicates_num = 0

        # 可以复用的线程池或进程池
        if self.execution_mode == 'thread' and self.thread_pool is None:
            self.thread_pool = ThreadPoolExecutor(max_workers=self.worker_limit)
        elif self.execution_mode == 'process' and self.process_pool is None:
            self.process_pool = ProcessPoolExecutor(max_workers=self.worker_limit)

    def set_next_stages(self, next_stages: List[TaskManager] = None):
        """
        定义任务链中的节点
        :param next_stages: 后续节点列表
        """
        self.next_stages = next_stages or []  # 默认为空列表

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
            if len(arg_str) < self.max_info or not self.max_info:
                info_list.append(arg_str)
            else:
                first_info = arg_str[:int(self.max_info*2//3)]
                second_info = arg_str[-int(self.max_info*1//3):]
                info_list.append(f"{first_info}...{second_info}")
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
        
    def start_stage(self, input_queue: ThreadQueue, output_queue: ThreadQueue, stage_index: int):
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
        for pool in [self.thread_pool, self.process_pool]:
            if pool:
                pool.shutdown(wait=True)

    def clean_env(self):
        """
        清理环境
        """
        self.release_resources()
        
        self.task_queue = None
        self.result_queue = None
        
        self.thread_pool = None
        self.process_pool = None
    
    def test_method(self, execution_mode: str, task_list: list) -> float:
        """
        测试方法
        """
        start = time()
        self.init_result_error_dict()
        self.set_execution_mode(execution_mode)
        self.start(task_list)
        return time() - start

    def test_methods(self, task_list: list) -> dict:
        """
        测试多种方法
        """
        results = {}
        for mode in ['serial', 'thread', 'process']:
            results[f'run_in_{mode}'] = self.test_method(mode, task_list)
        return results
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clean_env()


class ExampleTaskManager(TaskManager):
    """
    As an example of use, we redefine the subclass of TaskManager
    """
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
