import json
from pathlib import Path

from wcwidth import wcswidth

from ...constants import FILE_ICONS
from ...instances.inst_units import HumanBytes, HumanTimestamp
from ...tools.FileOperations import (
    get_dir_mtime,
    get_dir_size,
    get_file_mtime,
    get_file_size,
    get_files_info_recursive,
)
from .file_node import BaseNode, DirNode, ExcludedDirsNode, ExcludedFilesNode, FileNode


class FileTree:
    def __init__(self, root: DirNode, path: Path):
        """
        初始化文件树。

        :param root: 根目录节点。
        :param path: 根目录的路径。
        """
        self.root = root
        self.path = path

    @classmethod
    def build_from_path(cls, root_path: Path, exclude_names=None, exclude_exts=None):
        """
        从路径构建文件树。

        :param root_path: 根目录路径
        :param exclude_names: 要排除的目录名称集合。
        :param exclude_exts: 要排除的文件扩展名集合。
        :return: 文件树
        :raises ValueError: 如果路径不是目录
        """
        root_path = Path(root_path)
        if not root_path.is_dir():
            raise ValueError(f"Path {root_path} is not a directory")

        exclude_names = set(exclude_names or [])
        exclude_exts = set(exclude_exts or [])

        def _build(node_path: Path, level: int) -> BaseNode:
            if node_path.is_file():
                node_info = _info.get(node_path, {})
                size = node_info.get("size", HumanBytes(0))
                mtime = node_info.get("mtime", HumanTimestamp(0))
                icon = FILE_ICONS.get(node_path.suffix.lower(), FILE_ICONS["default"])
                return FileNode(
                    node_path.name,
                    node_path.suffix,
                    node_path,
                    size,
                    mtime,
                    icon,
                    level,
                )

            entries = list(node_path.iterdir())
            children = []

            total_size = HumanBytes(0)
            dir_mtime = HumanTimestamp(0)

            excluded_dirs = []
            excluded_files = []

            for child in entries:
                if child.is_dir() and child.name in exclude_names:
                    excluded_dirs.append(child)
                elif child.is_file() and child.suffix.lower() in exclude_exts:
                    excluded_files.append(child)
                else:
                    cnode = _build(child, level + 1)
                    children.append(cnode)
                    total_size += cnode.size
                    dir_mtime = max(dir_mtime, cnode.mtime)

            if excluded_dirs:
                exc_size = sum((get_dir_size(d) for d in excluded_dirs), HumanBytes(0))
                exc_mtime = max(get_dir_mtime(d) for d in excluded_dirs)
                total_size += exc_size
                dir_mtime = max(dir_mtime, exc_mtime)
                children.append(
                    ExcludedDirsNode(
                        len(excluded_dirs), node_path, exc_size, exc_mtime, level + 1
                    )
                )

            if excluded_files:
                exc_size = sum((get_file_size(f) for f in excluded_files), HumanBytes(0))
                exc_mtime = max(get_file_mtime(f) for f in excluded_files)
                total_size += exc_size
                dir_mtime = max(dir_mtime, exc_mtime)
                children.append(
                    ExcludedFilesNode(
                        len(excluded_files), node_path, exc_size, exc_mtime, level + 1
                    )
                )

            return DirNode(
                node_path.name,
                node_path,
                total_size,
                dir_mtime,
                level,
                children,
            )

        _info = get_files_info_recursive(root_path)
        return cls(_build(root_path, 0), root_path)

    # ---- 序列化 / 反序列化 ----

    _CACHE_DIR = ".file_tree"

    def _node_to_dict(self, node: BaseNode) -> dict:
        """将节点递归转换为可 JSON 序列化的字典。"""
        d = {
            "name": node.name,
            "path": node.node_path.as_posix(),
            "size": int(node.size),
            "mtime": float(node.mtime),
            "icon": node.icon,
            "level": node.level,
            "is_dir": node.is_dir(),
        }
        if node.is_dir():
            d["children"] = [self._node_to_dict(c) for c in node.children]
        else:
            d["suffix"] = node.suffix
        return d

    @staticmethod
    def _dict_to_node(d: dict) -> BaseNode:
        """将字典递归还原为节点。"""
        if d["is_dir"]:
            children = [FileTree._dict_to_node(c) for c in d["children"]]
            return DirNode(
                name=d["name"],
                node_path=Path(d["path"]),
                size=HumanBytes(d["size"]),
                mtime=HumanTimestamp(d["mtime"]),
                level=d["level"],
                children=children,
            )
        return FileNode(
            name=d["name"],
            suffix=d["suffix"],
            node_path=Path(d["path"]),
            size=HumanBytes(d["size"]),
            mtime=HumanTimestamp(d["mtime"]),
            icon=d["icon"],
            level=d["level"],
        )

    def _cache_path(self) -> Path:
        """返回缓存 JSON 的路径: <root>/.file_tree/<root_name>.json"""
        cache_dir = self.path / self._CACHE_DIR
        return cache_dir / f"{self.path.name}.json"

    def save(self) -> Path:
        """
        将文件树序列化为 JSON 并保存到 <root>/.file_tree/<root_name>.json。

        JSON 中额外存储 root_mtime（通过 get_dir_mtime 计算），供 update 时比对。

        :return: 写入的 JSON 文件路径。
        """
        data = {
            "root_path": self.path.as_posix(),
            "root_mtime": self.root.mtime,
            "tree": self._node_to_dict(self.root),
        }
        path = self._cache_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return path

    @classmethod
    def load(cls, root_path: str | Path) -> "FileTree":
        """
        从 <root_path>/.file_tree/<dir_name>.json 还原文件树。

        :param root_path: 根目录路径，用于定位 .file_tree 下的缓存 JSON。
        :return: 还原的 FileTree 对象。
        :raises FileNotFoundError: 找不到对应的缓存文件时抛出。
        """
        root_path = Path(root_path)
        cache_file = root_path / cls._CACHE_DIR / f"{root_path.name}.json"
        if not cache_file.exists():
            raise FileNotFoundError(f"Cache file not found: {cache_file}")

        data = json.loads(cache_file.read_text(encoding="utf-8"))
        root_node = cls._dict_to_node(data["tree"])
        return cls(root_node, root_path)

    def update(self) -> bool:
        """
        检查目录 mtime 是否变化，若变化则重新构建并保存。

        比较方式：用 get_dir_mtime 重新计算 root 的 mtime，与缓存 JSON
        中记录的 root_mtime 比对。

        :return: True 表示已更新，False 表示无变化。
        """
        cache_file = self._cache_path()

        if cache_file.exists():
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            saved_mtime = data.get("root_mtime", 0)
        else:
            saved_mtime = 0

        current_mtime = float(get_dir_mtime(self.path))
        if current_mtime == saved_mtime:
            return False

        new_tree = FileTree.build_from_path(self.path)
        self.root = new_tree.root
        self.save()
        return True

    # ---- 打印 ----

    def print_tree(self, max_depth=3, show_files=True):
        """
        递归打印整棵文件树，目录在前、文件在后。

        :param max_depth: 最大打印深度。
        :param show_files: 是否显示文件节点，为 False 时只显示目录结构。
        :return: None
        """

        def _is_excluded(node: BaseNode) -> bool:
            return isinstance(node, (ExcludedFilesNode, ExcludedDirsNode))

        def _get_display_name(node: BaseNode, depth: int) -> str:
            if node.is_dir() and hasattr(node, "children") and node.children and depth >= max_depth:
                return node.name + "[已折叠]"
            return node.name

        def _print(node: BaseNode, depth: int, max_name_len: int = 0):
            display_name = _get_display_name(node, depth)
            node.print(name=display_name, max_name_len=max_name_len)

            if _is_excluded(node):
                return
            if node.is_dir() and hasattr(node, "children") and node.children and depth >= max_depth:
                return
            if not node.is_dir() or not hasattr(node, "children") or not node.children:
                return

            dirs = []
            files = []
            child_names = []

            for child in node.children:
                if not show_files and not child.is_dir():
                    continue
                if child.is_dir():
                    dirs.append(child)
                else:
                    files.append(child)
                child_names.append(_get_display_name(child, depth + 1))

            child_max_name_len = max(
                (wcswidth(name) for name in child_names), default=0
            )

            for d in dirs:
                _print(d, depth + 1, child_max_name_len)
            for f in files:
                _print(f, depth + 1, child_max_name_len)

        _print(self.root, 0)
