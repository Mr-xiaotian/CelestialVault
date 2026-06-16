IMG_SUFFIXES = [
    ".jpg",
    ".png",
    ".jpeg",
    ".heic",
    ".bmp",
    ".tiff",
    ".webp",
    ".svg",
]

VIDEO_SUFFIXES = [
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".divx",
    ".mpg",
    ".flv",
    ".rm",
    ".rmvb",
    ".mpeg",
    ".wmv",
    ".3gp",
    ".vob",
    ".ogm",
    ".ogv",
    ".asf",
    ".ts",
    ".webm",
    ".mts",
    ".m2t",
    ".f4v",
    ".m4a",
    ".ogg",
    ".skm",
    ".mpe",
    ".asx",
    ".vdat",
]

AUDIO_SUFFIXES = [
    ".mp3",
    ".wav",
    ".aac",
    ".flac",
    ".ogg",
    ".wma",
    ".m4a",
    ".alac",
    ".aiff",
    ".opus",
]

ZIP_SUFFIXES = [
    ".zip",
    ".rar",
    ".tar",
    ".7z",
    ".gz",
    ".bz2",
    ".xz",
    ".zipx",
    ".tar.gz",
]

TEXT_SUFFIXES = [
    ".txt",
    ".md",
    ".json",
    ".xml",
    ".csv",
    ".tsv",
    ".yaml",
    ".yml",
    ".ini",
    ".conf",
    ".config",
    ".properties",
    ".prop",
    ".props",
]

FILE_ICONS: dict[str, str] = {}
FILE_ICONS.update(dict.fromkeys(IMG_SUFFIXES, "📷"))
FILE_ICONS.update(dict.fromkeys(VIDEO_SUFFIXES, "🎬"))
FILE_ICONS.update(dict.fromkeys(AUDIO_SUFFIXES, "🎧"))
FILE_ICONS.update(dict.fromkeys(ZIP_SUFFIXES, "📦"))
FILE_ICONS.update(dict.fromkeys(TEXT_SUFFIXES, "📝"))
FILE_ICONS.update(
    {
        # 文档文件
        ".md": "📝",
        ".txt": "📝",
        ".doc": "📄",
        ".docx": "📄",
        ".xls": "📊",
        ".xlsx": "📊",
        ".ppt": "📽️",
        ".pptx": "📽️",
        ".pdf": "📚",
        ".html": "🌐",
        ".css": "🎨",
        ".js": "📜",
        ".json": "🗄️",
        ".xml": "🗂️",
        ".ini": "⚙️",
        # 音频文件
        ".flac": "🎧",
        ".alac": "🎧",  # 高质量音频
        ".mp3": "🎵",
        ".aac": "🎵",  # 普通音频
        ".wav": "🔊",
        ".wma": "🔊",
        ".ogg": "🔊",  # 压缩音频/音效
        # 特殊文件
        ".gif": "🎞️",
        ".bak": "🛡️",
        ".iso": "💿",
        # 代码文件
        ".py": "🐍",
        ".java": "☕",
        ".cpp": "🖥️",
        ".c": "📟",
        ".cs": "🔷",
        ".rb": "💎",
        ".php": "🐘",
        ".sh": "📜",
        ".bat": "⚙️",
        ".go": "🌀",
        ".rs": "🦀",
        ".swift": "🦅",
        ".kt": "🔶",
        ".ts": "📘",
        ".jsx": "⚛️",
        ".tsx": "📘",
        ".ipynb": "📓",  # Jupyter Notebook
        # 数据库文件
        ".sql": "🗃️",
        ".db": "🗄️",
        ".sqlite": "🗄️",
        ".mdb": "🗃️",
        ".accdb": "🗃️",
        # 图像编辑文件
        ".psd": "🎨",
        ".ai": "🖌️",
        ".xcf": "🖼️",
        # 默认
        "default": "❓",
    }
)
