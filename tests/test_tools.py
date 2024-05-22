import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import logging
from src.tools.TextTools import string_split
from src.tools.FileOperations import compress_folder, get_all_file_paths


def test_string_split():
    input_string = ('dfg4354df6g654dfg585d8gd87fg56df132e1rg8df87f56g4d3s1dg45431', '3')
    except_result = []
    result = string_split(*input_string)

    logging.info(result)

def test_compress_folder():
    pass

def test_get_all_file_paths():
    file_path = get_all_file_paths('./tests')
    logging.info(file_path)