
import multiprocessing
from collections import defaultdict
from queue import Queue as ThreadQueue
from multiprocessing import Process, Queue as MPQueue
from typing import List, Any, Dict, Union
from time import time
from .task_manage import TaskManager
from .task_support import TERMINATION_SIGNAL, task_logger


class TaskChain:
    def __init__(self, stages, chain_mode='serial'):
        """
        :param stages: 一个包含 StageManager 实例的列表，表示执行链
        :param chain_mode: 执行链的模式，可以是 'serial'（串行）或 'process'（并行）
        """
        self.stages: List[TaskManager] = stages
        self.chain_mode = chain_mode

        self.init_dict()

    def init_dict(self):
        """
        初始化字典
        """
        self.final_result_dict = {}  # 用于保存初始任务到最终结果的映射
        self.final_error_dict = defaultdict(list)  # 用于保存初始任务到最终错误的映射

    def initialize_queues(self, tasks: list, is_mp: bool = False):
        queues = [MPQueue() if is_mp else ThreadQueue() for _ in range(len(self.stages) + 1)]
        for task in tasks:
            queues[0].put(task)
        queues[0].put(TERMINATION_SIGNAL)
        return queues

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

        task_logger.end_chain(time() - start_time)

    def run_chain_in_serial(self, tasks):
        """
        串行运行任务链
        """
        queues = self.initialize_queues(tasks, is_mp=False)

        stage_result_dicts = [dict() for _ in self.stages]
        stage_error_dicts = [dict() for _ in self.stages]

        for stage_index, stage in enumerate(self.stages):
            stage.init_result_error_dict(stage_result_dicts[stage_index], stage_error_dicts[stage_index])
            stage.start_stage(queues[stage_index], queues[stage_index + 1], stage_index)

        self.process_final_result_dict(tasks)
        self.handle_final_error_dict()
        self.release_resources([], None, [])

    def run_chain_in_process(self, tasks):
        """
        并行运行任务链
        """
        # 创建进程间的队列
        MPqueues = self.initialize_queues(tasks, is_mp=True)
        
        # 为每个stage创建独立的共享result_dict
        manager = multiprocessing.Manager()
        stage_result_dicts = [manager.dict() for _ in self.stages]
        stage_error_dicts = [manager.dict() for _ in self.stages]
        
        # 创建多进程来运行每个环节
        processes = []
        for stage_index, stage in enumerate(self.stages):
            stage.init_result_error_dict(stage_result_dicts[stage_index], stage_error_dicts[stage_index])
            p = multiprocessing.Process(target=stage.start_stage, args=(MPqueues[stage_index], MPqueues[stage_index + 1], stage_index))
            p.start()
            processes.append(p)
        
        # 等待所有进程结束
        for p in processes:
            p.join()

        self.process_final_result_dict(tasks)
        self.handle_final_error_dict()
        self.release_resources(MPqueues, manager, processes)

    def release_resources(self, MPqueues: List[MPQueue], manager, processes: List[Process]):
        # 关闭所有队列并确保它们的后台线程被终止
        for queue in MPqueues:
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
                stage_result_dict = stage.get_result_dict()
                stage_error_dict = stage.get_error_dict()
                if stage_task in stage_result_dict:
                    stage_task = stage_result_dict[stage_task]
                elif stage_task in stage_error_dict:
                    stage_task = (stage_error_dict[stage_task], stage.func.__name__, stage_index)
                    break
                else:
                    dispear_exception = Exception("Task not found.")
                    stage_task = (dispear_exception, stage.func.__name__, stage_index)
                    break

            self.final_result_dict[initial_task] = stage_task

    def handle_final_error_dict(self):
        """
        处理最终错误字典
        """
        for stage_index, stage in enumerate(self.stages):
            stage_error_dict = stage.get_error_dict()
            for task, error in stage_error_dict.items():
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
    
    def test_methods(self, task_list: List[Any]) -> Dict[str, Any]:
        """
        测试 TaskChain 在 'serial' 和 'process' 模式下的执行时间。
        
        :param task_list: 任务列表
        :return: 包含两种执行模式下的执行时间的字典
        """
        results = {}
        for mode in ['serial', 'process']:
            start_time = time()
            self.init_dict()
            self.set_chain_mode(mode)
            self.start_chain(task_list)
            results[f'{mode} chain'] = time() - start_time
        results['Final result dict'] = self.get_final_result_dict()
        results['Final error dict'] = self.get_final_error_dict()
        return results