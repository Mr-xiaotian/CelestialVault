import pytest
import time
from bidict import bidict
from celestialvault.instances.inst_symmetric import SymmetricMap


def test_symmetric_map_basic():
    m = SymmetricMap()
    m['a'] = 'b'
    assert m['a'] == 'b' and m['b'] == 'a'
    assert 'a' in m and 'b' in m and len(m) == 1

    m['x'] = 'y'
    assert set(m.keys()) == {'a', 'x'}
    assert set(m.values()) == {'b', 'y'}
    assert set(m.items()) == {('a', 'b'), ('x', 'y')}

    # 幂等设置
    m['a'] = 'b'  # 不应改变内容
    assert len(m) == 2

    # 变更配对
    m['a'] = 'y'  # 会先解绑 a<->b 与 x<->y，再建立 a<->y
    assert 'b' not in m and 'x' not in m and len(m) == 1 and m['a'] == 'y'

def compare_symmetric_map():
    # === 测试数据 ===
    N = 1_000_000  # 可调大些看趋势
    keys = [f'k{i}' for i in range(N)]
    values = [f'v{i}' for i in range(N)]

    # --- SymmetricMap ---
    start = time.time()
    sym = SymmetricMap()
    for k, v in zip(keys, values):
        sym[k] = v
    print(f"SymmetricMap 插入: {time.time() - start:.3f} 秒")

    start = time.time()
    for k in keys:
        _ = sym[k]
    print(f"SymmetricMap 正向查找: {time.time() - start:.3f} 秒")

    start = time.time()
    for v in values:
        _ = sym[v]
    print(f"SymmetricMap 反向查找: {time.time() - start:.3f} 秒")

    print("-" * 50)

    # --- bidict ---
    start = time.time()
    b = bidict()
    for k, v in zip(keys, values):
        b[k] = v
    print(f"bidict 插入: {time.time() - start:.3f} 秒")

    start = time.time()
    for k in keys:
        _ = b[k]
    print(f"bidict 正向查找: {time.time() - start:.3f} 秒")

    start = time.time()
    for v in values:
        _ = b.inverse[v]
    print(f"bidict 反向查找: {time.time() - start:.3f} 秒")

    print("-" * 50)

    # --- dict + inverse ---
    start = time.time()
    fwd = {}
    inv = {}
    for k, v in zip(keys, values):
        fwd[k] = v
        inv[v] = k
    print(f"dict+inverse 插入: {time.time() - start:.3f} 秒")

    start = time.time()
    for k in keys:
        _ = fwd[k]
    print(f"dict 正向查找: {time.time() - start:.3f} 秒")

    start = time.time()
    for v in values:
        _ = inv[v]
    print(f"dict 反向查找: {time.time() - start:.3f} 秒")


if __name__ == '__main__':
    compare_symmetric_map()