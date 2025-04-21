from time import time
from .task_manage import ExampleTaskManager
from .task_support import task_logger

class TaskSplitter(ExampleTaskManager):
    def __init__(self):
        """
        :param split_func: 用于分解任务的函数，默认直接返回原始值
        """
        super().__init__(func=self.split_task, execution_mode='serial')
    
    def split_task(self, task):
        """
        实际上这个函数不执行逻辑，仅用于符合 TaskManager 架构
        """
        return task

    def process_task_success(self, task, result, start_time):
        """
        统一处理成功任务

        :param task: 完成的任务
        :param result: 任务的结果
        :param start_time: 任务开始时间
        """
        processed_result = self.process_result(task, result)
        self.result_dict[task] = None
        split_count = 0

        if not hasattr(processed_result, '__iter__') or isinstance(processed_result, (str, bytes)):
            processed_result = [processed_result]

        for item in processed_result:
            self.result_queue.put(item)
            split_count += 1

        task_logger.splitter_success(self.func.__name__, self.get_task_info(task), split_count, time() - start_time)

