import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest, logging
from src.tools import print_directory_structure

def test_print_directory_structure():
    # Test with a valid directory
    exclude_dirs = ['.git', '.pytest_cache', '__pycache__']
    exclude_exts = ['.pyc', '.pyo']
    print()
    print_directory_structure(exclude_dirs = exclude_dirs, exclude_exts = exclude_exts)