import time
import pytest
from multiprocessing import Queue as MPQueue
import redis

@pytest.fixture(scope="module")
def redis_client():
    r = redis.Redis(decode_responses=True)
    r.flushdb()
    return r

@pytest.mark.parametrize("count", [100_000])
def test_mpqueue_perf(count):
    q = MPQueue()

    start_put = time.time()
    for i in range(count):
        q.put(i)
    put_duration = time.time() - start_put

    start_get = time.time()
    for _ in range(count):
        q.get()
    get_duration = time.time() - start_get

    start_size = time.time()
    for _ in range(count):
        _ = q.qsize()
    size_duration = time.time() - start_size

    start_empty = time.time()
    for _ in range(count):
        _ = q.empty()
    empty_duration = time.time() - start_empty

    print(f"\nMPQueue ({count} items):")
    print(f"  put:    {put_duration:.4f}s")
    print(f"  get:    {get_duration:.4f}s")
    print(f"  qsize:  {size_duration:.6f}s ")
    print(f"  empty:  {empty_duration:.6f}s")


@pytest.mark.parametrize("count", [100_000])
def test_redis_list_perf(redis_client, count):
    key = "redis_queue"
    r = redis_client
    r.delete(key)

    start_put = time.time()
    for i in range(count):
        r.lpush(key, i)
    put_duration = time.time() - start_put

    start_get = time.time()
    for _ in range(count):
        r.rpop(key)
    get_duration = time.time() - start_get

    start_size = time.time()
    for _ in range(count):
        _ = r.llen(key)
    size_duration = time.time() - start_size

    start_empty = time.time()
    for _ in range(count):
        _ = (r.llen(key) == 0)
    empty_duration = time.time() - start_empty


    print(f"\nRedis List ({count} items):")
    print(f"  lpush:  {put_duration:.4f}s")
    print(f"  rpop:   {get_duration:.4f}s")
    print(f"  llen:   {size_duration:.6f}s")
    print(f"  empty:  {empty_duration:.6f}s")

