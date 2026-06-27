# test_FileOperations.py

> 最后更新日期: 2026/06/28

## 作用

验证 `celestialvault.tools.FileOperations` 中文件查重相关接口：检测相同内容文件并生成重复文件报告。

## 被测模块

| 模块 | 文件 | 说明 |
|------|------|------|
| `detect_identical_files` | `src/celestialvault/tools/FileOperations.py` | 扫描目录，按内容哈希找出重复文件 |
| `duplicate_report` | `src/celestialvault/tools/FileOperations.py` | 将重复文件结果以可读格式输出 |

## 测试重点

### `test_detect_identical_files`

- 以当前工作目录 `.` 为输入，调用 `detect_identical_files` 查找内容完全相同的文件。
- 调用 `duplicate_report` 打印结果。
- 当前仅覆盖正向运行路径，未对结果数量做断言。

### `_test_compress_dir`

- 占位测试，当前仅 `pass`。
- 注释中保留了外部目录路径示例，用于后续补充目录压缩测试。

## 运行方式

```bash
uv run pytest tests/test_FileOperations.py -s
```

> 测试结果会随仓库文件变化而变化；目前主要检查接口是否可正常运行。
