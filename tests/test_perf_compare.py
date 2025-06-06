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
    start = time.time()
    for i in range(N):
        q.put(i)
    for i in range(N):
        _ = q.get()
    print("MPQueue:", time.time() - start)

def manager_dict_worker(d):
    start = time.time()
    for i in range(N):
        d[i] = i
    for i in range(N):
        _ = d[i]
    print("Manager.dict:", time.time() - start)

def value_worker(val):
    start = time.time()
    for _ in range(N):
        with val.get_lock():
            val.value += 1
    print("Value (number):", time.time() - start)

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
    start = time.time()
    for i in range(N):
        d[i] = i
    for i in range(N):
        _ = d[i]
    print("Built-in dict:", time.time() - start)

def test_queue_thread():
    q = queue.Queue()
    start = time.time()
    for i in range(N):
        q.put(i)
    for i in range(N):
        _ = q.get()
    print("Queue (thread):", time.time() - start)

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
    start = time.time()
    for i in range(N):
        redis_conn.set(f'plain_key{i}', i)
    for i in range(N):
        _ = redis_conn.get(f'plain_key{i}')
    print("Redis (plain):", time.time() - start)

def test_redis_pipeline(redis_conn):
    start = time.time()

    pipe = redis_conn.pipeline()
    for i in range(N):
        pipe.set(f'pipe_key{i}', i)
    pipe.execute()

    pipe = redis_conn.pipeline()
    for i in range(N):
        pipe.get(f'pipe_key{i}')
    _ = pipe.execute()

    print("Redis (pipeline):", time.time() - start)
