import time
from bidict import bidict
from celestialvault.instances.inst_symmetric import SymmetricMap


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