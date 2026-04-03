# instances/inst_findiff.py

## 源文件
- `src/celestialvault/instances/inst_findiff.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- `from ..tools.ListDictTools import dictkey_mix`
- `from ..tools.TextTools import calculate_similarity, get_lcs, string_split`

## 模块常量
- 无

## 顶层函数
- 无

## 类
### `Findiffer`
- 继承: `object`
- 说明: 字符串和字典差异比较工具，高亮显示两段文本之间的不同部分。
- 方法:
  - `def __init__(self, norm_end: str = '[', diff_end: str = ']', split_part_str: str = '[]') -> None`
  - `def fd_str(self, string_a: str, string_b: str, split_str: str = None)`
  - `def fd_dict(self, dict_a: dict, dict_b: dict)`
  - `def compare_strings(self, str1: str, str2: str, lcs_part: list[str] = None) -> None`
  - `def get_diff_ranges(self, origin_str: str, lcs_part: list[str]) -> list[list[int]]`
  - `def print_diffs(self, input_str: str, diff_ranges: list) -> None`
