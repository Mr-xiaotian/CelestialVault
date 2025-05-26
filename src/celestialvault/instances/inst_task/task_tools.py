
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
    stage_dict = defaultdict(list)
    with open(jsonl_path, "r") as f:
        for line in f:
            item = json.loads(line)
            if "error" not in item or "stage" not in item:
                continue  # 跳过结构条或非错误记录
            
            task = ast.literal_eval(item["task"])
            stage_dict[item["stage"]].append(task)

    return dict(stage_dict)

def load_error_by_type(path):
    type_dict = defaultdict(list)
    with open(path, "r", encoding="utf-8") as f:
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
    try:
        item = q.get_nowait()
        q.put(item)  # optional: put it back
        return False
    except Empty:
        return True
    
async def is_queue_empty_async(q: AsyncQueue) -> bool:
    try:
        item = q.get_nowait()
        await q.put(item)  # ✅ 修复点
        return False
    except AsyncQueueEmpty:
        return True