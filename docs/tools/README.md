# tools/README.md

## 源文件
- src/celestialvault/tools/README.md

## 文档概要
该文件主要说明两个核心能力：

1. handle_dir_files
- 递归遍历目录并按后缀规则处理文件。
- 支持 serial/thread/process 三种执行模式。
- 处理后文件写入新的目标目录，并保持原始目录结构。
- 会记录处理错误并返回错误映射。

2. compress_dir
- 基于 handle_dir_files 的批处理封装。
- 按文件类型调用不同压缩逻辑（图片/视频/PDF）。
- 其他文件按复制处理。
- 支持并发执行并记录错误。

## 主要参数与行为
- dir_path: 输入目录路径。
- rules: 后缀到处理函数与重命名函数的映射。
- execution_mode: 任务执行模式（serial/thread/process）。
- progress_desc: 进度描述文本。

## 示例内容
源文档中包含：
- 按后缀处理 `.txt`、`.jpg` 的规则示例。
- 不区分后缀处理所有文件的示例。
- 错误文件回收与检查示例。
- 基于图片/视频/PDF 的压缩规则组合示例。
