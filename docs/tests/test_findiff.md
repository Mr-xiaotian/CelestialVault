# test_findiff.py

> 最后更新日期: 2026/06/28

## 作用

验证 `celestialvault.instances.inst_findiff.Findiffer` 对字符串与字典的差异对比能力，覆盖连续文本差异与键值对差异两类典型场景。

## 被测模块

| 模块 | 文件 | 说明 |
|------|------|------|
| `Findiffer` | `src/celestialvault/instances/inst_findiff.py` | 差异对比器 |
| `str_to_dict` | `src/celestialvault/tools/TextTools.py` | 将字符串解析为字典，供 `fd_dict` 使用 |

## 测试重点

### `test_fd_str`

- 构造多组典型字符串对比用例：
  - 纯数字局部差异（如 `"1657"` vs `"1626"`）
  - 含重复模式差异（如 `"1234dtyjdtyjdtyj6789"` vs `"123456789"`）
  - 无公共字符的字符串（如 `"132"` vs `"456"`）
  - 键值对形式字符串（如 `"WBtopGlobal_register_version=..."` vs `"wb_view_log=..."`）
- 使用 `Findiffer("[", "]", "[]")` 实例调用 `fd_str`，输出差异标记结果。

### `test_fd_dict`

- 使用 `str_to_dict` 将两条复杂的 Cookie 风格字符串解析为字典。
- 调用 `fd_dict` 对比两个字典，验证键值级别差异。

## 运行方式

```bash
uv run pytest tests/test_findiff.py -s
```
