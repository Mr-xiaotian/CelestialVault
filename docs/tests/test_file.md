# test_file.py

> 最后更新日期: 2026/06/28

## 作用

验证 `celestialvault.instances.inst_file.FileTree` 与 `celestialvault.tools.FileOperations.get_dir_hash` 在真实目录结构上行为一致：既能正确构建并打印目录树，又能生成与独立哈希函数一致的根目录哈希。

## 被测模块

| 模块 | 文件 | 说明 |
|------|------|------|
| `FileTree` | `src/celestialvault/instances/inst_file.py` | 从本地路径构建目录树对象 |
| `get_dir_hash` | `src/celestialvault/tools/FileOperations.py` | 计算目录内容哈希 |

## 测试重点

### `test_print_tree`

- 以当前工作目录为输入，按给定规则过滤目录与扩展名：
  - 排除目录：`.git`、`.pytest_cache`、`.vscode`、`__pycache__`、`logs`、`fallback`、`old_logs`
  - 排除扩展名：`.txt`、`.prof`、`.json`、`.ipynb`
- 调用 `FileTree.build_from_path(..., max_depth=99)` 构建目录树，并执行 `print_tree()`。
- 断言 `file_tree.root.hash` 与 `get_dir_hash` 在相同过滤条件下返回的哈希一致，确认两种目录摘要实现结果相同。

## 运行方式

```bash
uv run pytest tests/test_file.py -s
```

> 因使用当前目录作为输入，结果会随仓库文件变化而变化。测试通过的核心判定是两种摘要方法一致，而非固定哈希值。
