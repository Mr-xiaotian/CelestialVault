import re

"""
https://tool.oschina.net/regex/#
"""

# 匹配中文字符
CHINESE_REGEX = re.compile(r"[\u4e00-\u9fa5]+")

# 匹配双字节字符(包括汉字在内)
DOUBLE_BYTE_REGEX = re.compile(r"[^\x00-\xff]")

# 匹配空白行
WHITESPACE_REGEX = re.compile(r"[\s\t\r\n]+")

# 匹配Email地址
EMAIL_REGEX_0 = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
EMAIL_REGEX_1 = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
EMAIL_REGEX_2 = re.compile(
    r"[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*@(?:[\w](?:[\w-]*[\w])?\.)+[\w](?:[\w-]*[\w])?"
)

# 匹配网址URL
URL_REGEX_0 = re.compile(r"(https?|ftp)://[^\s/$.?#].[^\s]*")
URL_REGEX_1 = re.compile(r"[a-zA-z]+://\S*")

# 匹配国内电话号码
PHONE_REGEX_0 = re.compile(r"(\(\d{3,4}\)|\d{3,4}-|\s)?\d{7,14}")
PHONE_REGEX_1 = re.compile(r"\+?1?\d{9,15}")
PHONE_REGEX_2 = re.compile(r"\d{3}-\d{8}|\d{4}-\{7,8}")

# 匹配腾讯QQ号
QQ_REGEX = re.compile(r"[1-9][0-9]{4,}")

# 匹配中国邮政编码
POSTCODE_REGEX = re.compile(r"[1-9]\d{5}(?!\d)")

# 匹配18位身份证号
ID_CARD_REGEX = re.compile(r"\d{17}([0-9]|X)")

# 匹配(年-月-日)格式日期
DATE_REGEX = re.compile(r"\d{4}-\d{2}-\d{2}")
TIME_REGEX = re.compile(r"\d{2}:\d{2}:\d{2}")
DATETIME_REGEX = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")


# 常用正则表达式示例
NUMBER_REGEX = re.compile(r"\d+")
ALPHABET_REGEX = re.compile(r"^[a-zA-Z]+$")
ALPHANUMERIC_REGEX = re.compile(r"^[a-zA-Z0-9]+$")


# 特定格式正则表达式
IP_REGEX = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
MAC_REGEX = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")
HEX_REGEX = re.compile(r"^[0-9a-fA-F]+$")


# 银行卡号正则表达式
BANK_CARD_REGEX = re.compile(r"^\d{16}|\d{19}$")

# 密码强度正则表达式
PASSWORD_STRENGTH_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
)

# 中文姓名正则表达式
CHINESE_NAME_REGEX = re.compile(r"^[\u4e00-\u9fa5]{2,}$")

# 使用字典来组织正则表达式
REGEX_PATTERNS = {
    "email": EMAIL_REGEX_0,
    "url": URL_REGEX_1,
    "phone": PHONE_REGEX_1,
}
