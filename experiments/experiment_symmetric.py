import time
from typing import Optional
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


def benchmark_collections(N: int = 100_000, target: Optional[str] = None, verbose: bool = True) -> None:
    """
    基准测试：比较 list、tuple、set、dict、SymmetricMap 与 bidict 的查找性能。

    :param N: 元素数量（建议 1_000 ~ 1_000_000）
    :param target: 要查找的目标元素（默认查最后一个）
    :param verbose: 是否打印详细输出
    """
    if target is None:
        target = str(N - 1)

    if verbose:
        print(f"\n=== 基准测试: N = {N:,}, target = {target} ===")

    # ---------- 构造数据 ----------
    data_list = [str(i) for i in range(N)]
    data_tuple = tuple(data_list)
    data_set = set(data_list)
    data_dict = {str(i): i for i in range(N)}

    sym_map = SymmetricMap[str]()
    for i in range(N):
        s = str(i)
        sym_map[s] = i  # 绑定 str <-> int

    bi_map = bidict(data_dict)

    # ---------- 测试函数 ----------
    def bench(label, func):
        start = time.perf_counter()
        func()
        elapsed = time.perf_counter() - start
        if verbose:
            print(f"{label:<30}: {elapsed:.6f} 秒")
        return elapsed

    # ---------- 执行测试 ----------
    results = {}

    results["list"] = bench("list 查找", lambda: target in data_list)
    results["tuple"] = bench("tuple 查找", lambda: target in data_tuple)
    results["set"] = bench("set 查找", lambda: target in data_set)
    results["dict_key"] = bench("dict key 查找", lambda: target in data_dict)
    results["dict_value"] = bench("dict value 查找", lambda: int(target) in data_dict.values())

    results["sym_key"] = bench("SymmetricMap key 查找", lambda: target in sym_map.pairs)
    results["sym_value"] = bench("SymmetricMap value 查找", lambda: int(target) in sym_map.reverse)
    results["sym_contains"] = bench("SymmetricMap 双向查找", lambda: target in sym_map)

    results["bidict_key"] = bench("bidict key 查找", lambda: target in bi_map)
    results["bidict_value"] = bench("bidict value 查找", lambda: int(target) in bi_map.inv)

    # ---------- 汇总结果 ----------
    if verbose:
        fastest = min(results, key=results.get)
        print(f"\n⚡ 最快结构: {fastest} ({results[fastest]:.6f} 秒)")
        print("-" * 50)

    return results


if __name__ == '__main__':
    compare_symmetric_map()
    benchmark_collections()