import time
import queue
import redis
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
