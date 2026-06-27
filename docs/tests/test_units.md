# test_units.py

> 最后更新日期: 2026/06/28

## 作用

验证 `celestialvault.instances.inst_units` 中三个“人类可读”类型：`HumanBytes`、`HumanTime`、`HumanTimestamp` 的构造、运算与时区转换。

## 被测模块

| 模块 | 文件 | 说明 |
|------|------|------|
| `HumanBytes` | `src/celestialvault/instances/inst_units.py` | 字节数的人类可读表示 |
| `HumanTime` | `src/celestialvault/instances/inst_units.py` | 秒数的人类可读表示 |
| `HumanTimestamp` | `src/celestialvault/instances/inst_units.py` | 时间戳的封装与时区切换 |

## 测试重点

### `test_human_types`

- **HumanBytes**：
  - 从整数 `123456789` 构造
  - 从字符串 `"1GB 512MB"` 解析构造
  - 测试加法 `b1 + b2` 与乘法 `b1 * 2`
  - 测试 `repr(b1)`
- **HumanTime**：
  - 从浮点数 `5400.0` 构造
  - 从字符串 `"2h 15m 30s"` 解析构造
  - 测试加法 `t1 + t2` 与乘法 `t1 * 3`
  - 测试负时长 `HumanTime(-3700)`
- **HumanTimestamp**：
  - 从浮点数时间戳 `1742978962.1039817` 构造
  - 获取当前时间 `HumanTimestamp.now()`
  - 测试时间戳相减返回 `HumanTime`
  - 测试 `ts1 + 60`、ISO 格式输出 `to_iso()`、UTC 时区切换 `with_tz(ZoneInfo("UTC"))`

## 运行方式

```bash
uv run pytest tests/test_units.py -s
```
