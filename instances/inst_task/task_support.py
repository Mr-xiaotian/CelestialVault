from loguru import logger as loguru_logger
from time import strftime, localtime


class TerminationSignal:
    """用于标记任务队列终止的哨兵对象"""
    pass


class TaskLogger:
    """
    用于记录任务执行日志的类
    """
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

        
TERMINATION_SIGNAL = TerminationSignal()
task_logger = TaskLogger(loguru_logger)