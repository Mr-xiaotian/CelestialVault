# test_suber.py

> 最后更新日期: 2026/06/28

## 作用

验证 `celestialvault.instances.inst_sub.Suber` 对原始文本的清洗与格式化能力，覆盖 Markdown、HTML、列表、空白字符等复杂输入。

## 被测模块

| 模块 | 文件 | 说明 |
|------|------|------|
| `Suber` | `src/celestialvault/instances/inst_sub.py` | 文本清洗与规范化工具 |

## 测试重点

### `test_suber`

- 构造两段测试文本：
  - `test_text_0`：包含章节标题、列表、代码块、强调符号（`◆`）等 Markdown/类文档结构。
  - `test_text_1`：包含作者信息、HTML 段落、中文章节标题、特殊空白字符与不需要的换行。
- 创建 `Suber()` 实例并调用 `clear_text` 分别清洗两段文本。
- 打印 `test_text_0` 的清洗结果，验证：
  - 多余空白与特殊控制字符被移除
  - 段落结构被规范化
  - HTML 标签与 Markdown 符号按预期处理

## 运行方式

```bash
uv run pytest tests/test_suber.py -s
```

> `test_text_1` 的结果当前未打印，仅保留在注释中供调试使用。
