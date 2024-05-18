# CelestialVault
一些常用的辅助代码，主要包括放置常用工具函数的tools, 常用类的instances与常量的constants。以下各自介绍他们中最有用的部分内容:

## instances

### my_thread
这个代码库包含三个类：ThreadWorker ThreadManager和ExampleThreadManager。

ThreadWorker 是一个继承自 threading.Thread 的类，它接受一个可调用对象 func 和一个参数列表 args。当线程运行时，它会尝试调用 func 并保存结果。如果在调用过程中抛出异常，它会保存异常信息。

ThreadManager 是一个线程管理器，可以并行、串行或异步地执行任务。它接受一个可调用对象 func，一个可选的池（尚未在代码中使用），以及一个线程数量 thread_num，还有控制任务最大循环数的max_retries。此类有几个方法：

- get_args(obj): 这是一个抽象方法，需要被子类实现，用来从 obj 中获取参数。
- process_result(obj, result): 这是一个抽象方法，需要被子类实现，用来处理结果。
- handle_error(obj): 这是一个抽象方法，需要被子类实现，用来处理错误。
- start(dictory, start_type='serial'): 这个方法会根据 start_type 的值来选择串行、并行或异步地执行任务。
- start_async(dictory): 这个方法会异步地执行任务，需要从外界await调用。
- run_in_parallel(dictory): 这个方法会并行地执行任务。
- run_in_serial(dictory): 这个方法会串行地执行任务。
- run_in_async(dictory): 这个方法会异步地执行任务。
- get_result_list(): 这个方法返回结果列表。
- get_result_dict(): 这个方法返回结果字典。

该程序还包括一个 ExampleThreadManager 类，这是 ThreadManager 类的子类，作为一个使用示例。ExampleThreadManager 类定义了如何从任务对象中获取函数参数、如何处理结果和错误等具体细节。

### inst_findiff
这是一个用于对比字符串或字典的Python脚本。它包括以下主要函数：

- fd_str(a, b, split_str='\n')：此函数接收两个字符串（a和b）以及一个可选的分隔符（默认为换行符）作为输入。然后，它调用compare_strings打印出两个字符串的长度和不同之处（根据提供的分隔符进行划分）。
- fd_dict(dict_a, dict_b)：此函数接收两个字典（dict_a和dict_b）作为输入。它调用compare_strings对比这两个字典的键和值，并打印出它们的不同之处。
- compare_strings(str1: str, str2: str) -> None：此函数接收两个字符串作为输入并找出它们的不同之处。如果两个字符串完全一致，它会打印出"完全一致"。否则，它会找出并打印出两个字符串的不同之处。
- print_diffs(input_str: str, diff_ranges: list, nor_end='\033[0m', dif_end='\033[1m') -> None：此函数打印出两个字符串的不同之处。它接收一个输入字符串、一个包含差异范围的列表以及两个可选的终止符（默认为'\033[0m'和'\033[1m'）作为输入。

以下是一个简单的使用示例：

```
from CelestialVault import Findiffer

fd = Findiffer()

# 使用字符串对比函数
str_a = "Hello, World!"
str_b = "Hello, OpenAI!"
fd.fd_str(str_a, str_b)

# 使用字典对比函数
dict_a = {"key1": "value1", "key2": "value2"}
dict_b = {"key1": "value1", "key2": "value3"}
fd.fd_dict(dict_a, dict_b)
```

