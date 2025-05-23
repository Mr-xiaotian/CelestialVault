import threading
from multiprocessing import Queue as MPQueue
from queue import Queue as ThreadQueue, Empty
from threading import Thread
from time import localtime, strftime, sleep
from typing import List, Union

import requests
from loguru import logger as loguru_logger


class TerminationSignal:
    """用于标记任务队列终止的哨兵对象"""

    pass


class TaskError(Exception):
    """用于标记任务执行错误的异常类"""

    pass


class LogListener:
    def __init__(self, log_path=None, level="INFO"):
        now = strftime("%Y-%m-%d", localtime())
        self.log_path = log_path or f"logs/task_logger({now}).log"
        self.level = level
        self.log_queue = MPQueue()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._listen, daemon=True)

    def start(self):
        # 配置 loguru 的两个 handler，stdout + file
        loguru_logger.remove()
        loguru_logger.add(
            self.log_path,
            level=self.level,
            format="{time:YYYY-MM-DD HH:mm:ss} {level} {message}",
            enqueue=True,
        )
        self._thread.start()

    def _listen(self):
        while not self._stop_event.is_set():
            try:
                record = self.log_queue.get(timeout=0.5)
                if isinstance(record, TerminationSignal):
                    break
                loguru_logger.log(record["level"], record["message"])
            except Empty:
                continue
            # except Exception as e:
            #     loguru_logger.error(f"LogListener thread error: {type(e).__name__}({e})")

    def get_queue(self):
        return self.log_queue

    def stop(self):
        self._stop_event.set()
        self.log_queue.put(TerminationSignal)  # 通知线程退出
        self._thread.join()


class TaskLogger:
    """
    多进程安全日志包装类，所有日志通过队列发送到监听进程写入
    """

    def __init__(self, log_queue=None):
        self.log_queue = log_queue

    def _log(self, level, message):
        self.log_queue.put({"level": level.upper(), "message": message})

    def start_manager(self, func_name, task_num, execution_mode, worker_limit):
        text = f"'{func_name}' start {task_num} tasks by {execution_mode}"
        text += f"({worker_limit} workers)." if execution_mode != "serial" else "."
        self._log("INFO", text)

    def end_manager(self, func_name, execution_mode, use_time, success_num, failed_num, duplicated_num):
        self._log(
            "INFO",
            f"'{func_name}' end tasks by {execution_mode}. Use {use_time:.2f} second. "
            f"{success_num} tasks successed, {failed_num} tasks failed, {duplicated_num} tasks duplicated.",
        )

    def start_stage(self, stage_name, func_name, execution_mode, worker_limit):
        text = f"The {stage_name} in '{func_name}' start tasks by {execution_mode}"
        text += f"({worker_limit} workers)." if execution_mode != "serial" else "."
        self._log("INFO", text)

    def end_stage(self, stage_name, func_name, execution_mode, use_time, success_num, failed_num, duplicated_num):
        self._log(
            "INFO",
            f"The {stage_name} in '{func_name}' end tasks by {execution_mode}. Use {use_time:.2f} second. "
            f"{success_num} tasks successed, {failed_num} tasks failed, {duplicated_num} tasks duplicated.",
        )

    def start_tree(self, stage_structure):
        self._log("INFO", f"Starting TaskTree stages. Tree structure:")
        for line in stage_structure:
            self._log("INFO", line)

    def end_tree(self, use_time):
        self._log("INFO", f"TaskTree end. Use {use_time:.2f} second.")

    def task_success(self, func_name, task_info, execution_mode, result_info, use_time):
        self._log("SUCCESS", f"In '{func_name}', Task {task_info} completed by {execution_mode}. Result is {result_info}. Used {use_time:.2f} seconds.")

    def task_retry(self, func_name, task_info, retry_times):
        self._log("WARNING", f"In '{func_name}', Task {task_info} failed {retry_times} times and will retry.")

    def task_error(self, func_name, task_info, exception):
        self._log("ERROR", f"In '{func_name}', Task {task_info} failed and can't retry: ({type(exception).__name__}){exception}.")

    def task_duplicate(self, func_name, task_info):
        self._log("SUCCESS", f"In '{func_name}', Task {task_info} has been duplicated.")

    def splitter_success(self, func_name, task_info, split_count, use_time):
        self._log("SUCCESS", f"In '{func_name}', Task {task_info} has split into {split_count} parts. Used {use_time:.2f} seconds.")


