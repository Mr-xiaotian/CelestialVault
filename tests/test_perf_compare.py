import time
import queue
import redis
import logging
import threading
import pytest
import multiprocessing
from multiprocessing import Manager, Queue, Process, Value

N = 10000

# =======================
# Worker functions (must be global for Windows)
# =======================

def mpqueue_worker(q):
    t0 = time.time()
    for i in range(N):
        q.put(i)
    t1 = time.time()
    for i in range(N):
        _ = q.get()
    t2 = time.time()
    print(f"MPQueue: put={t1 - t0:.4f}s, get={t2 - t1:.4f}s")

def manager_dict_worker(d):
    t0 = time.time()
    for i in range(N):
        d[i] = i
    t1 = time.time()
    for i in range(N):
        _ = d[i]
    t2 = time.time()
    print(f"Manager.dict: put={t1 - t0:.4f}s, get={t2 - t1:.4f}s")

def value_worker(val):
    t0 = time.time()
    for _ in range(N):
        with val.get_lock():
            val.value += 1
    t1 = time.time()
    print(f"Value (number): inc={t1 - t0:.4f}s")

# =======================
# Fixtures
# =======================

@pytest.fixture(scope="module")
def redis_conn():
    return redis.Redis(host='localhost', port=6379, db=0)

# =======================
# Tests
# =======================

def test_builtin_dict():
    d = {}
    t0 = time.time()
    for i in range(N):
        d[i] = i
    t1 = time.time()
    for i in range(N):
        _ = d[i]
    t2 = time.time()
    print(f"Built-in dict: put={t1 - t0:.4f}s, get={t2 - t1:.4f}s")

def test_queue_thread():
    q = queue.Queue()
    t0 = time.time()
    for i in range(N):
        q.put(i)
    t1 = time.time()
    for i in range(N):
        _ = q.get()
    t2 = time.time()
    print(f"Queue (thread): put={t1 - t0:.4f}s, get={t2 - t1:.4f}s")

def test_mpqueue():
    q = multiprocessing.Queue()
    p = Process(target=mpqueue_worker, args=(q,))
    p.start()
    p.join()

def test_manager_dict():
    with Manager() as manager:
        d = manager.dict()
        p = Process(target=manager_dict_worker, args=(d,))
        p.start()
        p.join()

def test_value_number():
    v = Value('i', 0)
    p = Process(target=value_worker, args=(v,))
    p.start()
    p.join()

def test_redis_plain(redis_conn):
    t0 = time.time()
    for i in range(N):
        redis_conn.set(f'plain_key{i}', i)
    t1 = time.time()
    for i in range(N):
        _ = redis_conn.get(f'plain_key{i}')
    t2 = time.time()
    print(f"Redis (plain): set={t1 - t0:.4f}s, get={t2 - t1:.4f}s")

def test_redis_pipeline(redis_conn):
    t0 = time.time()
    pipe = redis_conn.pipeline()
    for i in range(N):
        pipe.set(f'pipe_key{i}', i)
    pipe.execute()
    t1 = time.time()

    pipe = redis_conn.pipeline()
    for i in range(N):
        pipe.get(f'pipe_key{i}')
    _ = pipe.execute()
    t2 = time.time()

    print(f"Redis (pipeline): set={t1 - t0:.4f}s, get={t2 - t1:.4f}s")

def test_redis_multithread_plain(redis_conn, num_threads=10):
    """
    多线程并发写入 + 读取 Redis，不使用 pipeline
    """
    count_per_thread = N // num_threads
    threads = []

    # --- 写入阶段 ---
    def writer(tid, base):
        for i in range(count_per_thread):
            redis_conn.set(f"mt_key{tid}_{i+base}", i)

    t0 = time.time()
    for t_id in range(num_threads):
        base = t_id * count_per_thread
        thread = threading.Thread(target=writer, args=(t_id, base))
        thread.start()
        threads.append(thread)

    for t in threads:
        thread.join()
    t1 = time.time()

    # --- 读取阶段 ---
    threads = []
    def reader(tid, base):
        for i in range(count_per_thread):
            _ = redis_conn.get(f"mt_key{tid}_{i+base}")

    for t_id in range(num_threads):
        base = t_id * count_per_thread
        thread = threading.Thread(target=reader, args=(t_id, base))
        thread.start()
        threads.append(thread)

    for t in threads:
        thread.join()
    t2 = time.time()

    print(f"Redis (multi-thread x{num_threads}, no pipeline): set={t1 - t0:.4f}s, get={t2 - t1:.4f}s")

def test_redis_hash(redis_conn):
    t0 = time.time()
    for i in range(N):
        redis_conn.hset("hash_test", f"field{i}", i)
    t1 = time.time()
    for i in range(N):
        _ = redis_conn.hget("hash_test", f"field{i}")
    t2 = time.time()
    print(f"Redis (hash): hset={t1 - t0:.4f}s, hget={t2 - t1:.4f}s")

def test_redis_list(redis_conn):
    redis_conn.delete("list_test")
    t0 = time.time()
    for i in range(N):
        redis_conn.rpush("list_test", i)
    t1 = time.time()
    for i in range(N):
        _ = redis_conn.lindex("list_test", i)
    t2 = time.time()
    print(f"Redis (list): rpush={t1 - t0:.4f}s, lindex={t2 - t1:.4f}s")

def test_redis_set(redis_conn):
    redis_conn.delete("set_test")
    t0 = time.time()
    for i in range(N):
        redis_conn.sadd("set_test", i)
    t1 = time.time()
    for i in range(N):
        _ = redis_conn.sismember("set_test", i)
    t2 = time.time()
    print(f"Redis (set): sadd={t1 - t0:.4f}s, sismember={t2 - t1:.4f}s")

def test_redis_zset(redis_conn):
    redis_conn.delete("zset_test")
    t0 = time.time()
    for i in range(N):
        redis_conn.zadd("zset_test", {f"item{i}": i})
    t1 = time.time()
    for i in range(N):
        _ = redis_conn.zscore("zset_test", f"item{i}")
    t2 = time.time()
    print(f"Redis (zset): zadd={t1 - t0:.4f}s, zscore={t2 - t1:.4f}s")

def test_redis_pipeline_multiprocess(redis_conn):
    from multiprocessing import Process

    num_processes = 10
    num_items = 1000  # 每个测试传输的数据量

    # 确保所有队列干净
    for i in range(num_processes):
        redis_conn.delete(f"pipe_stage:{i}")

    def stage_worker(stage_id):
        input_key = f"pipe_stage:{stage_id - 1}"
        output_key = f"pipe_stage:{stage_id}"

        for _ in range(num_items):
            while True:
                item = redis_conn.lpop(input_key)
                if item is not None:
                    break
                time.sleep(0.001)  # 避免死循环太占 CPU
            redis_conn.rpush(output_key, item)

    # 第一个进程的输入数据
    for i in range(num_items):
        redis_conn.rpush("pipe_stage:0", f"item{i}")

    processes = []
    t0 = time.time()
    for i in range(1, num_processes):
        p = Process(target=stage_worker, args=(i,))
        p.start()
        processes.append(p)

    # 最后一个进程从 pipe_stage:N-1 消费数据
    output_key = f"pipe_stage:{num_processes - 1}"
    count = 0
    while count < num_items:
        item = redis_conn.lpop(output_key)
        if item is not None:
            count += 1
        else:
            time.sleep(0.001)

    for p in processes:
        p.join()
    t1 = time.time()

    print(f"Redis (list-based, {num_processes} processes, {num_items} items): total={t1 - t0:.4f}s")
