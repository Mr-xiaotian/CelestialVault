import time

from .task_manage import TaskManager


class TaskSplitter(TaskManager):
    def __init__(self):
        """
        :param split_func: 用于分解任务的函数，默认直接返回原始值
        """
        super().__init__(
            func=self.split_task,
            execution_mode="serial",
            progress_desc="Spliting tasks",
            show_progress=False,
        )

    def split_task(self, *task):
        """
        实际上这个函数不执行逻辑，仅用于符合 TaskManager 架构
        """
        return task

    def get_args(self, task):
        return task

    def process_result(self, task, result):
        """
        处理不可迭代的任务结果
        """
        if not hasattr(result, "__iter__") or isinstance(result, (str, bytes)):
            result = (result,)
        elif isinstance(result, list):
            result = tuple(result)

        return result

    def process_task_success(self, task, result, start_time):
        """
        统一处理成功任务

        :param task: 完成的任务
        :param result: 任务的结果
        :param start_time: 任务开始时间
        """
        processed_result = self.process_result(task, result)
        self.redis_client.hset(f"{self.get_stage_tag()}:success", str(task), str(processed_result))
        self.redis_client.hset(f"{self.get_stage_tag()}:done_time", str(task), time.time())

        # 加锁方式（保证正确）
        with self.success_lock:
            self.success_counter.value += 1

        split_count = 0
        for item in processed_result:
            self.put_result_queues(item)
            split_count += 1

        self.extra_stats["split_output_count"].value += split_count

        self.task_logger.splitter_success(
            self.func.__name__,
            self.get_task_info(task),
            split_count,
            time.time() - start_time,
        )

