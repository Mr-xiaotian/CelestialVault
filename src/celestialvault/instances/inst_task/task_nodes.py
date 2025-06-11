import json
import time
import redis

from .task_manage import TaskManager
from .task_tools import object_to_str_hash


class TaskSplitter(TaskManager):
    def __init__(self):
        """
        :param split_func: 用于分解任务的函数，默认直接返回原始值
        """
        super().__init__(
            func=self.split_task,
            execution_mode="serial",
            progress_desc="Spliting tasks",
            show_progress=False,
        )

    def split_task(self, *task):
        """
        实际上这个函数不执行逻辑，仅用于符合 TaskManager 架构
        """
        return task

    def get_args(self, task):
        return task

    def process_result(self, task, result):
        """
        处理不可迭代的任务结果
        """
        if not hasattr(result, "__iter__") or isinstance(result, (str, bytes)):
            result = (result,)
        elif isinstance(result, list):
            result = tuple(result)

        return result

    def process_task_success(self, task, result, start_time):
        """
        统一处理成功任务

        :param task: 完成的任务
        :param result: 任务的结果
        :param start_time: 任务开始时间
        """
        processed_result = self.process_result(task, result)
        self.success_dict[task] = processed_result

        self.add_succes_counter()

        split_count = 0
        for item in processed_result:
            self.put_result_queues(item)
            split_count += 1

        self.extra_stats["split_output_count"].value += split_count

        self.task_logger.splitter_success(
            self.func.__name__,
            self.get_task_info(task),
            split_count,
            time.time() - start_time,
        )


class TaskRedisTransfer(TaskManager):
    def __init__(self, host="localhost", port=6379, db=0, timeout=10):
        super().__init__(self._process_via_redis, "thread")

        self.host = host
        self.port = port
        self.db = db
        self.timeout = timeout

    def init_redis(self):
        if not hasattr(self, "redis_client"):
            self.redis_client = redis.Redis(host=self.host, port=self.port, db=self.db, decode_responses=True)

    def _process_via_redis(self, task):
        self.init_redis()
        input_key = f"{self.get_stage_tag()}:input"
        output_key = f"{self.get_stage_tag()}:output"

        # 将任务写入 redis（如 list 或 stream）
        task_id = object_to_str_hash(task)
        payload = json.dumps({"id": task_id, "task": task})
        self.redis_client.rpush(input_key, payload)

        # 等待结果（可以阻塞，或轮询）
        start_time = time.time()
        while True:
            result = self.redis_client.hget(output_key, task_id)
            if result:
                self.redis_client.hdel(output_key, task_id)
                return json.loads(result)
            elif time.time() - start_time > self.timeout:
                raise TimeoutError("Redis result not returned in time")
            time.sleep(0.1)
