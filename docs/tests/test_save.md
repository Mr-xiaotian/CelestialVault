# test_save.py

> 最后更新日期: 2026/06/28

## 作用

验证 `celestialvault.instances.inst_save.Saver` 的批量 URL 下载能力，测试串行模式下的任务链执行与结果收集。

## 被测模块

| 模块 | 文件 | 说明 |
|------|------|------|
| `Saver` | `src/celestialvault/instances/inst_save.py` | 资源下载器，支持串行/并发模式 |

## 测试重点

### `test_saver`

- 准备 3 条任务：两条真实图片 URL、一条无效字符串。
- 构造 `(url, index, ".jpg")` 形式的 `task_list`。
- 初始化 `Saver(r"../test")` 并调用 `set_add_path("test_jpg")` 设置子目录。
- 将 `stage_mode` 设为 `"serial"`（测试代码中本地变量命名为 `chain_mode`）执行 `download_urls`。
- 记录并打印任务耗时与结果字典。

## 运行方式

```bash
uv run pytest tests/test_save.py -s
```

> 该测试会发起真实网络请求并写入相对路径 `../test/test_jpg`，运行前请确认网络与目录权限。注释中保留了 `fetch_threader` 异步模式的调用示例，当前未启用。
