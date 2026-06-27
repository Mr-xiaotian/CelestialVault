# test_logger.md

> 最后更新日期: 2026/06/28

## 作用

验证 `loguru` 与标准库 `logging` 的集成行为，包括基本日志输出、自定义格式、多目标输出（控制台 + 文件）。

## 被测模块

| 模块 | 来源 | 说明 |
|------|------|------|
| `loguru.logger` | 第三方依赖 `loguru` | 结构化日志记录器 |
| `logging` | Python 标准库 | 兼容标准日志 API |

## 测试重点

### `test_log`

- 移除 `loguru` 默认 sink，添加 `sys.stderr` 输出并设置级别为 `INFO`。
- 分别输出：
  - `logger.info("logger success")`
  - `print("print success")`
  - `logging.info("logging success")`
- 用于确认 `loguru` 与 `logging` 在测试环境中能正常输出。

### `test_logger`

- 配置自定义格式：
  - 控制台格式：带颜色级别与时间
  - 文件格式：纯文本时间、级别、消息
- 添加两个 sink：
  - 控制台：通过 `lambda msg: print(msg, end="")`
  - 文件：`thread_manager.log`
- 输出包含 ANSI 高亮字符的日志消息，验证格式化与高亮内容可正常写入。

## 运行方式

```bash
uv run pytest tests/test_logger.py -s
```

> `test_logger` 会在当前工作目录生成 `thread_manager.log`，多次运行会追加写入。
