# TaskManager

TaskManager 是一个用于管理和执行任务的灵活框架，支持串行、并行、异步及多进程的任务执行方式。它具有强大的重试机制、日志记录功能、进度管理，以及多种执行模式的兼容性。

## 特性
- **多种执行模式**：支持串行（serial）、线程池（thread）、进程池（process）以及异步（async）执行。
- **重试机制**：对于指定的异常类型任务，可以自动重试，支持指数退避策略。
- **日志记录**：使用 loguru 记录任务执行过程中的成功、失败、重试等情况。
- **进度管理**：支持通过 ProgressManager 动态显示任务进度。
- **任务结果管理**：任务的执行结果和错误信息被统一记录并可获取。
- **任务去重**：支持任务去重，防止重复任务的执行。
- **资源释放**：自动管理线程池和进程池资源的创建和关闭，防止资源泄漏。

## 安装
确保你的环境中已经安装了以下依赖项：

```bash
pip install loguru
```

## 快速上手

### 1. 初始化 TaskManager
首先，定义一个你想要并行执行的任务函数。任务函数接受的参数形式可以自由定义，稍后你需要在 TaskManager 中实现如何获取这些参数。

```python
def example_task(x, y):
    return x + y
```

然后，创建一个 TaskManager 实例，并指定你的任务函数、执行模式和其他配置参数：

```python
from task_manager import TaskManager

# 创建TaskManager实例
task_manager = TaskManager(
    func=example_task,
    execution_mode='thread',  # 可选：serial, thread, process, async
    worker_limit=5,           # 最大并发限制
    max_retries=3,            # 最大重试次数
    show_progress=True        # 是否显示进度
)
```

### 2. 启动任务
准备好任务列表后，可以通过 start 方法启动任务执行：

```python
tasks = [(1, 2), (3, 4), (5, 6), (7, 8)]
task_manager.start(tasks)
```

TaskManager 将根据设定的执行模式并发或异步地执行任务，并自动处理任务的成功、失败和重试逻辑。

### 3. 获取任务结果
任务执行完成后，可以通过 get_result_dict 方法获取执行结果，或通过 get_error_dict 获取失败的任务及其对应的异常。

```python
# 获取成功的结果
results = task_manager.get_result_dict()
print("Results:", results)

# 获取失败的任务及其异常
errors = task_manager.get_error_dict()
print("Errors:", errors)
```

### 4. 关闭资源
在任务执行完成后，务必调用 shutdown_pools 方法以确保资源被正确释放。

```python
task_manager.shutdown_pools()
```

## 主要参数和方法说明

### TaskManager 类
func: 任务执行函数，必须是可调用对象。
execution_mode: 执行模式，支持 'serial'、'thread'、'process' 和 'async'。
worker_limit: 最大并发任务数，适用于并发和异步执行模式。
max_retries: 任务失败时的最大重试次数，支持指数退避。
show_progress: 是否显示任务进度条，默认不显示。
progress_desc: 进度条的描述文字，用于标识任务类型。

### 常用方法
start(task_list: List): 启动任务执行，task_list 是任务列表，每个任务的格式取决于你在 get_args 中如何定义。
start_async(task_list: List): 异步地执行任务。
get_result_dict() -> dict: 返回任务执行的结果字典，键是任务对象，值是任务结果。
get_error_dict() -> dict: 返回任务执行失败的字典，键是任务对象，值是异常信息。
shutdown_pools(): 关闭线程池和进程池，释放资源。

### 自定义方法
你可以通过继承 TaskManager 并实现以下方法，来自定义任务处理的逻辑：

get_args(task): 从任务对象中提取执行函数的参数。根据任务对象的结构，自定义参数提取逻辑。
process_result(task, result): 处理任务的执行结果。可以对结果进行处理、格式化或存储。
handle_error(): 统一处理任务执行后的所有错误。可以自定义错误处理逻辑。

**示例**
1. 串行任务执行
```python
task_manager = TaskManager(func=example_task, execution_mode='serial')
task_manager.start(tasks)
```
2. 多线程任务执行
```python
task_manager = TaskManager(func=example_task, execution_mode='thread', worker_limit=10)
task_manager.start(tasks)
```
3. 异步任务执行
```python
async def example_async_task(x, y):
    await asyncio.sleep(1)
    return x + y

task_manager = TaskManager(func=example_async_task, execution_mode='async', worker_limit=5)
await task_manager.start_async(tasks)
```

## 日志
TaskManager 使用 loguru 进行日志记录，默认将日志保存到 logs/ 目录下。你可以通过自定义 TaskLogger 来修改日志格式或路径。

## 进阶

### 自定义任务参数
如果你的任务对象有复杂的参数，可以通过继承 TaskManager 并重写 get_args 方法，来自定义参数的提取方式。例如：

```python
class MyTaskManager(TaskManager):
    def get_args(self, task):
        return task['x'], task['y']
```

### 重试机制
对于定义的 retry_exceptions，如 TimeoutError 或 ConnectionError，TaskManager 将自动重试这些任务。如果你有自定义的异常类型，可以通过设置 self.retry_exceptions 来扩展重试逻辑。

