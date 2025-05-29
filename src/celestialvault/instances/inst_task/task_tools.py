
import json, ast
from collections import defaultdict
from datetime import datetime
from multiprocessing import Queue as MPQueue
from asyncio import Queue as AsyncQueue
from queue import Queue as ThreadQueue
from queue import Empty
from asyncio import QueueEmpty as AsyncQueueEmpty


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
