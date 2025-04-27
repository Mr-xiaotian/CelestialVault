import pytest, logging
from celestialvault.tools.FileOperations import print_directory_structure, compress_folder, detect_identical_files, duplicate_files_report

def test_print_directory_structure():
    # Test with a valid directory
    exclude_dirs = ['.git', '.pytest_cache', '__pycache__']
    exclude_exts = ['.pyc', '.pyo']
    print()
    print_directory_structure(r'Q:\Project\test', exclude_dirs = exclude_dirs, exclude_exts = exclude_exts)

def _test_compress_folder():
    # Test with a valid directory
    # compress_folder(r'C:\Users\27342\OneDrive\Videos\compress_temp')
    pass

def _test_detect_identical_files():
    identical_dict = detect_identical_files(r"Q:\Project\test")
    duplicate_files_report(identical_dict)