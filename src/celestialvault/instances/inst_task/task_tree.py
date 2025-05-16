import json
import multiprocessing
from collections import defaultdict
from datetime import datetime
from multiprocessing import Queue as MPQueue
from pathlib import Path
from time import time
from typing import Any, Dict, List

from .task_manage import TaskManager
from .task_nodes import TaskSplitter
from .task_support import TERMINATION_SIGNAL, TaskError, task_logger
from .task_web import TaskWebServer


class TaskTree:
    def __init__(self, root_stage: TaskManager, start_web_server=False):
        """
        :param root_stage: 任务链的根 TaskManager 节点
        :param start_web_server: 是否启动 web 服务
        """
        self.set_root_stage(root_stage)
        self.init_dict()

        self.web_server = None
        if start_web_server:
            self.web_server = TaskWebServer(self)
            self.web_server.start_server()

    def init_env(self, tasks: list):
        """
        初始化环境
        """
        self.processes: List[multiprocessing.Process] = []
        self.manager = multiprocessing.Manager()
        self.status_manager = multiprocessing.Manager()

        self.init_dict()
        self.init_queues(tasks)

    def init_dict(self):
        """
        初始化字典
        """
        self.stage_dict: Dict[str, TaskManager] = {}
        self.stage_queues_dict: Dict[str, MPQueue] = {}
        
        self.final_result_dict = {}  # 用于保存初始任务到最终结果的映射
        self.final_error_dict = defaultdict(list)  # 用于保存错误到出现该错误任务的映射
        self.final_fail_dict = defaultdict(list)  # 用于保存节点到节点失败任务的映射

    def init_queues(self, tasks: list):
        """
        初始化任务队列
        :param tasks: 待处理的任务列表
        """

        def collect_queue(stage: TaskManager):
            # 为每个节点创建队列
            self.stage_queues_dict[stage.get_stage_tag()] = MPQueue()
            self.stage_dict[stage.get_stage_tag()] = stage
            visited_stages.add(stage)

            for next_stage in stage.next_stages:
                if next_stage in visited_stages:
                    continue
                collect_queue(next_stage)

        # 初始化每个节点的队列
        visited_stages = set()
        self.stage_dict[self.root_stage.get_stage_tag()] = self.root_stage
        collect_queue(self.root_stage)

        for task in tasks:
            self.stage_queues_dict[self.root_stage.get_stage_tag()].put(task)
        self.stage_queues_dict[self.root_stage.get_stage_tag()].put(TERMINATION_SIGNAL)

    def set_root_stage(self, root_stage: TaskManager):
        """
        设定根节点
        """
        self.root_stage = root_stage

    def set_tree_mode(self, stage_mode: str, execution_mode: str):
        """
        设置任务链的执行模式
        :param stage_mode: 节点执行模式, 可选值为 'serial' 或 'process'
        :param execution_mode: 节点内部执行模式, 可选值为 'serial' 或 'thread''
        """

        def set_subsequent_satge_mode(stage: TaskManager):
            stage.set_stage_mode(stage_mode)
            stage.set_execution_mode(execution_mode)
            visited_stages.add(stage)

            for next_stage in stage.next_stages:
                if next_stage in visited_stages:
                    continue
                set_subsequent_satge_mode(next_stage)

        visited_stages = set()
        set_subsequent_satge_mode(self.root_stage)

    def get_status_dict(self) -> dict:
        return {
            stage.stage_name: {
                **stage.get_status_snapshot(),
                "tasks_pending": self.stage_queues_dict[stage_tag].qsize() if stage_tag in self.stage_queues_dict else 0,
            }
            for stage_tag, stage in self.get_stage_dict().items()
        }

    def start_tree(self, init_tasks):
        start_time = time()
        structure_list = self.format_structure_list()
        task_logger.start_tree(structure_list)

        self.init_env(init_tasks)
        self._execute_stage(self.root_stage, set())

        # 等待所有进程结束
        for p in self.processes:
            p.join()
            task_logger.logger.debug(f"{p.name} exitcode: {p.exitcode}")

        self.process_final_result_dict(init_tasks)
        self.handle_final_error_dict()
        self.save_failures()
        self.release_resources()

        task_logger.end_tree(time() - start_time)

    def _execute_stage(self, stage: TaskManager, stage_visited: set):
        """
        递归地执行节点任务
        """
        stage_visited.add(stage)
        input_queue = self.stage_queues_dict[stage.get_stage_tag()]
        if not stage.next_stages:
            output_queues = []
        else:
            output_queues = [
                self.stage_queues_dict[next_stage.get_stage_tag()]
                for next_stage in stage.next_stages
            ]
        fail_queue = None # 先在stage内部自建ThreadQueue, 以避免fail_queue不消费导致缓冲区填满

        if stage.stage_mode == "process":
            stage.init_shared_status(self.status_manager.Namespace())
            stage.init_dict(self.manager.dict(), self.manager.dict())
            p = multiprocessing.Process(
                target=stage.start_stage, args=(input_queue, output_queues, fail_queue), name=stage.get_stage_tag()
            )
            p.start()
            self.processes.append(p)
        else:
            stage.init_dict({}, {})
            stage.start_stage(input_queue, output_queues, fail_queue)

        for next_stage in stage.next_stages:
            if next_stage in stage_visited:
                continue
            self._execute_stage(next_stage, stage_visited)

    def release_resources(self):
        """
        释放资源
        """

        def clean_stage(stage: TaskManager):
            stage.clean_env()
            visited_stages.add(stage)
            for next_stage in stage.next_stages:
                if next_stage in visited_stages:
                    continue
                clean_stage(next_stage)

        # 关闭 multiprocessing.Manager
        if self.manager is not None:
            self.manager.shutdown()

        # 确保所有进程已被正确终止
        for p in self.processes:
            if p.is_alive():
                p.terminate()  # 如果进程仍在运行，强制终止
            p.join()  # 确保进程终止

        # 关闭所有stage的线程池
        visited_stages = set()
        clean_stage(self.root_stage)

    def process_final_result_dict(self, initial_tasks):
        """
        查找对应的初始任务并更新 final_result_dict

        :param initial_tasks: 一个包含初始任务的列表
        """

        def update_final_result_dict(stage_task, stage: TaskManager):
            stage_success_dict = stage.get_success_dict()
            stage_error_dict = stage.get_error_dict()
            visited_stages.add(stage)

            final_list = []
            if stage_task in stage_success_dict:
                stage_task = stage_success_dict[stage_task]
            elif stage_task in stage_error_dict:
                stage_task = stage_error_dict[stage_task]
                task_execution_status[initial_task] = False
                return [(stage_task, stage.get_stage_tag())]
            else:
                dispear_exception = TaskError(f"({stage_task}) not found.")
                task_execution_status[initial_task] = False
                return [(dispear_exception, stage.get_stage_tag())]

            if not stage.next_stages:
                return [(stage_task, stage.get_stage_tag())]

            for next_stage in stage.next_stages:
                if next_stage in visited_stages:
                    continue
                elif not isinstance(stage, TaskSplitter):
                    next_stage_final_list = update_final_result_dict(
                        stage_task, next_stage
                    )
                    final_list.extend(next_stage_final_list)
                    continue

                # 如果是 TaskSplitter，则递归处理每个子任务
                for split_task in stage_task:
                    next_stage_final_list = update_final_result_dict(
                        split_task, next_stage
                    )
                    final_list.extend(next_stage_final_list)

            return final_list

        task_execution_status = {}
        for initial_task in initial_tasks:
            visited_stages = set()
            task_execution_status[initial_task] = True
            self.final_result_dict[initial_task] = update_final_result_dict(
                initial_task, self.root_stage
            )
        self.failed_tasks = [
            task for task, pass_flag in task_execution_status.items() if not pass_flag
        ]

    def handle_final_error_dict(self):
        """
        处理最终错误字典
        """

        def update_error_dict(stage: TaskManager):
            stage_error_dict = stage.get_error_dict()
            visited_stages.add(stage)
            for task, error in stage_error_dict.items():
                error_key = (f"{type(error).__name__}({error})", stage.get_stage_tag())
                self.final_error_dict[error_key].append(task)
                self.final_fail_dict[stage.get_stage_tag()].append(task)
            for next_stage in stage.next_stages:
                if next_stage in visited_stages:
                    continue
                update_error_dict(next_stage)

        visited_stages = set()
        update_error_dict(self.root_stage)

    def get_stage_dict(self):
        """
        返回节点字典
        """
        return self.stage_dict

    def get_final_result_dict(self):
        """
        返回最终结果字典
        """
        return self.final_result_dict

    def get_final_error_dict(self):
        """
        返回最终错误字典
        """
        return dict(self.final_error_dict)

    def get_final_fail_dict(self):
        """
        返回最终失败字典
        """
        return dict(self.final_fail_dict)

    def get_failed_tasks(self):
        """
        返回失败的任务列表
        """
        return self.failed_tasks

    def get_structure_list(
        self, task_manager: TaskManager, indent=0, visited_stages=None
    ):
        """
        递归生成任务链的打印列表
        :param task_manager: 当前处理的 TaskManager
        :param indent: 当前缩进级别
        :param visited_stages: 已访问的 TaskManager 集合，避免重复访问
        :return: 打印内容列表
        """
        visited_stages = visited_stages or set()
        scructure_list = []

        stage_info = f"{task_manager.stage_name} (stage_mode: {task_manager.stage_mode}, func: {task_manager.func.__name__})"

        # 防止重复访问
        if task_manager in visited_stages:
            scructure_list.append(f"{stage_info} (already visited)")
            return scructure_list

        # 打印当前 TaskManager
        visited_stages.add(task_manager)
        scructure_list.append(stage_info)

        # 遍历后续节点
        for next_stage in task_manager.next_stages:
            sub_scructure_list = self.get_structure_list(
                next_stage, indent + 2, visited_stages
            )
            scructure_list.append("  " * indent + "╘-->")
            scructure_list[-1] += sub_scructure_list[0]
            scructure_list.extend(sub_scructure_list[1:])

        return scructure_list

    def format_structure_list(self, task_manager=None):
        """
        格式化任务链的打印列表
        :param task_manager: 起始 TaskManager
        """
        task_manager = task_manager or self.root_stage
        structure_list = self.get_structure_list(task_manager, 0, set())

        # 找到最长行的宽度
        max_length = max(len(line) for line in structure_list)

        # 对每一行进行补齐
        formatted_list = [
            f"| {line.ljust(max_length)} |"  # 左对齐，首尾加 '|'
            for line in structure_list
        ]

        # 添加顶部和底部边框
        border = "+" + "-" * (max_length + 2) + "+"
        formatted_list = [border] + formatted_list + [border]

        return formatted_list

    def save_failures(self, path="./fallback", name=None):
        """
        保存失败信息到 JSON 文件
        :param path: 保存路径
        :param name: 文件名
        """
        path = Path(path) / datetime.now().strftime("%Y-%m-%d")
        path.mkdir(parents=True, exist_ok=True)

        structure = self.format_structure_list()
        timestamp = datetime.now().strftime("%H-%M-%S-%f")[:-3]
        chain_name = self.root_stage.stage_name  # 🧠 添加 task_chain_name

        data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "structure": structure,
            },
            "fail tasks": self.get_final_fail_dict(),
            "fail init tasks": self.get_failed_tasks(),
        }

        file_name = name or f"{timestamp}__{chain_name}.json"
        file_path = path / file_name

        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def test_methods(self, task_list: List[Any]) -> Dict[str, Any]:
        """
        测试 TaskTree 在 'serial' 和 'process' 模式下的执行时间。

        :param task_list: 任务列表
        :return: 包含两种执行模式下的执行时间的字典
        """
        results = {}
        test_table_list = []
        final_result_dict = {}
        final_error_dict = {}
        final_fail_dict = {}
        failed_tasks = []

        stage_modes = ["serial", "process"]
        execution_modes = ["serial", "thread"]
        for stage_mode in stage_modes:
            time_list = []
            for execution_mode in execution_modes:
                start_time = time()
                self.set_tree_mode(stage_mode, execution_mode)
                self.start_tree(task_list)

                time_list.append(time() - start_time)
                final_result_dict.update(self.get_final_result_dict())
                final_error_dict.update(self.get_final_error_dict())
                final_fail_dict.update(self.get_final_fail_dict())
                failed_tasks += [
                    task for task in self.get_failed_tasks() if task not in failed_tasks
                ]

            test_table_list.append(time_list)

        results["Time table"] = (
            test_table_list,
            execution_modes,
            stage_modes,
            r"stage\execution",
        )
        results["Final result dict"] = final_result_dict
        results["Final error dict"] = final_error_dict
        results["Final fail dict"] = final_fail_dict
        results["Failed tasks"] = failed_tasks
        return results


class TaskChain(TaskTree):
    def __init__(self, stages: List[TaskManager], chain_mode: str = "serial", start_web_server=False):
        """
        初始化 TaskChain
        :param stages: TaskManager 列表
        :param chain_mode: 链式模式，默认为 'serial'
        """
        for num, stage in enumerate(stages):
            stage_name = f"Stage {num + 1}"
            next_stage = [stages[num + 1]] if num < len(stages) - 1 else []
            stage.set_tree_context(next_stage, chain_mode, stage_name)

        root_stage = stages[0]
        super().__init__(root_stage, start_web_server)