# TaskChain

TaskChain 是一个用于组织和执行多阶段任务链的框架。每个阶段都是由 TaskManager 实例组成，任务链可以串行或并行执行。在任务链中，任务会依次通过每个阶段的处理，并最终返回结果。

## 特性

- **多阶段任务管理**：TaskChain 将多个 TaskManager 实例连接起来，形成一个任务链，每个任务经过各个阶段的处理。
- **执行模式**：支持串行（serial）和多进程并行（process）执行方式。
- **任务结果追踪**：能够跟踪初始任务在整个任务链中的最终结果。
- **动态阶段管理**：可以动态添加、移除或修改任务链中的阶段。

## 依赖
TaskChain 基于 TaskManager 构建，因此需要先安装 TaskManager 相关依赖：

```bash
pip install loguru
```

## 快速上手
### 1. 初始化 TaskChain
首先，准备多个 TaskManager 实例，每个实例代表任务链中的一个阶段。然后，创建一个 TaskChain 实例，将这些 TaskManager 实例作为参数传递给 TaskChain。

```python
from task_manager import TaskManager, TaskChain

# 定义几个简单的任务函数
def task_stage_1(x):
    return x + 1

def task_stage_2(x):
    return x * 2

# 创建 TaskManager 实例，代表不同的任务阶段
stage_1 = TaskManager(func=task_stage_1, execution_mode='serial')
stage_2 = TaskManager(func=task_stage_2, execution_mode='thread')

# 创建 TaskChain 实例
task_chain = TaskChain(stages=[stage_1, stage_2])
```

### 2. 启动任务链
准备好初始任务列表后，通过 start_chain 方法启动任务链执行。任务将依次通过每个阶段进行处理。

```python
# 定义初始任务
initial_tasks = [1, 2, 3, 4]

# 启动任务链（默认串行模式）
task_chain.start_chain(initial_tasks)
```

### 3. 获取最终结果
任务链执行完成后，可以通过 get_final_result_dict 方法获取每个初始任务的最终处理结果。

```python
# 获取任务链的最终结果
final_results = task_chain.get_final_result_dict()
print("Final Results:", final_results)
```

### 4. 并行执行任务链
如果任务链中的每个阶段需要并行处理任务，可以将 chain_mode 设置为 'process'，并启动任务链。这会使用多进程来并行处理任务链中的每个阶段，此时每个阶段的处理结果会立刻交给下一阶段进行处理。

```python
task_chain.set_chain_mode('process')
task_chain.start_chain(initial_tasks)
```

## 主要参数和方法说明
### TaskChain 类
- **stages**: 一个包含 TaskManager 实例的列表，代表任务链的各个阶段。
- **chain_mode**: 任务链的执行模式，支持 'serial'（串行）和 'process'（并行）。默认为串行模式。

### 常用方法
- set_chain_mode(chain_mode: str): 设置任务链的执行模式，可以选择 'serial' 或 'process'。
- add_stage(stage: TaskManager): 动态添加一个新的任务阶段到任务链中。
- remove_stage(index: int): 移除任务链中指定索引的阶段。
- start_chain(tasks: List): 启动任务链，传入初始任务列表。根据 chain_mode 选择串行或并行方式执行任务链。
- run_chain_in_serial(tasks: List): 串行地执行任务链中的每个阶段。
- run_chain_in_process(tasks: List): 使用多进程并行地执行任务链中的每个阶段。
- get_final_result_dict() -> dict: 获取初始任务在整个任务链中最终处理的结果字典。

## TaskChain 关键功能解释
### 串行模式（serial）

每个任务依次经过任务链的所有阶段，前一个阶段的输出作为下一个阶段的输入。

### 并行模式（process）

每个阶段在独立的进程中并行执行，使用多进程队列（MPQueue）在阶段间传递任务结果。任务在第一个阶段的结果会作为输入传递给下一个阶段，直到所有阶段完成。

## 任务链的工作流程
- 初始化任务队列：初始任务列表被放入第一个阶段的任务队列中。
- 阶段执行：每个阶段分别处理任务，串行或并行模式下，任务通过各个阶段的处理。
- 结果收集：每个阶段的结果会传递到下一个阶段，最终获取初始任务的最终处理结果。

## 示例
### 1. 串行任务链
```python
# 创建 TaskChain 实例
task_chain = TaskChain(stages=[stage_1, stage_2], chain_mode='serial')

# 定义初始任务
initial_tasks = [1, 2, 3, 4]

# 启动任务链
task_chain.start_chain(initial_tasks)

# 获取最终结果
final_results = task_chain.get_final_result_dict()
print("Final Results:", final_results)
```
### 2. 并行任务链
```python
# 创建 TaskChain 实例
task_chain = TaskChain(stages=[stage_1, stage_2], chain_mode='process')

# 定义初始任务
initial_tasks = [1, 2, 3, 4]

# 启动任务链（并行模式）
task_chain.start_chain(initial_tasks)

# 获取最终结果
final_results = task_chain.get_final_result_dict()
print("Final Results:", final_results)
```

# 贡献
欢迎对本项目提出改进建议或提交 PR。如有任何问题，请提交 issues。