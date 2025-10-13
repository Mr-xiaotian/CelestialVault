import pytest, logging
from celestialvault.instances.inst_file import FileTree


def test_print_tree():
    # Test with a valid directory
    exclude_dirs = ['.git', '.pytest_cache', '__pycache__']
    exclude_exts = ['.pyc', '.pyo']
    print()

    file_tree = FileTree.build_from_path(r'Q:\Project\test', exclude_dirs = exclude_dirs, exclude_exts = exclude_exts)
    file_tree.print_tree()
