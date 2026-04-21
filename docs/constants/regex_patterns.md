# `celestialvault.constants.regex_patterns`

## 源文件
- `src/celestialvault/constants/regex_patterns.py`

## 模块说明
预编译的常用正则表达式模式集合，涵盖中文匹配、邮箱、URL、电话号码、身份证号、日期时间等常见场景。参考来源：https://tool.oschina.net/regex/#

## 导入依赖
- `re`（标准库）

## 模块常量

### 文本匹配类

| 常量名 | 类型 | 正则表达式 | 说明 |
|--------|------|-----------|------|
| `CHINESE_REGEX` | `re.Pattern` | `[\u4e00-\u9fa5]+` | 匹配中文字符 |
| `DOUBLE_BYTE_REGEX` | `re.Pattern` | `[^\x00-\xff]` | 匹配双字节字符（含汉字） |
| `WHITESPACE_REGEX` | `re.Pattern` | `[\s\t\r\n]+` | 匹配空白行 |
| `CHINESE_NAME_REGEX` | `re.Pattern` | `^[\u4e00-\u9fa5]{2,}$` | 匹配中文姓名（至少两个汉字） |

### 邮箱匹配类

| 常量名 | 类型 | 说明 |
|--------|------|------|
| `EMAIL_REGEX_0` | `re.Pattern` | 基础邮箱匹配 `[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+` |
| `EMAIL_REGEX_1` | `re.Pattern` | 带域名长度限制的邮箱匹配 `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}` |
| `EMAIL_REGEX_2` | `re.Pattern` | RFC 兼容的高级邮箱匹配 |

### URL 匹配类

| 常量名 | 类型 | 说明 |
|--------|------|------|
| `URL_REGEX_0` | `re.Pattern` | 匹配 http/https/ftp 协议 URL `(https?\|ftp)://[^\s/$.?#].[^\s]*` |
| `URL_REGEX_1` | `re.Pattern` | 匹配任意协议 URL `[a-zA-z]+://\S*` |

### 电话号码匹配类

| 常量名 | 类型 | 说明 |
|--------|------|------|
| `PHONE_REGEX_0` | `re.Pattern` | 匹配国内电话号码（含区号）`(\(\d{3,4}\)\|\d{3,4}-\|\s)?\d{7,14}` |
| `PHONE_REGEX_1` | `re.Pattern` | 匹配国际电话号码 `\+?1?\d{9,15}` |
| `PHONE_REGEX_2` | `re.Pattern` | 匹配固定格式电话号码 `\d{3}-\d{8}\|\d{4}-\{7,8}` |

### 其他身份/地址类

| 常量名 | 类型 | 正则表达式 | 说明 |
|--------|------|-----------|------|
| `QQ_REGEX` | `re.Pattern` | `[1-9][0-9]{4,}` | 匹配腾讯 QQ 号 |
| `POSTCODE_REGEX` | `re.Pattern` | `[1-9]\d{5}(?!\d)` | 匹配中国邮政编码 |
| `ID_CARD_REGEX` | `re.Pattern` | `\d{17}([0-9]\|X)` | 匹配 18 位身份证号 |

### 日期时间类

| 常量名 | 类型 | 正则表达式 | 说明 |
|--------|------|-----------|------|
| `DATE_REGEX` | `re.Pattern` | `\d{4}-\d{2}-\d{2}` | 匹配 年-月-日 格式日期 |
| `TIME_REGEX` | `re.Pattern` | `\d{2}:\d{2}:\d{2}` | 匹配 时:分:秒 格式时间 |
| `DATETIME_REGEX` | `re.Pattern` | `\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}` | 匹配日期时间 |

### 通用格式类

| 常量名 | 类型 | 正则表达式 | 说明 |
|--------|------|-----------|------|
| `NUMBER_REGEX` | `re.Pattern` | `\d+` | 匹配数字 |
| `ALPHABET_REGEX` | `re.Pattern` | `^[a-zA-Z]+$` | 匹配纯字母 |
| `ALPHANUMERIC_REGEX` | `re.Pattern` | `^[a-zA-Z0-9]+$` | 匹配字母数字 |

### 网络/硬件类

| 常量名 | 类型 | 正则表达式 | 说明 |
|--------|------|-----------|------|
| `IP_REGEX` | `re.Pattern` | `^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$` | 匹配 IPv4 地址 |
| `MAC_REGEX` | `re.Pattern` | `^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$` | 匹配 MAC 地址 |
| `HEX_REGEX` | `re.Pattern` | `^[0-9a-fA-F]+$` | 匹配十六进制字符串 |

### 其他

| 常量名 | 类型 | 说明 |
|--------|------|------|
| `BANK_CARD_REGEX` | `re.Pattern` | 匹配 16 位或 19 位银行卡号 `^\d{16}\|\d{19}$` |
| `PASSWORD_STRENGTH_REGEX` | `re.Pattern` | 匹配强密码（至少 8 位，含大小写、数字、特殊字符） |

### `REGEX_PATTERNS`
- **类型**: `dict[str, re.Pattern]`
- **值**: `{"email": EMAIL_REGEX_0, "url": URL_REGEX_1, "phone": PHONE_REGEX_1}`
- **说明**: 将常用正则表达式按名称组织的字典，便于通过字符串键名访问

## 用法示例

```python
from celestialvault.constants.regex_patterns import CHINESE_REGEX, EMAIL_REGEX_0, REGEX_PATTERNS

# 提取中文字符
text = "Hello 你好 World 世界"
matches = CHINESE_REGEX.findall(text)
print(matches)  # ['你好', '世界']

# 匹配邮箱
email_text = "联系我: test@example.com"
match = EMAIL_REGEX_0.search(email_text)
print(match.group())  # "test@example.com"

# 通过字典使用
pattern = REGEX_PATTERNS["url"]
urls = pattern.findall("访问 https://example.com 获取更多信息")
```

## 关联
- 可用于文本处理、数据清洗、表单验证等工具模块
- `CHINESE_REGEX` 可与 `celestialvault.constants.constant` 中的 `KangxiRadicalsDict` 配合进行中文文本处理

## 顶层函数
- 无

## 类
- 无
