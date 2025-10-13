# handle_dir_files
handle_dir_files 是一个用于遍历文件夹并对其中的文件进行批量处理的函数。它能够根据文件的后缀执行指定的处理逻辑，并在处理完成后将文件保存到新的目录中，同时保留原始的文件夹结构。如果目标文件已经存在，处理将被跳过。该函数支持多种执行模式（串行、线程池、多进程），并能记录在处理过程中出现的错误。

## 特性
- **文件遍历与处理**：递归遍历指定文件夹中的所有文件，根据文件的后缀执行指定的处理操作。
- **目标文件夹管理**：处理后的文件将按照原文件夹结构保存到一个新的文件夹中。
- **多种执行模式**：支持串行（serial）、线程池（thread）、多进程（process）执行。
- **错误处理**：记录文件处理过程中出现的错误，并在处理完成后返回错误列表。
- **进度显示**：可选的进度条显示功能，适用于大规模文件处理时的任务监控。

## 参数说明

### handle_dir_files 函数
- dir_path: 要处理的文件夹的路径，支持字符串或 Path 对象，可以是相对路径或绝对路径。此文件夹中的所有文件将按照规则进行处理。
- rules: 一个字典，键为文件后缀名（不带 .），值为一个元组，包含两个函数：
  - 第一个函数用于处理该类型的文件，接受两个参数（源文件路径和目标文件路径）。
  -  第二个函数用于重命名目标文件的路径。
- execution_mode: 指定任务的执行模式，默认为 'serial'。支持以下选项：
    - 'serial'：串行执行任务。
    - 'thread'：多线程执行任务。
    - 'process'：多进程执行任务。
- progress_desc: 进度条的描述文字，用于显示当前正在处理的任务阶段。

### 返回值
- error_path_dict: 一个字典，记录了处理过程中遇到错误的文件及其对应的错误信息。字典的键是异常对象，值是对应发生错误的文件路径列表。

## 工作流程
- **遍历文件夹**：首先，handle_dir_files 遍历指定的文件夹，获取所有文件的路径。文件夹结构会被递归遍历，确保处理所有子文件夹中的文件。
- **应用规则**：根据文件的后缀，从 rules 中获取对应的处理函数和重命名函数。如果文件后缀不在 rules 中，则默认执行文件复制操作。
- **任务管理**：handle_dir_files 使用 HandleFileManager 类管理任务执行，HandleFileManager 继承自 TaskManager，并根据执行模式选择串行或并行处理文件。
- **目标文件夹管理**：处理后的文件保存在原始文件夹的父文件夹中新建的 "_re" 文件夹中，并保持与原文件相同的目录结构。
- **错误处理**：处理过程中遇到的错误会被捕捉，并将未能正确处理的文件保存到新文件夹，同时记录在 error_path_dict 中。

## 示例
### 1. 处理 .txt 和 .jpg 文件
```python
from pathlib import Path
import shutil

# 定义处理规则
rules = {
    'txt': (shutil.copy, lambda p: p.with_suffix('.bak')),   # 将 .txt 文件重命名为 .bak 文件并复制
    'jpg': (shutil.copy, lambda p: p.with_name(f"new_{p.name}"))  # 将 .jpg 文件加上前缀 "new_"
}

# 定义文件夹路径
dir_path = Path('path/to/source_dir')

# 执行处理
error_path_dict = handle_dir_files(dir_path, rules, execution_mode='thread', progress_desc="Processing files")

# 查看错误文件列表
if error_path_dict:
    print("处理过程中出现以下错误:")
    for error, paths in error_path_dict.items():
        print(f"{error}:")
        for path in paths:
            print(f"  {path}")
```

在这个示例中：

- .txt 文件将会被重命名为 .bak 后复制到目标文件夹。
- .jpg 文件将会在名称前加上 "new_" 前缀后复制到目标文件夹。
处理以多线程模式执行。

### 2. 处理所有文件（不区分后缀）
如果你想处理所有文件，并且不需要根据文件后缀名来区分处理方式，可以定义一个简单的默认处理规则：

```python
# 定义默认规则，所有文件都复制
rules = {
    '': (shutil.copy, lambda p: p)  # 不修改文件名，直接复制
}

# 执行处理
error_path_dict = handle_dir_files('source_dir', rules)
```

### 3. 处理遇到错误的文件
handle_dir_files 会将处理过程中遇到的错误文件记录下来，并在处理完成后返回。这些文件会在复制时被保存在新文件夹中，并且可以使用返回的 error_path_dict 进行进一步的检查和处理。

```python
error_files = handle_dir_files('source_dir', rules)

if error_files:
    for error, paths in error_files.items():
        print(f"遇到错误: {error}")
        for path in paths:
            print(f"错误文件: {path}")
```

# compress_dir

`compress_dir` 是一个用于批量压缩指定文件夹内图片、视频和 PDF 文件的函数，并保留文件夹的原始结构。对于不属于这些类别的文件，它将直接复制到新的目标文件夹。该函数允许通过串行、线程池或多进程方式执行，并且会记录处理过程中遇到的错误。

整体框架由handle_dir_files提供:

```python
def rename_mp4(file_path: Path) -> Path:
    name = file_path.stem.replace("_compressed", "")
    parent = file_path.parent
    return parent / Path(name + '_compressed.mp4')

def rename_pdf(file_path: Path) -> Path:
    name = file_path.stem.replace("_compressed", "")
    parent = file_path.parent
    return parent / Path(name + '_compressed.pdf')

from tools.ImageProcessing import compress_img
from tools.VideoProcessing import compress_video
from tools.DocumentConversion import compress_pdf
from constants import IMG_SUFFIXES, VIDEO_SUFFIXES

rules = {suffix: (compress_img, lambda x: x) for suffix in IMG_SUFFIXES}
rules.update({suffix: (compress_video,rename_mp4) for suffix in VIDEO_SUFFIXES})
rules.update({suffix: (compress_pdf,rename_pdf) for suffix in ['pdf', 'PDF']})

return handle_dir_files(dir_path, rules, execution_mode, progress_desc='Compressing dir')
```