import pytest, logging
from celestialvault.tools.FileOperations import compress_dir, detect_identical_files, duplicate_files_report

def _test_compress_dir():
    # Test with a valid directory
    # compress_dir(r'C:\Users\27342\OneDrive\Videos\compress_temp')
    pass

def test_detect_identical_files():
    identical_dict = detect_identical_files(r".")
    duplicate_files_report(identical_dict)