# test_parse.py

> 最后更新日期: 2026/06/28

## 作用

验证 `celestialvault.instances.inst_parse.HTMLContentParser` 对 HTML 片段的解析能力，包括文本、图片、视频资源的提取。

## 被测模块

| 模块 | 文件 | 说明 |
|------|------|------|
| `HTMLContentParser` | `src/celestialvault/instances/inst_parse.py` | 将 HTML 解析为 Markdown、图片、视频列表 |
| `BeautifulSoup` | 第三方依赖 `beautifulsoup4` | HTML 解析工具 |

## 测试重点

### `test_html_content_parser`

- 构造一段包含以下元素的 HTML 片段：
  - 普通段落文本
  - 带 `data-xkrkllgl` 属性的图片
  - 带 `data-config` 的 `dplayer` 视频容器
- 使用 `BeautifulSoup(html_content, "html.parser")` 解析。
- 创建 `HTMLContentParser()` 实例并调用 `parse(soup)`。
- 打印解析结果：
  - `md_list`：Markdown 内容列表
  - `video_list`：视频 URL 列表
  - `img_list`：图片 URL 列表

## 运行方式

```bash
uv run pytest tests/test_parse.py -s
```
