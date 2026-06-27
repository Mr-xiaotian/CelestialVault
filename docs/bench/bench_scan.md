# bench_scan.py 基准测试

> 最后更新日期: 2026/06/28

## 作用

本基准测试用于评估 `celestialvault.tools.FileOperations.get_file_info` 在不同线程并发度（`max_workers`）下，批量扫描目录中所有文件的整体耗时表现。

通过对比 `max_workers = 1, 2, 4, 8, 16` 时的扫描时间，帮助判断在该场景下增加线程数是否真的能带来性能收益，以及收益是否随线程数增加而递减。

## 测试对象

| 对象 | 说明 |
|------|------|
| `celestialvault.tools.FileOperations.get_file_info` | 被测函数。默认仅采集文件大小与修改时间（`include_hash=False`），不计算哈希，因此本测试主要衡量文件元数据批量采集的 I/O 与并发开销。 |
| `celestialflow.TaskExecutor` | 执行器。负责以 `"thread"` 模式并发调度 `get_file_info` 任务。 |
| `celestialflow.TaskProgress` | 进度观察器。注册到 `TaskExecutor` 上，用于在控制台显示扫描进度。 |

### 核心代码结构

```python
def scan(dir_path: Path, max_workers) -> dict:
    scan_info_executor = TaskExecutor(
        "Scanning files",
        get_file_info,
        "thread",
        max_workers=max_workers,
    )
    scan_info_executor.add_observer(TaskProgress())

    file_path_list = [
        file_path for file_path in dir_path.glob("**/*") if file_path.is_file()
    ]
    start_time = time.perf_counter()
    scan_info_executor.start(file_path_list)
    end_time = time.perf_counter()
    print(f"Scanning completed in {end_time - start_time:.2f} seconds")
```

> ⚠️ 注意：`scan` 函数的类型标注为 `-> dict`，但当前实现并未返回任何字典，仅打印耗时。若后续希望收集并返回每次扫描的统计结果，需要同步修改函数实现与类型标注。

## 关键指标

| 指标 | 含义 | 采集方式 |
|------|------|----------|
| 扫描总耗时 | 从任务开始调度到全部文件处理完成所经过的墙钟时间 | `time.perf_counter()` |
| 并发度 | 同时执行 `get_file_info` 的工作线程数 | `max_workers` 参数 |
| 扫描文件数 | 被扫描目录下所有普通文件的数量 | `dir_path.glob("**/*")` 配合 `is_file()` 过滤 |

## 运行方式

### 1. 前置条件

- 已安装 `celestialflow` 包（`TaskExecutor`、`TaskProgress` 的来源）。
- 已安装 `celestialvault` 包，或者已将项目根目录加入 `PYTHONPATH`，使 `from celestialvault.tools.FileOperations import get_file_info` 能正常导入。
- 准备一个真实存在的待扫描目录。

### 2. 修改目标目录（必要）

脚本中的默认扫描路径为硬编码路径：

```python
dir_path = Path(r"Q:\Project\CelestialFlow")
```

运行前请将该路径替换为你本地实际存在的目录。

### 3. 执行命令

在项目根目录下执行：

```bash
python bench/bench_scan.py
```

### 4. 示例输出

```text
Scanning with max_workers=1...
Scanning completed in 12.34 seconds
Scanning with max_workers=2...
Scanning completed in 6.78 seconds
Scanning with max_workers=4...
Scanning completed in 4.56 seconds
Scanning with max_workers=8...
Scanning completed in 3.89 seconds
Scanning with max_workers=16...
Scanning completed in 3.92 seconds
```

## 结果解读

- **耗时随 `max_workers` 增加而下降**：说明文件元数据采集是 I/O 密集型或存在较多小文件，增加并发线程数能够重叠等待时间。
- **耗时下降趋缓甚至反弹**：说明线程调度、GIL 竞争或磁盘随机访问已成为瓶颈，继续提高并发度收益有限，甚至可能因为上下文切换和锁竞争导致性能下降。
- **单线程耗时明显高于多线程**：可作为性能优化前后的基线参考。

> ⚠️ 本测试仅采集文件大小与修改时间。如果需要评估包含哈希计算的完整文件信息获取性能，需要修改被测调用为 `get_file_info(path, include_hash=True)`，并重新运行对比。

## 依赖与运行前提

| 依赖 | 说明 |
|------|------|
| `celestialflow` | 提供 `TaskExecutor` 与 `TaskProgress`，用于任务并发执行与进度展示。 |
| `celestialvault` | 提供 `get_file_info`。 |
| 本地目标目录 | 脚本硬编码为 `Q:\Project\CelestialFlow`，必须改为实际路径。 |

## 注意事项 / 常见陷阱

1. **硬编码路径不可直接运行**：默认的 `Q:\Project\CelestialFlow` 很可能在本地不存在，运行前务必修改 `main()` 中的 `dir_path`。
2. **被测函数签名变化会导致失效**：若 `get_file_info` 的参数名、默认值或返回结构发生变化，需要同步调整 `TaskExecutor` 的构造方式或结果处理逻辑。
3. **`TaskExecutor` 接口漂移**：`TaskExecutor` 的构造参数（如执行模式名称、观察者接口）若发生重构，本脚本可能无法启动。
4. **结果受环境因素影响大**：文件系统类型（SSD / HDD / 网络盘）、文件数量与大小、缓存状态、系统负载都会显著影响耗时，跨机器对比时需谨慎。
5. **返回值未实际使用**：`scan` 函数当前仅打印耗时，未返回结构化结果；若需要进一步分析或绘图，建议将耗时与文件数存入字典或列表后返回。