class BroadcastQueueManager:
    def __init__(
        self,
        input_queue: Union[MPQueue, ThreadQueue],
        target_queues: List[Union[MPQueue, ThreadQueue]],
        func_name: str,
        logger_queue: MPQueue
    ):
        """
        广播队列管理器
        :param input_queue: 源输入队列
        :param target_queues: 目标队列列表
        """
        self.input_queue = input_queue
        self.target_queues = target_queues
        self.func_name = func_name
        self.log = TaskLogger(logger_queue)

    def start(self):
        """开始广播线程"""
        self.thread = Thread(target=self.broadcast)
        self.thread.start()

    def stop(self):
        """停止广播线程"""
        self.thread.join()

    def broadcast(self):
        """将输入队列的数据广播到目标队列"""
        while True:
            try:
                item = self.input_queue.get()  # 从输入队列获取数据
                if isinstance(item, TerminationSignal):  # 检测到终止信号时广播并退出
                    break
                self._broadcast_to_all(item)
            except Exception as e:
                self.log._log("ERROR",
                    f"{self.func_name} broadcast thread error: {type(e).__name__}({e})"
                )
        self._broadcast_to_all(TERMINATION_SIGNAL)

    def _broadcast_to_all(self, item):
        """广播数据到所有目标队列"""
        self.log._log("TRACE",
            f"{self.func_name} broadcasting {item} to all target queues."
        )
        for queue in self.target_queues:
            queue.put(item)


class TaskReporter:
    def __init__(self, task_tree, logger_queue, host="127.0.0.1", port=5000):
        from .task_tree import TaskTree

        self.task_tree: TaskTree = task_tree
        self.logger = TaskLogger(logger_queue)
        self.base_url = f"http://{host}:{port}"
        self._stop_flag = threading.Event()
        self._thread = None
        self.interval = 5

    def start(self):
        if self._thread is None or not self._thread.is_alive():
            self._stop_flag.clear()
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()
            self.push_structure_once()

    def stop(self):
        if self._thread:
            self.push_once()  # 最后一次
            self._stop_flag.set()
            self._thread.join(timeout=2)
            self._thread = None

    def _loop(self):
        while not self._stop_flag.is_set():
            try:
                self.push_once()
            except Exception as e:
                self.logger._log("ERROR",f"[Reporter] Push error: {type(e).__name__}({e})")
            self._stop_flag.wait(self.interval)

    def push_once(self):
        self._sync_interval()
        self._push_status()
        self._push_errors()

    def _sync_interval(self):
        try:
            res = requests.get(f"{self.base_url}/api/get_interval", timeout=1)
            if res.ok:
                interval = res.json().get("interval", 5)
                self.interval = max(1.0, min(interval, 60.0))
        except Exception as e:
            self.logger._log("WARNING",f"[Reporter] Interval fetch failed: {type(e).__name__}({e})")

    def _push_status(self):
        try:
            status_data = self.task_tree.get_status_dict()
            requests.post(f"{self.base_url}/api/push_status", json=status_data, timeout=1)
        except Exception as e:
            self.logger._log("WARNING",f"[Reporter] Status push failed: {type(e).__name__}({e})")

    def _push_errors(self):
        try:
            self.task_tree.handle_fail_queue()
            error_data = []
            for (err, tag), task_list in self.task_tree.get_error_timeline_dict().items():
                for task, ts in task_list:
                    error_data.append({
                        "error": err,
                        "node": tag,
                        "task_id": task,
                        "timestamp": ts,
                    })
            requests.post(f"{self.base_url}/api/push_errors", json=error_data, timeout=1)
        except Exception as e:
            self.logger._log("WARNING",f"[Reporter] Error push failed: {type(e).__name__}({e})")

    def push_structure_once(self):
        try:
            structure = self.task_tree.get_structure_tree(self.task_tree.root_stage)
            requests.post(f"{self.base_url}/api/push_structure", json=structure, timeout=1)
        except Exception as e:
            self.logger._log("WARNING",f"[Reporter] Structure push failed: {type(e).__name__}({e})")


class NoOpContext:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class ValueWrapper:
    def __init__(self, value=0):
        self.value = value


null_lock = NoOpContext()
counter = ValueWrapper()
TERMINATION_SIGNAL = TerminationSignal()
