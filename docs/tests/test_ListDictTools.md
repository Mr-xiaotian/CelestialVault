# test_ListDictTools.py

> 最后更新日期: 2026/06/28

## 作用

验证 `celestialvault.tools.ListDictTools` 中列表与字典常用工具函数：删除元素、批量替换、字典键集合运算、生成器分批。

## 被测模块

| 模块 | 文件 | 说明 |
|------|------|------|
| `list_removes` | `src/celestialvault/tools/ListDictTools.py` | 移除列表中所有指定值 |
| `list_replace` | `src/celestialvault/tools/ListDictTools.py` | 按规则批量替换列表元素 |
| `dictkey_mix` | `src/celestialvault/tools/ListDictTools.py` | 对两个字典的键集合做并/交/差运算 |
| `batch_generator` | `src/celestialvault/tools/ListDictTools.py` | 将迭代器按固定大小分批 |

## 测试重点

### `test_list_removes`

- 输入 `[1, 2, 3, 2, 4, 2]`，移除所有 `2`。
- 期望输出 `[1, 3, 4]`。

### `test_list_replace`

- 输入列表包含数字、字符串、lambda、嵌套列表等混合类型。
- 替换规则覆盖：
  - 精确值替换
  - 子串替换（如 `"123"` → `"321"`）
  - lambda 表达式替换
  - 列表对象替换
- 期望输出 `[1, 5, '321456', 6, [15, 'b'], 'def']`。

### `test_dictkey_mix`

- 输入两个字典：
  - `dict_a = {"a": 1, "b": 2, "c": 3}`
  - `dict_b = {"b": 2, "c": 4, "d": 5}`
- 验证返回四元组：
  - `key_max`: 并集 `['a', 'b', 'c', 'd']`
  - `key_min`: 交集 `['b', 'c']`
  - `dif_key_a`: 仅 A `['a']`
  - `dif_key_b`: 仅 B `['d']`

### `test_batch_generator`

- 输入 `range(1, 11)`，批次大小 `3`。
- 期望输出 `[[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]]`。

## 运行方式

```bash
uv run pytest tests/test_ListDictTools.py -s
```
