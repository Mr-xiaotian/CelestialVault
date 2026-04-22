# ruff: noqa: F403, F405
from .constant import *
from .image_format import *
from .pi_digit import *
from .regex_patterns import *
from .style_parameters import *
from .suffix import *

__all__ = [
    # constant
    "user_agent_list",
    "zh_headers_test",
    "GRAY",
    "NAVYBLUE",
    "WHITE",
    "RED",
    "GREEN",
    "BLUE",
    "YELLOW",
    "ORANGE",
    "PURPLE",
    "CYAN",
    "BLACK",
    "DARKGREEN",
    "DARKGRAY",
    "COLOR_LIST",
    "city_coordinate",
    "new_city_coordinate",
    "KangxiRadicalsDict",
    "CJKRadicalsSupplementDict",
    # image_format
    "IMAGE_SUFFIX_TO_FORMAT",
    # pi_digit
    "PI_STR_1E6",
    # regex_patterns
    "CHINESE_REGEX",
    "DOUBLE_BYTE_REGEX",
    "WHITESPACE_REGEX",
    "EMAIL_REGEX_0",
    "EMAIL_REGEX_1",
    "EMAIL_REGEX_2",
    "URL_REGEX_0",
    "URL_REGEX_1",
    "PHONE_REGEX_0",
    "PHONE_REGEX_1",
    "PHONE_REGEX_2",
    "QQ_REGEX",
    "POSTCODE_REGEX",
    "ID_CARD_REGEX",
    "DATE_REGEX",
    "TIME_REGEX",
    "DATETIME_REGEX",
    "NUMBER_REGEX",
    "ALPHABET_REGEX",
    "ALPHANUMERIC_REGEX",
    "IP_REGEX",
    "MAC_REGEX",
    "HEX_REGEX",
    "BANK_CARD_REGEX",
    "PASSWORD_STRENGTH_REGEX",
    "CHINESE_NAME_REGEX",
    "REGEX_PATTERNS",
    # style_parameters
    "style_params",
    "image_mode_params",
    # suffix
    "IMG_SUFFIXES",
    "VIDEO_SUFFIXES",
    "AUDIO_SUFFIXES",
    "ZIP_SUFFIXES",
    "TEXT_SUFFIXES",
    "FILE_ICONS",
]
