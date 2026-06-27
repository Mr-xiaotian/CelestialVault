# test_symmetric.py

> 最后更新日期: 2026/06/28

## 作用

验证 `celestialvault.instances.inst_symmetric.SymmetricMap` 的双向对称映射行为，包括插入、幂等写入、变更配对、键值遍历等核心操作。

## 被测模块

| 模块 | 文件 | 说明 |
|------|------|------|
| `SymmetricMap` | `src/celestialvault/instances/inst_symmetric.py` | 自动维护 key↔value 双向索引的映射容器 |

## 测试重点

### `test_symmetric_map_basic`

- 插入 `m["a"] = "b"` 后断言：
  - `m["a"] == "b"`
  - `m["b"] == "a"`（对称访问）
  - `"a" in m` 与 `"b" in m`
  - `len(m) == 1`（一对只计一次）
- 继续插入 `m["x"] = "y"`，验证 `keys()`、`values()`、`items()` 返回正确的独立配对集合。
- 幂等测试：再次写入 `m["a"] = "b"`，确认长度不变。
- 变更配对：写入 `m["a"] = "y"`，验证旧的 `b` 与 `x` 被解绑，最终仅剩 `a↔y` 一对。

## 运行方式

```bash
uv run pytest tests/test_symmetric.py -s
```
