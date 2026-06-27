# test_Utilities.py

> 最后更新日期: 2026/06/28

## 作用

验证 `celestialvault.tools.Utilities` 中对象内存占用估算与函数执行计时装饰器。

## 被测模块

| 模块 | 文件 | 说明 |
|------|------|------|
| `get_total_size` | `src/celestialvault/tools/Utilities.py` | 递归计算 Python 对象的总内存占用 |
| `log_time` | `src/celestialvault/tools/Utilities.py` | 装饰器，记录函数执行耗时 |

## 测试重点

### `test_get_total_size`

- 构造一个包含列表、元组、集合、嵌套字典的复合字典：
  ```python
  data = {
      "key1": [1, 2, 3],
      "key2": (4, 5),
      "key3": {6, 7, 8},
      "key4": {"nested_key": [9, 10]},
  }
  ```
- 调用 `get_total_size(data)`，期望输出约为 `1KB 423B`。

### `test_log_time`

- 使用 `log_time` 装饰一个休眠函数 `print_num(num)`。
- 调用 `print_num(5)`，验证装饰器能打印/记录函数执行耗时。

## 运行方式

```bash
uv run pytest tests/test_Utilities.py -s
```
