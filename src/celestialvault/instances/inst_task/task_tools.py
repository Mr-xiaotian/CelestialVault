import json, ast
from collections import defaultdict
from datetime import datetime
from multiprocessing import Queue as MPQueue
from asyncio import Queue as AsyncQueue
from queue import Queue as ThreadQueue
from pathlib import Path
from queue import Empty
from asyncio import QueueEmpty as AsyncQueueEmpty
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from .task_manage import TaskManager  # 或者用绝对路径，例如 from task_tree.task_manage import TaskManager


def format_duration(seconds):
    """将秒数格式化为 HH:MM:SS 或 MM:SS（自动省略前导零）"""
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def format_timestamp(timestamp) -> str:
    """将时间戳格式化为 YYYY-MM-DD HH:MM:SS"""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def cleanup_mpqueue(queue: MPQueue):
    """
    清理队列
    """
    queue.close()
    queue.join_thread()  # 确保队列的后台线程正确终止

def load_error_by_stage(jsonl_path):
    """
    加载错误记录，按 stage 分类
    """
    stage_dict = defaultdict(list)
    with open(jsonl_path, "r") as f:
        for line in f:
            item = json.loads(line)
            if "error" not in item or "stage" not in item:
                continue  # 跳过结构条或非错误记录
            
            task = ast.literal_eval(item["task"])
            stage_dict[item["stage"]].append(task)

    return dict(stage_dict)

def load_error_by_type(jsonl_path):
    """
    加载错误记录，按 error 和 stage 分类
    """
    type_dict = defaultdict(list)
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            if "error" not in item or "stage" not in item:
                continue  # 跳过结构条或非错误记录

            error = item["error"]
            stage = item["stage"]
            task = ast.literal_eval(item["task"])
            key = f"({error}, {stage})"
            type_dict[key].append(task)
            
    return dict(type_dict)

def is_queue_empty(q: ThreadQueue) -> bool:
    """
    判断队列是否为空
    """
    try:
        item = q.get_nowait()
        q.put(item)  # optional: put it back
        return False
    except Empty:
        return True
    
async def is_queue_empty_async(q: AsyncQueue) -> bool:
    """
    判断队列是否为空
    """
    try:
        item = q.get_nowait()
        await q.put(item)  # ✅ 修复点
        return False
    except AsyncQueueEmpty:
        return True
    
def make_hashable(obj):
    """
    把 obj 转换成可哈希的形式。
    """
    if isinstance(obj, (tuple, list)):
        return tuple(make_hashable(e) for e in obj)
    elif isinstance(obj, dict):
        # dict 转换成 (key, value) 对的元组，且按 key 排序以确保哈希结果一致
        return tuple(sorted((make_hashable(k), make_hashable(v)) for k, v in obj.items()))
    elif isinstance(obj, set):
        # set 转换成排序后的 tuple
        return tuple(sorted(make_hashable(e) for e in obj))
    else:
        # 基本类型直接返回
        return obj

def build_structure_tree(task_manager: "TaskManager", visited_stages=None) -> Dict[str, Any]:
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
        child_node = build_structure_tree(next_stage, visited_stages)
        node["next_stages"].append(child_node)

    return node

def format_structure_list_from_tree(root_root: dict = None, indent=0) -> list:
    """
    从 JSON 树结构直接生成带边框的格式化任务结构文本列表
    :param root_root: JSON 格式任务树根节点
    :param indent: 当前缩进级别
    :return: 带边框的格式化字符串列表
    """

    def build_lines(node: dict, current_indent: int):
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
    raw_lines = build_lines(root_root, indent)

    # 计算最大行宽
    max_length = max(len(line) for line in raw_lines)

    # 包装为表格形式
    content_lines = [f"| {line.ljust(max_length)} |" for line in raw_lines]
    border = "+" + "-" * (max_length + 2) + "+"
    return [border] + content_lines + [border]

def append_jsonl_log(log_data: dict, start_time: float, base_path: str, prefix: str, logger=None):
    """
    将日志字典写入指定目录下的 JSONL 文件。

    :param log_data: 要写入的日志项（字典）
    :param start_time: 运行开始时间，用于构造路径
    :param base_path: 基础路径，例如 './fallback'
    :param prefix: 文件名前缀，例如 'realtime_errors'
    :param logger: 可选的日志对象用于记录失败信息
    """
    try:
        date_str = datetime.fromtimestamp(start_time).strftime("%Y-%m-%d")
        time_str = datetime.fromtimestamp(start_time).strftime("%H-%M-%S-%f")[:-3]
        file_path = Path(base_path) / date_str / f"{prefix}({time_str}).jsonl"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
    except Exception as e:
        if logger:
            logger._log("WARNING", f"[Persist] 写入日志失败: {e}")
