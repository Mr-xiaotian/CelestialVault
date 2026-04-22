# `celestialvault.instances.inst_findiff`

> 📅 最后更新日期: 2026/04/17

## 源文件 - `src/celestialvault/instances/inst_findiff.py`

## 模块说明

提供字符串和字典差异比较工具类 `Findiffer`，基于最长公共子序列（LCS）高亮显示两段文本或字典之间的不同部分。

## 导入依赖

- `celestialvault.tools.ListDictTools.dictkey_mix` - 字典键集合操作
- `celestialvault.tools.TextTools.calculate_similarity` - 计算文本相似度
- `celestialvault.tools.TextTools.get_lcs` - 获取最长公共子序列
- `celestialvault.tools.TextTools.string_split` - 字符串分割

## 类

### `Findiffer`

- 继承: 无
- 说明: 字符串和字典差异比较工具，高亮显示两段文本之间的不同部分。

- 构造函数: `__init__(self, norm_end: str = '[', diff_end: str = ']', split_part_str: str = '[]') -> None`
  - 参数:
    - `norm_end` (`str`): 正常文本的结束标记，可使用 `'\033[0m'`、`'_'`、`'['` 等，默认 `'['`。
    - `diff_end` (`str`): 差异文本的结束标记，可使用 `'\033[1m'`、`'_'`、`']'` 等，默认 `']'`。
    - `split_part_str` (`str`): 分段显示字符串，可使用 `'-'`、`'_'`、`'[]'` 等，默认 `'[]'`。

- 方法:

  #### `fd_str(self, string_a, string_b, split_str=None)`
  - 签名: `fd_str(self, string_a: str, string_b: str, split_str: str = None) -> None`
  - 说明: 比较两个字符串的差异，按分隔符分段后逐段高亮不同部分并输出相似度。
  - 参数:
    - `string_a` (`str`): 第一个字符串。
    - `string_b` (`str`): 第二个字符串。
    - `split_str` (`str | None`): 分隔符，用于将字符串分段比较；为 `None` 时不分段。

  #### `fd_dict(self, dict_a, dict_b)`
  - 签名: `fd_dict(self, dict_a: dict, dict_b: dict) -> None`
  - 说明: 比较两个字典，对共有键的值进行差异对比，并列出各自特有的键。
  - 参数:
    - `dict_a` (`dict`): 第一个字典。
    - `dict_b` (`dict`): 第二个字典。

  #### `compare_strings(self, str1, str2, lcs_part=None)`
  - 签名: `compare_strings(self, str1: str, str2: str, lcs_part: list[str] = None) -> None`
  - 说明: 基于最长公共子序列高亮打印两个字符串的差异部分。
  - 参数:
    - `str1` (`str`): 第一个字符串。
    - `str2` (`str`): 第二个字符串。
    - `lcs_part` (`list[str] | None`): 预计算的最长公共子序列部分列表；为 `None` 时自动计算。

  #### `get_diff_ranges(self, origin_str, lcs_part)`
  - 签名: `get_diff_ranges(self, origin_str: str, lcs_part: list[str]) -> list[list[int]]`
  - 说明: 根据 LCS 返回的相似部分，计算字符串中不同区域的位置范围。
  - 参数:
    - `origin_str` (`str`): 原始字符串。
    - `lcs_part` (`list[str]`): 相似部分列表。
  - 返回值: 不同区域的位置列表 `[[start, end], ...]`。

  #### `print_diffs(self, input_str, diff_ranges)`
  - 签名: `print_diffs(self, input_str: str, diff_ranges: list) -> None`
  - 说明: 根据差异范围打印带高亮标记的字符串。
  - 参数:
    - `input_str` (`str`): 输入字符串。
    - `diff_ranges` (`list`): 差异区域的范围列表。

- 用法示例:

```python
from celestialvault.instances.inst_findiff import Findiffer

fd = Findiffer(norm_end='\033[0m', diff_end='\033[1m')

# 比较两个字符串
fd.fd_str("Hello World", "Hello Python")

# 按换行符分段比较
fd.fd_str("第一行\n第二行", "第一行\n修改行", split_str="\n")

# 比较两个字典
dict_a = {"title": "原始标题", "content": "原始内容", "extra": "仅a有"}
dict_b = {"title": "修改标题", "content": "原始内容", "new_key": "仅b有"}
fd.fd_dict(dict_a, dict_b)
```

- 关联: 依赖 `celestialvault.tools.TextTools` 中的 LCS 和相似度计算函数；依赖 `celestialvault.tools.ListDictTools` 的字典键操作。
