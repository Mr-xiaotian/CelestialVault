# test_TextTools.py

> 最后更新日期: 2026/06/28

## 作用

验证 `celestialvault.tools.TextTools` 与 `celestialvault.tools.NumberUtils` 中字符串处理、中文文本统计、表格格式化、Reed-Solomon 编解码相关工具。

## 被测模块

| 模块 | 文件 | 说明 |
|------|------|------|
| `pro_slash` | `src/celestialvault/tools/TextTools.py` | 规范化字符串中的斜杠 |
| `str_to_dict` | `src/celestialvault/tools/TextTools.py` | 按分隔符解析字符串为字典 |
| `language_fingerprint` | `src/celestialvault/tools/TextTools.py` | 计算文本语言指纹（已移除，仅测试占位保留） |
| `calculate_valid_chinese_text` | `src/celestialvault/tools/TextTools.py` | 计算中文有效文本比例 |
| `calculate_valid_text` | `src/celestialvault/tools/TextTools.py` | 计算有效文本比例 |
| `format_table` | `src/celestialvault/tools/TextTools.py` | 格式化二维数据为文本表格 |
| `string_split` | `src/celestialvault/tools/TextTools.py` | 按固定长度拆分字符串 |
| `rs_encode` / `rs_decode` | `src/celestialvault/tools/TextTools.py` | Reed-Solomon 编解码 |
| `pad_bytes` / `unpad_bytes` | `src/celestialvault/tools/TextTools.py` | 字节补位与去补位 |
| `choose_square_container` / `redundancy_from_container` | `src/celestialvault/tools/NumberUtils.py` | 选择容器大小与冗余量 |

## 测试重点

### `test_pro_slash`

- 测试三种斜杠场景：
  - 混合斜杠字符串 `(W//R\S/H\\U)` 的规范化
  - URL 中转义斜杠 `https:\/\/...` 还原为正常 URL
  - 原始字符串 `this\\is\a\\test\\\\string` 的斜杠处理

### `test_str_to_dict`

- 默认分隔符：按换行与冒号解析。
- 自定义分隔符：按 `;` 与 `=` 解析，并处理空值情况。

### `_test_language_fingerprint`

- 占位测试，当前未启用。原设计用于读取本地小说文件并计算语言指纹；该函数在源码中已移除。

### `test_calculate_valid_text`

- 使用《夜晚的潜水艇》推荐语作为长文本输入。
- 分别计算中文有效比例与整体有效比例。

### `test_format_table`

- 输入不等长行数据、列名、行名，按居中对齐生成文本表格。

### `test_string_split`

- 将长字符串按固定长度 `3` 拆分。

### `test_rs_encode_decode`

- 生成 1KB 随机字节，使用 `rs_encode(data, nsym=600)` 编码。
- 断言编码后长度等于 `len(data) + nsym`。
- 随机破坏 100 个字节后调用 `rs_decode`，断言能恢复原始数据。

### `test_rs_workflow`

- 端到端容器化 RS 流程：
  1. `choose_square_container` 选择容器大小与冗余量
  2. `pad_bytes` 补位到容器载荷
  3. `rs_encode` 编码
  4. `rs_decode` 解码
  5. `unpad_bytes` 去补位
- 最终断言去补位后的数据与原始数据一致。

## 运行方式

```bash
uv run pytest tests/test_TextTools.py -s
```

> `_test_language_fingerprint` 依赖本地小说文件路径，当前未启用。
