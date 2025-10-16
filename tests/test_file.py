import pytest, logging

from celestialvault.instances.inst_file import FileTree
from celestialvault.tools.FileOperations import get_dir_hash


def test_print_tree():
    # Test with a valid directory
    exclude_dirs=['.git', '.pytest_cache', '.vscode', '__pycache__', 'logs', 'fallback', 'old_logs']
    exclude_exts=[".txt", ".prof", ".json", ".ipynb"]
    print()

    file_tree = FileTree.build_from_path(r'.', exclude_dirs = exclude_dirs, exclude_exts = exclude_exts, max_depth=99)
    file_tree.print_tree()

    assert file_tree.root.hash == get_dir_hash(r'.', exclude_dirs = exclude_dirs, exclude_exts = exclude_exts)
    print("\nPass hash test.")
