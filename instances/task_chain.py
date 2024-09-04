import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import time

# 环节管理类
class TaskStage:
    def __init__(self, func, mode='parallel', thread_num=5):
        self.func = func
        self.mode = mode
        self.thread_num = thread_num

    def run_stage(self, input_queue, output_queue):
        """
        运行环节，消费上一个环节的结果，并将结果推送到下一个环节的任务池
        """
        if self.mode == 'parallel':
            with ThreadPoolExecutor(max_workers=self.thread_num) as executor:
                while True:
                    try:
                        # 从输入队列获取数据并处理
                        task = input_queue.get(timeout=1)
                        if task is None:
                            break
                        future = executor.submit(self.func, task)
                        result = future.result()
                        # 将结果放入输出队列
                        output_queue.put(result)
                    except Exception as e:
                        print(f"Error in stage: {e}")
        else:
            # 串行执行
            while True:
                try:
                    task = input_queue.get(timeout=1)
                    if task is None:
                        break
                    result = self.func(task)
                    output_queue.put(result)
                except Exception as e:
                    print(f"Error in stage: {e}")
        
        # 标记完成
        output_queue.put(None)

# 处理链管理器
class ChainManager:
    def __init__(self, stages):
        """
        stages: 一个包含 StageManager 实例的列表，表示执行链
        """
        self.stages = stages

    def start_chain(self, tasks):
        # 创建进程间的队列
        queues = [multiprocessing.Queue() for _ in range(len(self.stages) + 1)]
        
        # 向第一个队列添加初始任务
        for task in tasks:
            queues[0].put(task)
        
        # 创建多进程来运行每个环节
        processes = []
        for i, stage in enumerate(self.stages):
            p = multiprocessing.Process(target=stage.run_stage, args=(queues[i], queues[i + 1]))
            p.start()
            processes.append(p)
        
        # 等待最后一个环节处理完成
        while True:
            result = queues[-1].get()
            if result is None:
                break
            print(f"Final result: {result}")
        
        # 等待所有进程结束
        for p in processes:
            p.join()

# 定义各个环节的处理函数
def process_stage_1(task):
    time.sleep(1)
    return task * 2

def process_stage_2(task):
    time.sleep(1)
    return task + 10

def process_stage_3(task):
    time.sleep(1)
    return task - 5

# 定义执行链
stages = [
    TaskStage(process_stage_1, mode='parallel', thread_num=5),
    TaskStage(process_stage_2, mode='parallel', thread_num=3),
    TaskStage(process_stage_3, mode='serial')
]

# 创建 ChainManager
chain_manager = ChainManager(stages)

# 启动执行链
tasks = [1, 2, 3, 4, 5]  # 初始任务
chain_manager.start_chain(tasks)
