# constants/__init__.py

> 📅 最后更新日期: 2026/06/28

## 源文件
- `src/celestialvault/constants/__init__.py`

## 模块说明
`celestialvault.constants` 子包的入口文件，通过 `from .constant import *` 等方式从各常量模块批量导入符号，并显式维护 `__all__` 列表以控制通配导入的公开导出内容。

## 导入依赖
- `from .constant import *`
- `from .image_format import *`
- `from .pi_digit import *`
- `from .regex_patterns import *`
- `from .style_parameters import *`
- `from .suffix import *`

## `__all__` 导出列表

以下符号可通过 `from celestialvault.constants import *` 通配导入。由于 `__init__.py` 使用 `*` 导入，实际来源以各子模块为准；此处按子模块重新分组展示。

### 来自 `constant.py`
- `user_agent_list`
- `zh_headers_test`
- 颜色常量：`BLACK`、`BLUE`、`CYAN`、`DARKGRAY`、`DARKGREEN`、`GRAY`、`GREEN`、`NAVYBLUE`、`ORANGE`、`PURPLE`、`RED`、`WHITE`、`YELLOW`
- `COLOR_LIST`
- `city_coordinate`、`new_city_coordinate`
- `KangxiRadicalsDict`、`CJKRadicalsSupplementDict`

### 来自 `image_format.py`
- `IMAGE_SUFFIX_TO_FORMAT`

### 来自 `pi_digit.py`
- `PI_STR_1E6`

### 来自 `regex_patterns.py`
- `ALPHABET_REGEX`、`ALPHANUMERIC_REGEX`
- `BANK_CARD_REGEX`
- `CHINESE_NAME_REGEX`、`CHINESE_REGEX`
- `DATETIME_REGEX`、`DATE_REGEX`
- `DOUBLE_BYTE_REGEX`
- `EMAIL_REGEX_0`、`EMAIL_REGEX_1`、`EMAIL_REGEX_2`
- `HEX_REGEX`
- `ID_CARD_REGEX`
- `IP_REGEX`
- `MAC_REGEX`
- `NUMBER_REGEX`
- `PASSWORD_STRENGTH_REGEX`
- `PHONE_REGEX_0`、`PHONE_REGEX_1`、`PHONE_REGEX_2`
- `POSTCODE_REGEX`
- `QQ_REGEX`
- `REGEX_PATTERNS`
- `TIME_REGEX`
- `URL_REGEX_0`、`URL_REGEX_1`
- `WHITESPACE_REGEX`

### 来自 `style_parameters.py`
- `image_mode_params`
- `style_params`

### 来自 `suffix.py`
- `AUDIO_SUFFIXES`
- `IMG_SUFFIXES`
- `TEXT_SUFFIXES`
- `VIDEO_SUFFIXES`
- `ZIP_SUFFIXES`
- `FILE_ICONS`

## 用法示例

```python
from celestialvault.constants import (
    RED,
    IMAGE_SUFFIX_TO_FORMAT,
    EMAIL_REGEX_0,
    IMG_SUFFIXES,
    style_params,
)

# 颜色常量
print(RED)  # (255, 0, 0)

# 图片后缀映射
print(IMAGE_SUFFIX_TO_FORMAT[".png"])  # "PNG"

# 正则表达式
print(EMAIL_REGEX_0.search("test@example.com").group())

# 图片后缀
print(".gif" in IMG_SUFFIXES)  # True

# 风格参数
print(list(style_params.keys()))
```

## 顶层函数
- 无

## 类
- 无
