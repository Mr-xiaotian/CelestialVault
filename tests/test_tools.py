import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import logging
from src.tools.TextTools import string_split
from src.tools.ListDictTools import list_removes


def test_string_split():
    input_string = ('dfg4354df6g654dfg585d8gd87fg56df132e1rg8df87f56g4d3s1dg45431', '3')
    except_result = []
    result = string_split(*input_string)

    logging.info(result)


def test_list_removes():
    input_list = [1, 2, 3, 2, 4, 2]
    result = list_removes(input_list, 2)
    logging.info("Test input: %s", input_list)
    logging.info("Expected output: [1, 3, 4]")
    logging.info("Actual output: %s", result)
    assert result == [1, 3, 4], "Should remove all 2s from the list"
