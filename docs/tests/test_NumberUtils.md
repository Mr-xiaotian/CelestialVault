# test_NumberUtils.py

> 最后更新日期: 2026/06/28

## 作用

验证 `celestialvault.tools.NumberUtils` 中基于圆周率数字串的查询、统计与组合分析函数。

## 被测模块

| 模块 | 文件 | 说明 |
|------|------|------|
| `get_pi_digits` | `src/celestialvault/tools/NumberUtils.py` | 获取 π 指定区间数字 |
| `get_pi_digits_from_ranges` | `src/celestialvault/tools/NumberUtils.py` | 批量获取 π 多个区间数字 |
| `segment_search_in_pi` | `src/celestialvault/tools/NumberUtils.py` | 分段搜索序列在 π 中的位置 |
| `greedy_search_in_pi` | `src/celestialvault/tools/NumberUtils.py` | 贪心搜索序列在 π 中的位置 |
| `find_all_combinations_ratio` | `src/celestialvault/tools/NumberUtils.py` | 计算组合覆盖比例 |
| `digit_frequency` | `src/celestialvault/tools/NumberUtils.py` | 统计数字串中各数字出现频率 |

## 测试重点

### `test_get_pi_digits_from_ranges`

- 准备 10 组 `(start, end)` 位置区间。
- 调用 `get_pi_digits_from_ranges(position)` 批量提取 π 数字。
- 期望输出固定串 `552244442871634579700161695178671319555995250019`。

### `test_segment_search_in_pi`

- 输入由短横线连接的多段序列。
- 调用 `segment_search_in_pi(sequence_1, 5)`，验证分段搜索可执行。

### `test_greedy_search_in_pi`

- 输入同样的序列。
- 调用 `greedy_search_in_pi(sequence_1)`，验证贪心搜索可执行。

### `test_find_all_combinations_ratio`

- 以前 100 万位 π 字符串为输入，窗口大小 `4`。
- 期望比例约为 `0.9999111111111111`。

### `test_digit_frequency`

- 统计 `PI_STR_1E6` 中 0-9 各数字出现次数，打印频率分布。

## 运行方式

```bash
uv run pytest tests/test_NumberUtils.py -s
```

> 部分测试依赖 `celestialvault.constants.pi_digit.PI_STR_1E6`，若常量未加载或位数不足会导致失败。
