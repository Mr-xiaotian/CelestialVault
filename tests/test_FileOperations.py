import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest, logging
from tools.FileOperations import print_directory_structure, compress_folder

def test_print_directory_structure():
    # Test with a valid directory
    exclude_dirs = ['.git', '.pytest_cache', '__pycache__']
    exclude_exts = ['.pyc', '.pyo']
    print()
    print_directory_structure(r'C:\Users\27342\OneDrive\Videos\compress_temp', exclude_dirs = exclude_dirs, exclude_exts = exclude_exts)

def test_compress_folder():
    # Test with a valid directory
    compress_folder(r'C:\Users\27342\OneDrive\Videos\compress_temp')