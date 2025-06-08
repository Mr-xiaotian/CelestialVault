from __future__ import annotations

import asyncio, time, redis, ast
from asyncio import Queue as AsyncQueue
from collections import defaultdict
from collections.abc import Iterable  
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import Queue as MPQueue
from queue import Queue as ThreadQueue
from threading import Event, Lock
from typing import List

from httpx import (
    ConnectError,
    ConnectTimeout,
    PoolTimeout,
    ProtocolError,
    ReadError,
    ReadTimeout,
    ProxyError,
    RequestError,
)

from .task_progress import ProgressManager
from .task_support import TERMINATION_SIGNAL, TerminationSignal, LogListener, TaskLogger, null_lock, ValueWrapper
from .task_tools import cleanup_mpqueue, is_queue_empty, is_queue_empty_async, make_hashable, format_repr


class TaskManager:
    def __init__(
        self,
        func,
        execution_mode="serial",
        worker_limit=50,
        max_retries=3,
        max_info=50,
        progress_desc="Processing",
        show_progress=False,
    ):
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

        self.set_prev_stage(None)
        self.set_stage_name(None)

        self.retry_exceptions = (
            ConnectTimeout,
            ProtocolError,
            ReadError,
            ConnectError,
            PoolTimeout,
            ReadTimeout,
            ProxyError,
        )  # 需要重试的异常类型

        self.init_dict()

    def init_redis(self, host="localhost", port=6379, db=0, decode_responses=True):
        self.redis_client = redis.Redis(
            host=host,             # 默认 Redis 服务地址
            port=port,             # 默认端口
            db=db,               # 使用的 Redis 数据库编号
            decode_responses=decode_responses  # 字符串自动解码为 str，而不是 bytes
        )

    def init_dict(self, success_counter=None, success_lock=None, extra_stats=None):
        """
        初始化结果字典
        """
        self.retry_time_dict = {}

        self.success_counter = success_counter if success_counter is not None else ValueWrapper()
        self.success_lock = success_lock if success_lock is not None else null_lock
        self.extra_stats = extra_stats if extra_stats is not None else {}

    def init_env(self, task_queue=None, result_queues=None, fail_queue=None, logger_queue=None):
        """
        初始化环境
        """
        self.init_queue(task_queue, result_queues, fail_queue, logger_queue)
        self.init_pool()
        self.init_logger()

        self.duplicates_num = 0

    def init_queue(self, task_queue=None, result_queues=None, fail_queue=None, logger_queue=None):
        """
        初始化队列
        """
        queue_map = {
            "process": MPQueue,
            "async": AsyncQueue,
            "thread": ThreadQueue,
            "serial": ThreadQueue,
        }
        self.task_queue: ThreadQueue|MPQueue = task_queue or queue_map[self.execution_mode]()
        self.result_queues = result_queues or [ThreadQueue()]
        self.fail_queue = fail_queue or ThreadQueue()
        self.logger_queue = logger_queue or ThreadQueue()

    def init_pool(self):
        """
        初始化线程池或进程池
        """
        # 可以复用的线程池或进程池
        if self.execution_mode == "thread" and self.thread_pool is None:
            self.thread_pool = ThreadPoolExecutor(max_workers=self.worker_limit)
        elif self.execution_mode == "process" and self.process_pool is None:
            self.process_pool = ProcessPoolExecutor(max_workers=self.worker_limit)

    def init_logger(self):
        """
        初始化日志
        """
        self.task_logger = TaskLogger(self.logger_queue)

    def init_listener(self):
        """
        初始化监听器
        """
        self.log_listener = LogListener("INFO")
        self.log_listener.start()

    def set_execution_mode(self, execution_mode):
        """
        设置执行模式
        :param execution_mode: 执行模式，可以是 'thread'（线程）, 'process'（进程）, 'async'（异步）, 'serial'（串行）
        """
        self.execution_mode = (
            execution_mode
            if execution_mode in ["thread", "process", "async", "serial"]
            else "serial"
        )

    def set_tree_context(
        self,
        next_stages: List[TaskManager] = None,
        stage_mode: str = None,
        stage_name: str = None,
    ):
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
        for next_stage in self.next_stages:
            next_stage.set_prev_stage(self)

    def set_stage_mode(self, stage_mode: str):
        """
        设置当前节点在tree中的执行模式, 可以是 'serial'（串行）或 'process'（并行）
        """
        self.stage_mode = stage_mode if stage_mode == "process" else "serial"

    def set_stage_name(self, name: str):
        """
        设置当前节点名称
        """
        self.stage_name = name or id(self)

    def set_prev_stage(self, prev_stage: TaskManager):
        """
        设置当前节点为最后一个节点
        """
        self.prev_stage = prev_stage

    def get_stage_tag(self):
        """
        获取当前节点在tree中的标签
        """
        return f"{self.stage_name}[{self.func.__name__}]"
    
    def get_status_snapshot(self) -> dict:
        """
        获取当前节点的状态快照
        """
        return {
            "execution_mode": self.execution_mode if self.execution_mode == "serial" else self.execution_mode + f"-{self.worker_limit}",
            "stage_mode": self.stage_mode,
            "func_name": self.func.__name__,
            "class_name": self.__class__.__name__,
        }

    def add_retry_exceptions(self, *exceptions):
        """
        添加需要重试的异常类型
        """
        self.retry_exceptions = self.retry_exceptions + tuple(exceptions)

    def put_task_queue(self, task_source) -> int:
        """
        将任务放入任务队列
        """
        task_num = 0
        for item in task_source:
            self.task_queue.put(make_hashable(item))
            task_num += 1
        self.task_queue.put(TERMINATION_SIGNAL)  # 添加一个哨兵任务，用于结束任务队列
        return task_num

    async def put_task_queue_async(self, task_source) -> int:
        """
        将任务放入任务队列(async模式)
        """
        task_num = 0
        for item in task_source:
            await self.task_queue.put(make_hashable(item))
            task_num += 1
        await self.task_queue.put(
            TERMINATION_SIGNAL
        )  # 添加一个哨兵任务，用于结束任务队列
        return task_num

    def put_result_queues(self, result):
        """
        将结果放入所有结果队列
        """
        for result_queue in self.result_queues:
            result_queue.put(result)

    def put_fail_queue(self, task, error):
        """
        将失败的任务放入失败队列
        """
        self.fail_queue.put({
            "stage_tag": self.get_stage_tag(),
            "task": str(task),
            "error_info": repr(error),
            "timestamp": time.time()
        })

    def is_duplicate(self, task):
        """
        判断任务是否重复
        """
        task_str = str(task)
        exists_success = self.redis_client.hexists(name=f"{self.get_stage_tag()}:success", key=task_str)
        exists_error = self.redis_client.hexists(name=f"{self.get_stage_tag()}:error", key=task_str)
        return exists_success or exists_error

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
        获取任务参数信息的可读字符串表示。
        """
        args = self.get_args(task)

        # 格式化每个参数
        def format_args_list(args_list):
            return [format_repr(arg, self.max_info) for arg in args_list]

        if len(args) <= 3:
            formatted_args = format_args_list(args)
        else:
            # 显示前两个 + ... + 最后一个
            head = format_args_list(args[:2])
            tail = format_args_list([args[-1]])
            formatted_args = head + ["..."] + tail

        return f"({', '.join(formatted_args)})"

    def get_result_info(self, result):
        """
        获取结果信息
        """
        return format_repr(result, self.max_info)

    def process_task_success(self, task, result, start_time):
        """
        统一处理成功任务

        :param task: 完成的任务
        :param result: 任务的结果
        :param start_time: 任务开始时间
        """
        processed_result = self.process_result(task, result)
        self.redis_client.hset(f"{self.get_stage_tag()}:success", str(task), str(processed_result))

        # 加锁方式（保证正确）
        with self.success_lock:
            self.success_counter.value += 1

        self.put_result_queues(processed_result)
        self.task_logger.task_success(
            self.func.__name__,
            self.get_task_info(task),
            self.execution_mode,
            self.get_result_info(result),
            time.time() - start_time,
        )

    def handle_task_error(self, task, exception: Exception):
        """
        统一处理异常任务

        :param task: 发生异常的任务
        :param exception: 捕获的异常
        :return 是否需要重试
        """
        retry_time = self.retry_time_dict.setdefault(task, 0)

        # 基于异常类型决定重试策略
        if (
            isinstance(exception, self.retry_exceptions)
            and retry_time < self.max_retries
        ):
            self.task_queue.put(task)
            self.retry_time_dict[task] += 1
            # delay_time = 2 ** retry_time
            # sleep(delay_time)  # 指数退避
            self.task_logger.task_retry(
                self.func.__name__, self.get_task_info(task), self.retry_time_dict[task]
            )
        else:
            # 如果不是可重试的异常，直接将任务标记为失败
            self.redis_client.hset(f"{self.get_stage_tag()}:error", str(task), repr(exception))
            self.put_fail_queue(task, exception)
            self.task_logger.task_error(
                self.func.__name__, self.get_task_info(task), exception
            )

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
        if (
            isinstance(exception, self.retry_exceptions)
            and retry_time < self.max_retries
        ):  # isinstance(exception, self.retry_exceptions) and
            await self.task_queue.put(task)
            self.retry_time_dict[task] += 1
            # delay_time = 2 ** retry_time
            self.task_logger.task_retry(
                self.func.__name__, self.get_task_info(task), self.retry_time_dict[task]
            )
            # sleep(delay_time)  # 指数退避
        else:
            # 如果不是可重试的异常，直接将任务标记为失败
            self.redis_client.hset(f"{self.get_stage_tag()}:error", str(task), repr(exception))
            self.put_fail_queue(task, exception)
            self.task_logger.task_error(
                self.func.__name__, self.get_task_info(task), exception
            )

        return will_try

    def start(self, task_source: Iterable):
        """
        根据 start_type 的值，选择串行、并行、异步或多进程执行任务

        :param task_source: 任务迭代器或者生成器
        """
        start_time = time.time()
        self.init_redis()
        self.init_listener()
        self.init_env(logger_queue=self.log_listener.get_queue())

        total_tasks = self.put_task_queue(task_source)
        self.task_logger.start_manager(
            self.func.__name__, total_tasks, self.execution_mode, self.worker_limit
        )

        # 根据模式运行对应的任务处理函数
        if self.execution_mode == "thread":
            self.run_with_executor(self.thread_pool)
        elif self.execution_mode == "process":
            self.run_with_executor(self.process_pool)
            cleanup_mpqueue(self.task_queue)
        elif self.execution_mode == "async":
            asyncio.run(self.run_in_async())
        else:
            self.set_execution_mode("serial")
            self.run_in_serial()

        self.task_logger.end_manager(
            self.func.__name__,
            self.execution_mode,
            time.time() - start_time,
            self.redis_client.hlen(f"{self.get_stage_tag()}:success"),
            self.redis_client.hlen(f"{self.get_stage_tag()}:error"),
            self.duplicates_num,
        )
        self.log_listener.stop()

    async def start_async(self, task_source: Iterable):
        """
        异步地执行任务

        :param task_source: 任务迭代器或者生成器
        """
        start_time = time.time()
        self.set_execution_mode("async")
        self.init_redis()
        self.init_listener()
        self.init_env(logger_queue=self.log_listener.get_queue())

        total_tasks = await self.put_task_queue_async(task_source)
        self.task_logger.start_manager(
            self.func.__name__, total_tasks, "async(await)", self.worker_limit
        )

        await self.run_in_async()

        self.task_logger.end_manager(
            self.func.__name__,
            self.execution_mode,
            time.time() - start_time,
            self.redis_client.hlen(f"{self.get_stage_tag()}:success"),
            self.redis_client.hlen(f"{self.get_stage_tag()}:error"),
            self.duplicates_num,
        )
        self.log_listener.stop()

    def start_stage(self, input_queue: MPQueue, output_queues: List[MPQueue], fail_queue: MPQueue, logger_queue: MPQueue):
        """
        根据 start_type 的值，选择串行、并行执行任务

        :param input_queue: 输入队列
        :param output_queue: 输出队列
        :param fail_queue: 失败队列
        """
        start_time = time.time()
        self.active = True
        self.init_redis()
        self.init_env(input_queue, output_queues, fail_queue, logger_queue)
        self.task_logger.start_stage(
            self.stage_name, self.func.__name__, self.execution_mode, self.worker_limit
        )

        # 根据模式运行对应的任务处理函数
        if self.execution_mode == "thread":
            self.run_with_executor(self.thread_pool)
        elif self.execution_mode == "process":
            self.run_with_executor(self.process_pool)
        elif self.execution_mode == "async":
            asyncio.run(self.run_in_async())
        else:
            self.run_in_serial()

        # cleanup_mpqueue(input_queue) # 会影响之后finalize_nodes
        self.put_result_queues(TERMINATION_SIGNAL)

        self.task_logger.end_stage(
            self.stage_name,
            self.func.__name__,
            self.execution_mode,
            time.time() - start_time,
            self.redis_client.hlen(f"{self.get_stage_tag()}:success"),
            self.redis_client.hlen(f"{self.get_stage_tag()}:error"),
            self.duplicates_num,
        )
        self.release_pool()

    def run_in_serial(self):
        """
        串行地执行任务
        """
        progress_manager = ProgressManager(
            total_tasks=self.task_queue.qsize(),
            desc=f"{self.progress_desc}(serial)",
            mode="normal",
            show_progress=self.show_progress,
        )

        # 从队列中依次获取任务并执行
        while True:
            task = self.task_queue.get()
            self.task_logger._log("TRACE",
                f"Task {task} is submitted to {self.func.__name__}"
            )
            if isinstance(task, TerminationSignal):
                progress_manager.update(1)
                break
            elif self.is_duplicate(task):
                # 加锁方式（保证正确）
                with self.success_lock:
                    self.success_counter.value += 1
                self.duplicates_num += 1
                self.task_logger.task_duplicate(self.func.__name__, self.get_task_info(task))
                progress_manager.update(1)
                continue
            try:
                start_time = time.time()
                result = self.func(*self.get_args(task))
                self.process_task_success(task, result, start_time)
            except Exception as error:
                self.handle_task_error(task, error)
            progress_manager.update(1)

        progress_manager.close()

        if not is_queue_empty(self.task_queue):
            self.task_logger._log("DEBUG", f"Retrying tasks for '{self.func.__name__}'")
            self.task_queue.put(TERMINATION_SIGNAL)
            self.run_in_serial()

    def run_with_executor(self, executor: ThreadPoolExecutor | ProcessPoolExecutor):
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
            desc=f"{self.progress_desc}({self.execution_mode}-{self.worker_limit})",
            mode="normal",
            show_progress=self.show_progress,
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
            self.task_logger._log("TRACE",
                f"Task {task} is submitted to {self.func.__name__}"
            )

            if isinstance(task, TerminationSignal):
                # 收到终止信号后不再提交新任务
                progress_manager.update(1)
                break
            elif self.is_duplicate(task):
                # 加锁方式（保证正确）
                with self.success_lock:
                    self.success_counter.value += 1
                self.duplicates_num += 1
                self.task_logger.task_duplicate(self.func.__name__, self.get_task_info(task))
                progress_manager.update(1)
                continue

            # 提交新任务时增加in_flight计数，并清除完成事件
            with in_flight_lock:
                in_flight += 1
                all_done_event.clear()

            task_start_dict[task] = time.time()
            future = executor.submit(self.func, *self.get_args(task))
            future.add_done_callback(
                lambda f, t=task: on_task_done(f, t, progress_manager)
            )

        # 等待所有已提交任务完成（包括回调）
        all_done_event.wait()

        # 所有任务和回调都完成了，现在可以安全关闭进度条
        progress_manager.close()

        if not is_queue_empty(self.task_queue):
            self.task_logger._log("DEBUG", f"Retrying tasks for '{self.func.__name__}'")
            self.task_queue.put(TERMINATION_SIGNAL)
            self.run_with_executor(executor)

    async def run_in_async(self):
        """
        异步地执行任务，限制并发数量
        """
        semaphore = asyncio.Semaphore(self.worker_limit)  # 限制并发数量

        async def sem_task(task):
            start_time = time.time()  # 记录任务开始时间
            async with semaphore:  # 使用信号量限制并发
                result = await self._run_single_task(task)
                return task, result, start_time  # 返回 task, result 和 start_time

        # 创建异步任务列表
        async_tasks = []
        progress_manager = ProgressManager(
            total_tasks=self.task_queue.qsize(),
            desc=f"{self.progress_desc}(async-{self.worker_limit})",
            mode="async",
            show_progress=self.show_progress,
        )

        while True:
            task = await self.task_queue.get()
            self.task_logger._log("TRACE",
                f"Task {task} is submitted to {self.func.__name__}"
            )
            if isinstance(task, TerminationSignal):
                progress_manager.update(1)
                break
            elif self.is_duplicate(task):
                # 加锁方式（保证正确）
                with self.success_lock:
                    self.success_counter.value += 1
                self.duplicates_num += 1
                self.task_logger.task_duplicate(self.func.__name__, self.get_task_info(task))
                progress_manager.update(1)
                continue
            async_tasks.append(sem_task(task))  # 使用信号量包裹的任务

        # 并发运行所有任务
        for task, result, start_time in await asyncio.gather(
            *async_tasks, return_exceptions=True
        ):
            if not isinstance(result, Exception):
                self.process_task_success(task, result, start_time)
            else:
                await self.handle_task_error_async(task, result)
            progress_manager.update(1)

        progress_manager.close()

        if not await is_queue_empty_async(self.task_queue):
            self.task_logger._log("DEBUG", f"Retrying tasks for '{self.func.__name__}'")
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
        获取成功任务的字典，并还原为原始类型
        """
        raw_dict = self.redis_client.hgetall(f"{self.get_stage_tag()}:success")
        return {ast.literal_eval(k): ast.literal_eval(v) for k, v in raw_dict.items()}

    def get_error_dict(self) -> dict:
        """
        获取出错任务的字典，并还原为原始类型
        """
        raw_dict = self.redis_client.hgetall(f"{self.get_stage_tag()}:error")
        return {ast.literal_eval(k): ast.literal_eval(v) for k, v in raw_dict.items()}

    def release_queue(self):
        """
        清理环境
        """
        self.task_queue = None
        self.result_queues = None
        self.fail_queue = None

    def release_pool(self):
        """
        关闭线程池和进程池，释放资源
        """
        for pool in [self.thread_pool, self.process_pool]:
            if pool:
                pool.shutdown(wait=True)
        self.thread_pool = None
        self.process_pool = None

        self.redis_client = None

    def clear_stage_data(self):
        self.redis_client.delete(f"{self.get_stage_tag()}:success")
        self.redis_client.delete(f"{self.get_stage_tag()}:error")

    def test_method(self, execution_mode: str, task_list: list) -> float:
        """
        测试方法
        """
        start = time.time()
        self.set_execution_mode(execution_mode)
        self.init_dict()
        self.start(task_list)
        self.clear_stage_data()  # 清理数据
        return time.time() - start

    def test_methods(self, task_source: list | tuple | set) -> dict:
        """
        测试多种方法
        """
        # 如果 task_source 是生成器或一次性可迭代对象，需要提前转化成列表
        # 确保对不同模式的测试使用同一批任务数据
        task_list = list(task_source)

        results = {}
        for mode in ["serial", "thread", "process"]:
            results[f"run_in_{mode}"] = self.test_method(mode, task_list)
        return results

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release_queue()
