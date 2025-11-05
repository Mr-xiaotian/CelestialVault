import pytest
import logging
from celestialvault.constants.pi_digit import PI_STR_1E6
from celestialvault.tools.NumberUtils import (
    get_pi_digits,
    get_pi_digits_from_ranges,
    segment_search_in_pi,
    greedy_search_in_pi,
    find_all_combinations_ratio,
    digit_frequency,
)


def test_get_pi_digits_from_ranges():
    position = [
        (13783, 13787),
        (115786, 115790),
        (8588, 8592),
        (122724, 122728),
        (120693, 120697),
        (41874, 41878),
        (161538, 161542),
        (1231, 1235),
        (18058, 18062),
        (167, 169),
    ]
    digit = get_pi_digits_from_ranges(position)

    logging.info(f"{'Test input':<15}: {position}")
    logging.info(
        f"{'Expected output':<15}: 552244442871634579700161695178671319555995250019"
    )
    logging.info(f"{'Actual output':<15}: {digit}")


def test_segment_search_in_pi():
    sequence_0 = "122276-137808-538450-398750-366190-218757-344157-583682"
    sequence_1 = "552244-442871-634579-700161-695178-671319-555995-250019"
    result = segment_search_in_pi(sequence_1, 5)

    logging.info(f"{'Test input':<15}: {sequence_1}")
    logging.info(f"{'Expected output':<15}: ......")
    logging.info(f"{'Actual output':<15}: {result}")


def test_greedy_search_in_pi():
    sequence_0 = "122276-137808-538450-398750-366190-218757-344157-583682"
    sequence_1 = "552244-442871-634579-700161-695178-671319-555995-250019"
    result = greedy_search_in_pi(sequence_1)

    logging.info(f"{'Test input':<15}: {sequence_1}")
    logging.info(f"{'Expected output':<15}: ......")
    logging.info(f"{'Actual output':<15}: {result}")


def test_find_all_combinations_ratio():
    ratio = find_all_combinations_ratio(PI_STR_1E6, 4)  # 5

    logging.info(f"{'Expected output':<15}: 0.9999111111111111")
    logging.info(f"{'Actual output':<15}: {ratio}")


def test_digit_frequency():
    digit = digit_frequency(PI_STR_1E6)

    logging.info(f"{'Actual output':<15}: {digit}")
