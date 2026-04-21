# `celestialvault.constants.suffix`

## 源文件
- `src/celestialvault/constants/suffix.py`

## 模块说明
定义各类文件后缀名列表及文件后缀到图标 emoji 的映射字典，用于文件分类和文件浏览器中的图标显示。

## 导入依赖
- 无

## 模块常量

### `IMG_SUFFIXES`
- **类型**: `list[str]`
- **值**: `[".jpg", ".png", ".jpeg", ".heic", ".bmp", ".tiff", ".webp", ".svg"]`
- **说明**: 常见图片文件后缀名列表，共 8 项

### `VIDEO_SUFFIXES`
- **类型**: `list[str]`
- **值**: `[".mp4", ".avi", ".mov", ".mkv", ".divx", ".mpg", ".flv", ".rm", ".rmvb", ".mpeg", ".wmv", ".3gp", ".vob", ".ogm", ".ogv", ".asf", ".ts", ".webm", ".mts", ".m2t", ".f4v", ".m4a", ".ogg", ".skm", ".mpe", ".asx", ".vdat"]`
- **说明**: 常见视频文件后缀名列表，共 27 项

### `AUDIO_SUFFIXES`
- **类型**: `list[str]`
- **值**: `[".mp3", ".wav", ".aac", ".flac", ".ogg", ".wma", ".m4a", ".alac", ".aiff", ".opus"]`
- **说明**: 常见音频文件后缀名列表，共 10 项

### `ZIP_SUFFIXES`
- **类型**: `list[str]`
- **值**: `[".zip", ".rar", ".tar", ".7z", ".gz", ".bz2", ".xz", ".zipx", ".tar.gz"]`
- **说明**: 常见压缩文件后缀名列表，共 9 项

### `TEXT_SUFFIXES`
- **类型**: `list[str]`
- **值**: `[".txt", ".md", ".json", ".xml", ".csv", ".tsv", ".yaml", ".yml", ".ini", ".conf", ".config", ".properties", ".prop", ".props"]`
- **说明**: 常见文本/配置文件后缀名列表，共 14 项

### `FILE_ICONS`
- **类型**: `dict[str, str]`
- **值**: 文件后缀名到 emoji 图标的映射字典
- **说明**: 首先批量将上述五类后缀列表中的条目映射为对应类别图标（图片: 📷, 视频: 🎬, 音频: 🎧, 压缩包: 📦, 文本: 📝），然后进一步覆盖更细粒度的映射：

| 类别 | 后缀示例 | 图标 |
|------|----------|------|
| 文档文件 | `.doc`/`.docx` | 📄 |
| 表格文件 | `.xls`/`.xlsx` | 📊 |
| 演示文件 | `.ppt`/`.pptx` | 📽️ |
| PDF | `.pdf` | 📚 |
| 网页文件 | `.html` | 🌐 |
| CSS | `.css` | 🎨 |
| JavaScript | `.js` | 📜 |
| JSON | `.json` | 🗄️ |
| XML | `.xml` | 🗂️ |
| 配置文件 | `.ini` | ⚙️ |
| 高质量音频 | `.flac`/`.alac` | 🎧 |
| 普通音频 | `.mp3`/`.aac` | 🎵 |
| 音效 | `.wav`/`.wma`/`.ogg` | 🔊 |
| GIF | `.gif` | 🎞️ |
| 备份文件 | `.bak` | 🛡️ |
| 光盘镜像 | `.iso` | 💿 |
| Python | `.py` | 🐍 |
| Java | `.java` | ☕ |
| C++ | `.cpp` | 🖥️ |
| C | `.c` | 📟 |
| C# | `.cs` | 🔷 |
| Ruby | `.rb` | 💎 |
| PHP | `.php` | 🐘 |
| Shell | `.sh` | 📜 |
| Batch | `.bat` | ⚙️ |
| Go | `.go` | 🌀 |
| Rust | `.rs` | 🦀 |
| Swift | `.swift` | 🦅 |
| Kotlin | `.kt` | 🔶 |
| TypeScript | `.ts`/`.tsx` | 📘 |
| JSX | `.jsx` | ⚛️ |
| Jupyter | `.ipynb` | 📓 |
| SQL | `.sql` | 🗃️ |
| 数据库 | `.db`/`.sqlite` | 🗄️ |
| Access | `.mdb`/`.accdb` | 🗃️ |
| PSD | `.psd` | 🎨 |
| AI | `.ai` | 🖌️ |
| XCF | `.xcf` | 🖼️ |
| Markdown | `.md` | 📝 |
| 文本 | `.txt` | 📝 |
| 默认 | `"default"` | ❓ |

## 用法示例

```python
from celestialvault.constants.suffix import IMG_SUFFIXES, VIDEO_SUFFIXES, FILE_ICONS

# 判断文件是否为图片
filename = "photo.jpg"
ext = "." + filename.rsplit(".", 1)[-1].lower()
if ext in IMG_SUFFIXES:
    print("这是一个图片文件")

# 获取文件图标
icon = FILE_ICONS.get(ext, FILE_ICONS["default"])
print(f"{icon} {filename}")  # 📷 photo.jpg

# 获取所有视频后缀
print(VIDEO_SUFFIXES)
```

## 关联
- `IMG_SUFFIXES` 可与 `celestialvault.constants.image_format` 中的 `IMAGE_SUFFIX_TO_FORMAT` 配合使用
- `FILE_ICONS` 可用于文件浏览器、文件管理工具中的图标显示
- 各后缀列表可用于文件分类、过滤等工具模块

## 顶层函数
- 无

## 类
- 无
