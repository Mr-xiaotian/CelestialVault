# CelestialVault

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个综合性的 Python 工具库，提供文件/图像/视频/文本处理、神经网络构建块、HTTP 请求封装、交互式测验框架以及大量常用常量与数据结构。

## 安装

```bash
# 从源码安装（开发模式）
pip install -e .

# 或安装生产依赖
pip install .
```

 requires **Python >= 3.10**。

## 项目结构

```
celestialvault/
├── constants/   # 静态常量与数据表
├── instances/   # 面向对象的工具类
└── tools/       # 函数式工具集
```

### 1. `constants` — 常用常量

| 模块 | 内容 |
|------|------|
| `constant` | `user_agent_list`、中国城市坐标、Unicode 部首字典、RGB 颜色常量 |
| `image_format` | `IMAGE_SUFFIX_TO_FORMAT`（42 种图像扩展名到 Pillow 格式的映射） |
| `pi_digit` | `PI_STR_1E6`（π 的前 1,000,000 位小数） |
| `regex_patterns` | 预编译正则：中文、邮箱、URL、手机号、身份证、IP/MAC 等 |
| `style_parameters` | `style_params`（20 种艺术调色板 HSV 参数）、`image_mode_params` |
| `suffix` | `IMG_SUFFIXES`、`VIDEO_SUFFIXES` 等文件后缀列表与 `FILE_ICONS` |

### 2. `instances` — 核心类库

| 模块 | 说明 |
|------|------|
| `inst_fetch.Fetcher` | 基于 `httpx` 的 HTTP 客户端，支持自动重试、Clash 代理切换 |
| `inst_save.Saver` | 统一文件保存器，支持文本/图像/DataFrame/JSON/Pickle 及批量下载 |
| `inst_file.FileTree` | 多线程文件树构建、JSON 序列化、增量更新与格式化打印 |
| `inst_file.FileDiff` | 目录差异比较与双向同步（`compare_trees`、`sync_dirs`） |
| `inst_imgcodecs` | 图像隐写编解码器家族：LSB、调色板、Reed-Solomon 纠错、冗余存储 |
| `inst_network` | 三层前馈神经网络与可组合的顺序网络（支持小批量 SGD） |
| `inst_quiz` | 基于 `ipywidgets` 的交互式测验框架（乘法速算、单词听写） |
| `inst_symmetric.SymmetricMap` | 泛型双向一对一映射（`a <-> b`） |
| `inst_units` | `HumanBytes`、`HumanTime`、`HumanTimestamp` 人类可读数值包装器 |
| `inst_findiff.Findiffer` | 基于 LCS 的文本/字典差异高亮工具 |
| `inst_parse.HTMLContentParser` | BeautifulSoup 树遍历，提取文本、图片、视频信息 |
| `inst_sub.Suber` | 中文小说文本清洗与文件名净化正则工具 |

### 3. `tools` — 函数式工具集

| 模块 | 核心功能 |
|------|---------|
| `FileOperations` | 目录批量处理、压缩/解压缩（zip/rar/tar/7z）、重复文件/目录检测、哈希计算 |
| `ImageProcessing` | 图像压缩、格式转换、PDF 合成、调色板生成、SSIM 比较、PNG tEXt 读写、损坏模拟 |
| `VideoProcessing` | 视频压缩（H.264）、GIF 转视频、视频旋转、编码检测、DAR 校正 |
| `AudioProcessing` | MP3 与 WAV 互转 |
| `DocumentConversion` | PDF 合并（含书签）、压缩、页面宽度统一、Markdown 转 PDF |
| `TextTools` | CRC32、长度头、Base64、zlib、Reed-Solomon 编解码、LCS、表格格式化 |
| `NumberUtils` | π  digit 查询、幻方验证与生成、Miller-Rabin 素数检测、平方容器计算 |
| `ListDictTools` | 列表/字典批处理、方阵转换 |
| `Utilities` | 时间格式化、函数字节码比较、递归内存计算、计时装饰器 |
| `SampleGenerate` | 测试数据工厂（图像树、多尺寸 PDF、随机矩阵等） |

## 快速示例

### 文件树与差异对比

```python
from celestialvault.instances.inst_file.file_tree import FileTree
from celestialvault.instances.inst_file.file_diff import compare_trees

tree1 = FileTree.build_from_path("/path/to/dir1")
tree2 = FileTree.build_from_path("/path/to/dir2")

diff = compare_trees(tree1, tree2, compare_hash=True)
diff.print_diff_tree()
diff.sync_dirs(mode="->")   # 以 dir1 为准同步到 dir2
```

### 图像隐写编解码

```python
from celestialvault.instances.inst_imgcodecs import CODEC_REGISTRY

codec = CODEC_REGISTRY["rgba_ori"]
img = codec.encode_text("Hello, World!")
img.save("encoded.png")

text = codec.decode_text(img)
print(text)  # Hello, World!
```

### HTTP 请求（自动代理切换）

```python
from celestialvault.instances.inst_fetch import Fetcher

fetcher = Fetcher(use_proxy=True, wait_time=10)
text = fetcher.getText("https://example.com/api")
```

### 批量保存与下载

```python
from celestialvault.instances.inst_save import Saver

saver = Saver(base_path="./output", overwrite=False)
saver.save_json({"key": "value"}, "config", file_suffix=".json")

# 批量下载
tasks = [
    ("https://example.com/a.jpg", "img_a", ".jpg"),
    ("https://example.com/b.jpg", "img_b", ".jpg"),
]
saver.download_urls(tasks, chain_mode="serial", show_progress=True)
```

## 文档

所有模块的详细 API 文档位于 `docs/` 目录，与源代码一一对应：

- [`docs/constants/`](./docs/constants/) — 常量模块文档
- [`docs/instances/`](./docs/instances/) — 类库文档
- [`docs/tools/`](./docs/tools/) — 工具函数文档

## 测试

```bash
pytest
```

## 许可证

[MIT](LICENSE)
