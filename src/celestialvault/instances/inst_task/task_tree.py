import json, time
import multiprocessing
from collections import defaultdict
from datetime import datetime
from multiprocessing import Value as MPValue, Lock as MPLock
from multiprocessing import Queue as MPQueue
from pathlib import Path
from typing import Any, Dict, List

from .task_manage import TaskManager
from .task_nodes import TaskSplitter
from .task_support import TERMINATION_SIGNAL, TaskError, TaskReporter, LogListener, TaskLogger, counter
from .task_tools import format_duration, format_timestamp, cleanup_mpqueue


class TaskTree:
    def __init__(self, root_stage: TaskManager):
        """
        :param root_stage: 任务链的根 TaskManager 节点
        :param start_web_server: 是否启动 web 服务
        """
        self.init_dict()
        self.init_fail_queue()
        self.init_log()
        self.set_root_stage(root_stage)

        self.init_tasks_num = {}
        self.set_reporter()

    def init_env(self, init_tasks_dict: dict):
        """
        初始化环境
        """
        self.processes: List[multiprocessing.Process] = []
        # self.manager = multiprocessing.Manager()

        self.init_dict()
        self.init_task_queues(init_tasks_dict)
        self.init_fail_queue()

    def init_dict(self):
        """
        初始化字典
        """
        self.stages_status_dict: Dict[str, dict] = defaultdict(dict)
        self.stage_locks = {}  # 可选的锁，用于控制每个阶段的并发数
        self.stage_success_counter = {}  # 用于保存每个阶段成功处理的任务数
        self.stage_extra_stats = defaultdict(dict) # 用于保存每个阶段的额外统计信息
        
        self.final_result_dict = {}  # 用于保存初始任务到最终结果的映射
        self.error_timeline_dict: Dict[str, list] = defaultdict(list)  # 用于保存错误到出现该错误任务的映射
        self.all_stage_error_dict: Dict[str, dict] = defaultdict(dict)  # 用于保存节点到节点失败任务的映射

    def init_task_queues(self, init_tasks_dict: dict):
        """
        初始化任务队列
        :param tasks: 待处理的任务列表
        """

        def collect_queue(stage: TaskManager):
            # 为每个节点创建队列
            stage_tag = stage.get_stage_tag()
            self.stages_status_dict[stage_tag]["stage"] = stage
            self.stages_status_dict[stage_tag]["task_queue"] = MPQueue()

            visited_stages.add(stage_tag)

            for next_stage in stage.next_stages:
                if next_stage.get_stage_tag() in visited_stages:
                    continue
                collect_queue(next_stage)

        # 初始化每个节点的队列
        visited_stages = set()
        collect_queue(self.root_stage)
        self.fail_queue = MPQueue()
        root_stage_tag = self.root_stage.get_stage_tag()

        self.init_tasks_num = {}
        for tag, tasks in init_tasks_dict.items():
            for task in tasks:
                self.stages_status_dict[tag]["task_queue"].put(task)
                self.init_tasks_num[tag] = self.init_tasks_num.get(tag, 0) + 1
        self.stages_status_dict[root_stage_tag]["task_queue"].put(TERMINATION_SIGNAL)

    def init_fail_queue(self):
        """
        初始化失败队列
        """
        self.fail_queue = MPQueue()

    def init_log(self):
        """
        初始化日志
        """
        self.log_listener = LogListener(level = "INFO")
        self.task_logger = TaskLogger(self.log_listener.get_queue())

    def set_root_stage(self, root_stage: TaskManager):
        """
        设定根节点
        """
        self.root_stage = root_stage
        self.root_stage.set_prev_stage(None)

    def set_reporter(self, is_report=False, host="127.0.0.1", port=5000):
        """
        设定报告器
        """
        self.is_report = is_report
        self.reporter = TaskReporter(self, self.log_listener.get_queue(), host, port)

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

    def start_tree(self, init_tasks_dict: dict):
        """
        启动任务链
        """
        self.log_listener.start()
        self.start_time = time.time()
        structure_list = self.format_structure_list_from_tree()
        self.task_logger.start_tree(structure_list)
        self._persist_structure_metadata()
        self.reporter.start() if self.is_report else None

        self.init_env(init_tasks_dict)
        self._execute_stage(self.root_stage, set())

        # 等待所有进程结束
        for p in self.processes:
            p.join()
            self.stages_status_dict[p.name]["is_active"] = False
            self.task_logger._log("DEBUG", f"{p.name} exitcode: {p.exitcode}")

        self.reporter.stop()
        self.handle_fail_queue()
        self.release_resources()

        self.task_logger.end_tree(time.time() - self.start_time)
        self.log_listener.stop()

    def _execute_stage(self, stage: TaskManager, stage_visited: set):
        """
        递归地执行节点任务
        """
        stage_tag = stage.get_stage_tag()
        stage_visited.add(stage_tag)

        input_queue = self.stages_status_dict[stage_tag]["task_queue"]
        if not stage.next_stages:
            output_queues = []
        else:
            output_queues = [
                self.stages_status_dict[next_stage.get_stage_tag()]["task_queue"]
                for next_stage in stage.next_stages
            ]
        logger_queue = self.log_listener.get_queue()

        self.stages_status_dict[stage_tag]["is_active"] = True
        self.stages_status_dict[stage_tag]["start_time"] = time.time()

        if isinstance(stage, TaskSplitter):
            self.stage_extra_stats[stage_tag]["split_output_count"] = MPValue("i", 0)
        else:
            self.stage_extra_stats[stage_tag] = {}

        if stage.stage_mode == "process":
            self.stage_success_counter[stage_tag] = MPValue("i", 0)
            self.stage_locks[stage_tag] = MPLock()

            stage.init_dict(
                {}, 
                self.stage_success_counter[stage_tag],
                self.stage_locks[stage_tag],
                self.stage_extra_stats[stage_tag]
                )
            p = multiprocessing.Process(
                target=stage.start_stage, args=(input_queue, output_queues, self.fail_queue, logger_queue), name=stage_tag
            )
            p.start()
            self.processes.append(p)
        else:
            self.stage_success_counter[stage_tag] = counter

            stage.init_dict(
                {}, 
                self.stage_success_counter[stage_tag], 
                None, 
                self.stage_extra_stats[stage_tag]
                )
            stage.start_stage(input_queue, output_queues, self.fail_queue, logger_queue)

            self.stages_status_dict[stage_tag]["is_active"]  = False

        for next_stage in stage.next_stages:
            if next_stage.get_stage_tag() in stage_visited:
                continue
            self._execute_stage(next_stage, stage_visited)

    def release_resources(self):
        """
        释放资源
        """

        for stage_status_dict in self.stages_status_dict.values():
            stage_status_dict["stage"].release_queue()

        cleanup_mpqueue(self.fail_queue)
        
    def process_final_result_dict(self, initial_tasks):
        """
        查找对应的初始任务并更新 final_result_dict

        :param initial_tasks: 一个包含初始任务的列表
        """

        def update_final_result_dict(stage_task, stage: TaskManager):
            stage_success_dict = stage.get_success_dict()
            stage_error_dict = all_stage_error_dict.get(stage.get_stage_tag(), {})
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
        all_stage_error_dict = self.get_all_stage_error_dict()
        for initial_task in initial_tasks:
            visited_stages = set()
            task_execution_status[initial_task] = True
            self.final_result_dict[initial_task] = update_final_result_dict(
                initial_task, self.root_stage
            )

    def handle_fail_queue(self):
        """
        消费 fail_queue, 构建失败字典
        """
        while not self.fail_queue.empty():
            item: dict = self.fail_queue.get_nowait()
            stage_tag = item["stage_tag"]
            task_str = item["task"]
            error_info = item["error_info"]
            timestamp = item["timestamp"]
            error_key = (error_info, stage_tag)

            if task_str not in self.error_timeline_dict[error_key]:
                self.error_timeline_dict[error_key].append((task_str, timestamp))

            if task_str not in self.all_stage_error_dict[stage_tag]:
                self.all_stage_error_dict[stage_tag][task_str] = error_key

            self._persist_single_failure(task_str, error_info, stage_tag, timestamp)

    def _persist_single_failure(self, task_str, error_info, stage_tag, timestamp, path="./fallback"):
        """
        增量写入单条错误日志到每日文件中
        """
        try:
            date_str = datetime.fromtimestamp(self.start_time).strftime("%Y-%m-%d")
            time_str = datetime.fromtimestamp(self.start_time).strftime("%H-%M-%S-%f")[:-3]
            file_path = Path(path) / date_str / f"realtime_errors({time_str}).jsonl"
            file_path.parent.mkdir(parents=True, exist_ok=True)

            log_item = {
                "timestamp": datetime.fromtimestamp(timestamp).isoformat(),
                "stage": stage_tag,
                "error": error_info,
                "task": task_str,
            }

            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_item, ensure_ascii=False) + "\n")
        except Exception as e:
            self.task_logger._log("WARNING",f"[Persist] 写入实时错误日志失败: {e}")

    def _persist_structure_metadata(self, path="./fallback"):
        """
        在运行开始时写入任务结构元信息到 jsonl 文件
        """
        try:
            date_str = datetime.fromtimestamp(self.start_time).strftime("%Y-%m-%d")
            time_str = datetime.fromtimestamp(self.start_time).strftime("%H-%M-%S-%f")[:-3]
            file_path = Path(path) / date_str / f"realtime_errors({time_str}).jsonl"
            file_path.parent.mkdir(parents=True, exist_ok=True)

            log_item = {
                "timestamp": datetime.now().isoformat(),
                "structure": self.get_structure_tree(self.root_stage),
            }

            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_item, ensure_ascii=False) + "\n")
        except Exception as e:
            self.task_logger._log("WARNING",f"[Persist] 写入结构失败: {e}")

    def get_stages_status_dict(self):
        """
        返回节点状态字典
        """
        return dict(self.stages_status_dict)

    def get_final_result_dict(self):
        """
        返回最终结果字典
        """
        return self.final_result_dict

    def get_error_timeline_dict(self):
        """
        返回最终错误字典
        """
        return dict(self.error_timeline_dict)

    def get_all_stage_error_dict(self):
        """
        返回最终失败字典
        """
        return dict(self.all_stage_error_dict)
    
    def get_fail_by_error_dict(self):
        return {
            key: [a for a, _ in tuple_list]
            for key, tuple_list in self.get_error_timeline_dict().items()
        }

    def get_fail_by_stage_dict(self):
        return {
            stage: list(inner_dict.keys())
            for stage, inner_dict in self.get_all_stage_error_dict().items()
        }
    
    def get_status_dict(self) -> dict:
        """
        获取任务链的状态字典
        """
        status_dict = {}
        now = time.time()
        all_stage_error_dict = self.get_all_stage_error_dict()

        for tag, stage_status_dict in self.stages_status_dict.items():
            stage: TaskManager = stage_status_dict["stage"]
            prev = stage.prev_stage
            prev_tag = prev.get_stage_tag() if prev else None

            total_input = self.init_tasks_num.get(tag, 0)
            if prev:
                if isinstance(prev, TaskSplitter):
                    total_input += self.stage_extra_stats[prev_tag].get("split_output_count", counter).value
                else:
                    total_input += status_dict[prev_tag]["tasks_processed"] 

            is_active = stage_status_dict.get("is_active", False)
            processed = self.stage_success_counter.get(tag, counter).value
            failed = len(all_stage_error_dict.get(tag, {}))
            pending = max(0, total_input - processed - failed)

            start_time = stage_status_dict.get("start_time", 0)
            last_update_time = stage_status_dict.get("update_time", now)
            stage_is_pending_in_last_time = stage_status_dict.get("is_pending", False)

            stage_status_dict["is_pending"] = True if pending else False

            # 更新时间消耗（仅在 pending 非 0 时刷新）
            if start_time:
                elapsed = stage_status_dict.get("elapsed_time", 0)
                # 如果上一次是 pending，则累计时间
                if stage_is_pending_in_last_time:
                    # 如果上一次活跃, 那么无论当前状况，累计从上一次更新时间到现在的时间
                    elapsed += now - last_update_time
                    # 更新最后更新时间
                    stage_status_dict["update_time"] = now
            else:
                elapsed = 0

            stage_status_dict["elapsed_time"] = elapsed

            # 计算平均时间（秒/任务）并格式化为字符串
            if processed or failed:
                avg_time = elapsed / (processed + failed)
                if avg_time >= 1.0:
                    # 显示 "X.XX s/it"
                    avg_time_str = f"{avg_time:.2f}s/it"
                else:
                    # 显示 "X.XX it/s"（取倒数）
                    its_per_sec = (processed + failed) / elapsed if elapsed else 0
                    avg_time_str = f"{its_per_sec:.2f}it/s"
            else:
                avg_time_str = "N/A"  # 或 "0.00s/it" 根据需求

            # 估算剩余时间
            remaining = (elapsed / (processed + failed) * pending) if (processed or failed) and pending else 0

            status_dict[tag] = {
                **stage.get_status_snapshot(),
                "active": is_active,
                "tasks_processed": processed,
                "tasks_error": failed,
                "tasks_pending": pending,
                "start_time": format_timestamp(start_time),
                "elapsed_time": format_duration(elapsed),
                "remaining_time": format_duration(remaining),
                "task_avg_time": avg_time_str,  # 新增字段
            }

        return status_dict

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

        if task_manager.get_stage_tag() in visited_stages:
            node["visited"] = True
            return node

        visited_stages.add(task_manager.get_stage_tag())

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

        stage_modes = ["serial", "process"]
        execution_modes = ["serial", "thread"]
        for stage_mode in stage_modes:
            time_list = []
            for execution_mode in execution_modes:
                start_time = time.time()
                self.init_log()
                self.set_tree_mode(stage_mode, execution_mode)
                self.start_tree(task_list)

                time_list.append(time.time() - start_time)
                final_result_dict.update(self.get_final_result_dict())
                fail_by_error_dict.update(self.get_fail_by_error_dict())
                fail_by_stage_dict.update(self.get_fail_by_stage_dict())

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
