import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import logging
from constants.pi_digit import PI_STR_1E6
from tools.NumberUtils import get_pi_digits, get_pi_digits_from_ranges, find_sequence_in_pi, find_all_combinations_ratio

def test_get_pi_digits():
    position = [(13783, 13787), (115786, 115790), (8588, 8592), (122724, 122728), (120693, 120697), 
                (41874, 41878), (161538, 161542), (1231, 1235), (18058, 18062), (167, 169)]
    digit = get_pi_digits_from_ranges(position)
    
    logging.info(f"{'Test input':<15}: {position}")
    logging.info(f"{'Expected output':<15}: 552244442871634579700161695178671319555995250019")
    logging.info(f"{'Actual output':<15}: {digit}")


def test_find_sequence_in_pi():
    sequence = '552244-442871-634579-700161-695178-671319-555995-250019'
    result = find_sequence_in_pi(sequence)

    logging.info(f"{'Test input':<15}: {sequence}")
    logging.info(f"{'Expected output':<15}: ......")
    logging.info(f"{'Actual output':<15}: {result}")

def test_find_all_combinations_ratio():
    ratio = find_all_combinations_ratio(PI_STR_1E6, 5)

    logging.info(f"{'Expected output':<15}: 0.9999111111111111")
    logging.info(f"{'Actual output':<15}: {ratio}")