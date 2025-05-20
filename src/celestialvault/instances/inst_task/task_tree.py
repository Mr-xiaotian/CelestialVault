import json, time, requests
import multiprocessing
import threading
from collections import defaultdict
from datetime import datetime
from multiprocessing import Queue as MPQueue
from pathlib import Path
from typing import Any, Dict, List

from .task_manage import TaskManager
from .task_nodes import TaskSplitter
from .task_support import TERMINATION_SIGNAL, TaskError, task_logger


class TaskTree:
    def __init__(self, root_stage: TaskManager):
        """
        :param root_stage: 任务链的根 TaskManager 节点
        :param start_web_server: 是否启动 web 服务
        """
        self.set_root_stage(root_stage)
        self.init_dict()

        self._report_thread = None
        self._report_stop_flag = threading.Event()

    def init_env(self, tasks: list):
        """
        初始化环境
        """
        self.processes: List[multiprocessing.Process] = []
        self.manager = multiprocessing.Manager()

        self.init_dict()
        self.init_queues(tasks)

    def init_dict(self):
        """
        初始化字典
        """
        self.stage_dict: Dict[str, TaskManager] = {}
        self.stage_active_dict: Dict[str, bool] = {}
        self.stage_queues_dict: Dict[str, MPQueue] = {}
        self.stage_start_time_dict: Dict[str, float] = {}
        self.stage_elapsed_time_dict: Dict[str, float] = {}
        self.stage_update_time_dict: Dict[str, float] = {}
        self.stage_is_pending_dict: Dict[str, bool] = {}
        
        self.final_result_dict = {}  # 用于保存初始任务到最终结果的映射
        self.fail_task_time_dict = {}  # 用于保存失败任务到失败时间的映射(不精确)
        self.fail_by_error_dict = defaultdict(list)  # 用于保存错误到出现该错误任务的映射
        self.fail_by_stage_dict = defaultdict(list)  # 用于保存节点到节点失败任务的映射

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

        self.init_tasks_num = 0
        for task in tasks:
            self.stage_queues_dict[self.root_stage.get_stage_tag()].put(task)
            self.init_tasks_num += 1
        self.stage_queues_dict[self.root_stage.get_stage_tag()].put(TERMINATION_SIGNAL)

    def set_root_stage(self, root_stage: TaskManager):
        """
        设定根节点
        """
        self.root_stage = root_stage
        self.root_stage.set_prev_stage(None)

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

    def format_duration(self, seconds):
        """将秒数格式化为 HH:MM:SS 或 MM:SS（自动省略前导零）"""
        seconds = int(seconds)
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

    def format_timestamp(self, timestamp) -> str:
        """将时间戳格式化为 YYYY-MM-DD HH:MM:SS"""
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    def get_status_dict(self) -> dict:
        """
        获取任务链的状态字典
        """
        status_dict = {}
        now = time.time()

        for tag, stage in self.get_stage_dict().items():
            prev = stage.prev_stage

            total_input = (
                sum(len(v) for v in prev.success_dict.values()) if isinstance(prev, TaskSplitter)
                else len(prev.success_dict) if prev
                else self.init_tasks_num
            )

            processed = len(stage.success_dict)
            failed = len(stage.error_dict)
            pending = max(0, total_input - processed - failed)

            start_time = self.stage_start_time_dict.get(tag, 0)
            is_active = self.stage_active_dict.get(tag, False)
            last_update_time = self.stage_update_time_dict.get(tag, now)
            stage_is_pending_last_time = self.stage_is_pending_dict.get(tag, False)

            self.stage_is_pending_dict[tag] = True if pending else False

            # 更新时间消耗（仅在 pending 非 0 时刷新）
            if start_time:
                elapsed = self.stage_elapsed_time_dict.get(tag, 0)
                if pending and stage_is_pending_last_time:
                    # 有pending任务时，累计从上一次更新时间到现在的时间
                    elapsed += now - last_update_time
                    # 更新最后更新时间
                    self.stage_update_time_dict[tag] = now
            else:
                elapsed = 0

            self.stage_elapsed_time_dict[tag] = elapsed

            # 估算剩余时间
            remaining = (elapsed / processed * pending) if processed and pending else 0

            status_dict[tag] = {
                **stage.get_status_snapshot(),
                "active": is_active,
                "tasks_pending": pending,
                "start_time": self.format_timestamp(start_time),
                "elapsed_time": self.format_duration(elapsed),
                "remaining_time": self.format_duration(remaining),
            }

        return status_dict

    def start_tree(self, init_tasks):
        start_time = time.time()
        structure_list = self.format_structure_list_from_tree()
        task_logger.start_tree(structure_list)

        self.init_env(init_tasks)
        self._execute_stage(self.root_stage, set())

        # 等待所有进程结束
        for p in self.processes:
            p.join()
            self.stage_active_dict[p.name] = False
            task_logger.logger.debug(f"{p.name} exitcode: {p.exitcode}")

        self.stop_reporter()
        self.process_final_result_dict(init_tasks)
        self.handle_final_error_dict()
        self.save_failures()
        self.release_resources()

        task_logger.end_tree(time.time() - start_time)

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
            self.stage_active_dict[stage.get_stage_tag()] = True
            self.stage_start_time_dict[stage.get_stage_tag()] = time.time()

            stage.init_dict(self.manager.dict(), self.manager.dict())
            p = multiprocessing.Process(
                target=stage.start_stage, args=(input_queue, output_queues, fail_queue), name=stage.get_stage_tag()
            )
            p.start()
            self.processes.append(p)
        else:
            self.stage_active_dict[stage.get_stage_tag()] = True
            self.stage_start_time_dict[stage.get_stage_tag()] = time.time()

            stage.init_dict({}, {})
            stage.start_stage(input_queue, output_queues, fail_queue)

            self.stage_active_dict[stage.get_stage_tag()] = False

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
            stage.success_dict = stage.get_success_dict()
            stage.error_dict = stage.get_error_dict()

            visited_stages.add(stage)
            for next_stage in stage.next_stages:
                if next_stage in visited_stages:
                    continue
                clean_stage(next_stage)

        # 确保所有进程已被正确终止
        for p in self.processes:
            if p.is_alive():
                p.terminate()  # 如果进程仍在运行，强制终止
            p.join()  # 确保进程终止

        # 关闭所有stage的线程池
        visited_stages = set()
        clean_stage(self.root_stage)

        # 关闭 multiprocessing.Manager
        if self.manager is not None:
            self.manager.shutdown()

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

        for stage_tag, stage in self.stage_dict.items():
            stage_error_dict = stage.get_error_dict()
            for task, error in stage_error_dict.items():
                error_key = (f"{type(error).__name__}({error})", stage_tag)
                self.fail_by_error_dict[error_key].append(task) if task not in self.fail_by_error_dict[error_key] else None
                self.fail_by_stage_dict[stage_tag].append(task) if task not in self.fail_by_stage_dict[stage_tag] else None

                if task not in self.fail_task_time_dict:
                    self.fail_task_time_dict[task] = time.time()

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

    def get_fail_by_error_dict(self):
        """
        返回最终错误字典
        """
        return dict(self.fail_by_error_dict)

    def get_fail_by_stage_dict(self):
        """
        返回最终失败字典
        """
        return dict(self.fail_by_stage_dict)

    def get_failed_tasks(self):
        """
        返回失败的任务列表
        """
        return self.failed_tasks
    
    def start_reporter(self, interval=5, web_host="127.0.0.1", web_port=5000):
        def loop():
            while not self._report_stop_flag.is_set():
                try:
                    self._report_once(web_host, web_port)
                except Exception as e:
                    print(f"[Reporter] Error during push: {e}")
                self._report_stop_flag.wait(interval)  # 替代 time.sleep

        if self._report_thread is None or not self._report_thread.is_alive():
            self._report_structure_once(web_host, web_port)  # ✅ 只发一次
            
            self._report_stop_flag = threading.Event()  
            self._report_stop_flag.clear()
            self._report_thread = threading.Thread(target=loop, daemon=True)
            self._report_thread.start()

    def stop_reporter(self):
        if self._report_thread:
            self._report_once() # 发送最后一次
            self._report_stop_flag.set()
            self._report_thread.join(timeout=2)
            self._report_thread = None

    def _report_structure_once(self, host="127.0.0.1", port=5000):
        structure = self.get_structure_tree(self.root_stage)
        try:
            requests.post(f"http://{host}:{port}/api/push_structure", json=structure, timeout=1)
        except Exception as e:
            print(f"[Reporter] Failed to push structure: {e}")

    def _report_once(self, host="127.0.0.1", port=5000):
        base_url = f"http://{host}:{port}"

        # 上报状态
        status_data = self.get_status_dict()
        requests.post(f"{base_url}/api/push_status", json=status_data, timeout=1)

        # 上报错误
        error_data = []
        self.handle_final_error_dict()
        for (err, tag), task_list in self.get_fail_by_error_dict().items():
            for task in task_list:
                error_data.append({
                    "error": err,
                    "node": tag,
                    "task_id": str(task),
                    "timestamp": self.fail_task_time_dict.get(task),
                })
        requests.post(f"{base_url}/api/push_errors", json=error_data, timeout=1)

    def get_structure_tree(self, task_manager: TaskManager, visited_stages=None):
        """
        构建任务链的 JSON 树结构
        :param task_manager: 当前处理的 TaskManager
        :param visited_stages: 已访问的 TaskManager 集合，避免重复访问
        :return: JSON 结构的任务树
        """
        visited_stages = visited_stages or set()

        node = {
            "stage_name": task_manager.stage_name,
            "stage_mode": task_manager.stage_mode,
            "func_name": task_manager.func.__name__,
            "visited": False,
            "next_stages": []
        }

        if task_manager in visited_stages:
            node["visited"] = True
            return node

        visited_stages.add(task_manager)

        for next_stage in task_manager.next_stages:
            child_node = self.get_structure_tree(next_stage, visited_stages)
            node["next_stages"].append(child_node)

        return node
    
    def format_structure_list_from_tree(self, tree_root: dict = None, indent=0):
        """
        从 JSON 树结构直接生成带边框的格式化任务结构文本列表
        :param tree_root: JSON 格式任务树根节点
        :param indent: 当前缩进级别
        :return: 带边框的格式化字符串列表
        """

        def build_lines(node, current_indent):
            lines = []

            # 构建当前节点的行文本
            visited_note = " (already visited)" if node.get("visited") else ""
            line = f"{node['stage_name']} (stage_mode: {node['stage_mode']}, func: {node['func_name']}){visited_note}"
            lines.append(line)

            # 递归处理子节点
            for child in node.get("next_stages", []):
                sub_lines = build_lines(child, current_indent + 2)
                arrow_prefix = "  " * current_indent + "╘-->"
                sub_lines[0] = f"{arrow_prefix}{sub_lines[0]}"
                lines.extend(sub_lines)

            return lines

        # 构建原始行列表
        tree_root = tree_root or self.get_structure_tree(self.root_stage)
        raw_lines = build_lines(tree_root, indent)

        # 计算最大行宽
        max_length = max(len(line) for line in raw_lines)

        # 包装为表格形式
        content_lines = [f"| {line.ljust(max_length)} |" for line in raw_lines]
        border = "+" + "-" * (max_length + 2) + "+"
        return [border] + content_lines + [border]

    def save_failures(self, path="./fallback", name=None):
        """
        保存失败信息到 JSON 文件
        :param path: 保存路径
        :param name: 文件名
        """
        path = Path(path) / datetime.now().strftime("%Y-%m-%d")
        path.mkdir(parents=True, exist_ok=True)

        structure = self.format_structure_list_from_tree()
        timestamp = datetime.now().strftime("%H-%M-%S-%f")[:-3]
        chain_name = self.root_stage.stage_name

        data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "structure": structure,
            },
            "fail stages": self.get_fail_by_stage_dict(),
            "fail errors": {str(key): value for key, value in self.get_fail_by_error_dict().items()},
            "fail tasks": self.get_failed_tasks(),
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
        fail_by_error_dict = {}
        fail_by_stage_dict = {}
        failed_tasks = []

        stage_modes = ["serial", "process"]
        execution_modes = ["serial", "thread"]
        for stage_mode in stage_modes:
            time_list = []
            for execution_mode in execution_modes:
                start_time = time.time()
                self.set_tree_mode(stage_mode, execution_mode)
                self.start_tree(task_list)

                time_list.append(time.time() - start_time)
                final_result_dict.update(self.get_final_result_dict())
                fail_by_error_dict.update(self.get_fail_by_error_dict())
                fail_by_stage_dict.update(self.get_fail_by_stage_dict())
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
        results["Fail error dict"] = fail_by_error_dict
        results["Fail stage dict"] = fail_by_stage_dict
        results["Fail tasks"] = failed_tasks
        return results


class TaskChain(TaskTree):
    def __init__(self, stages: List[TaskManager], chain_mode: str = "serial"):
        """
        初始化 TaskChain
        :param stages: TaskManager 列表
        :param chain_mode: 链式模式，默认为 'serial'
        """
        for num, stage in enumerate(stages):
            stage_name = f"Stage {num + 1}"
            next_stages = [stages[num + 1]] if num < len(stages) - 1 else []
            stage.set_tree_context(next_stages, chain_mode, stage_name)

        root_stage = stages[0]
        super().__init__(root_stage)

    def start_chain(self, task_list: List[Any]):
        """
        启动任务链
        :param task_list: 任务列表
        """
        self.start_tree(task_list)
