# `celestialvault.instances.inst_quiz`

> 📅 最后更新日期: 2026/04/21

## 源文件 - `src/celestialvault/instances/inst_quiz.py`

## 模块说明

提供基于 Jupyter ipywidgets 的交互式测验框架，包含通用测验基类 `QuizBase`、乘法速算测验 `MultiplicationQuiz` 和单词听写测验 `DictationQuiz`。

## 导入依赖

- `random` - 随机数生成
- `re` - 正则表达式（解析模式字符串）
- `ipywidgets` - Jupyter 交互组件
- `IPython.display.clear_output`, `IPython.display.display` - Jupyter 显示控制
- `celestialvault.instances.inst_symmetric.SymmetricMap` - 双向映射（用于单词测验）

## 类

### `QuizBase`

- 继承: 无
- 说明: 通用测验 UI 框架，提供题目显示、答案检查、计分、历史记录和结束汇总功能。子类需实现 `question_text()` 和 `generate_problem()` 方法。

- 构造函数: `__init__(self, title='测验', input_type='text')`
  - 参数:
    - `title` (`str`): 测验标题，默认 `'测验'`。
    - `input_type` (`str`): 输入类型，`'text'` 使用 `widgets.Text`，`'int'` 使用 `widgets.IntText`，默认 `'text'`。
  - 属性:
    - `self.score` (`int`): 当前得分。
    - `self.total_questions` (`int`): 已答题数。
    - `self.history` (`list[tuple[str, int, bool]]`): 答题历史记录 `(题目文本, 正确答案, 是否正确)`。
  - 构造时自动调用 `generate_problem()` 生成第一题，并创建和显示 UI 组件。

- 方法:

  #### `question_text(self)`
  - 签名: `question_text(self) -> str`
  - 说明: 返回当前题目的显示文本（子类必须实现）。

  #### `generate_problem(self)`
  - 签名: `generate_problem(self) -> None`
  - 说明: 生成一道新题目，设置 `self.correct_answer`（子类必须实现）。

  #### `_check_answer(self, _)`
  - 说明: 检查用户答案是否正确，更新得分和历史记录，显示结果。

  #### `_next_question(self, _)`
  - 说明: 生成下一题并重置输入框。

  #### `_exit_quiz(self, _)`
  - 说明: 结束练习，显示汇总统计和答题历史 HTML 表格，禁用所有控件。

  #### `_summary(self)`
  - 签名: `_summary(self) -> dict`
  - 说明: 返回包含 `score`、`total`、`accuracy`、`history` 的汇总字典。

- 关联: 被 `MultiplicationQuiz` 和 `DictationQuiz` 继承。

---

### `MultiplicationQuiz`

- 继承: `QuizBase`
- 说明: 乘法速算测验，支持多种出题模式。

- 构造函数: `__init__(self, digit_num: int, modes: list[str] = None)`
  - 参数:
    - `digit_num` (`int`): 乘法数字的位数（至少为 1）。
    - `modes` (`list[str] | None`): 出题模式列表，默认 `['random']`。
  - 支持的模式:
    - `'square'` - 平方
    - `'square_with_5'` - 个位为5的平方
    - `'varied_digit_sum_10'` - 个位之和为10
    - `'fixed_digit_sum_10'` - 十位之和为10、个位相同
    - `'repeated_number_9'` - 重复数字乘以9
    - `'random'` - 随机
    - `'multiply<N>'` - 乘以指定数（如 `'multiply11'`）
    - `'nearby<N>'` - 接近指定数（如 `'nearby100'`）
    - `'square_difference<N>'` - 平方差速算（如 `'square_difference5'`）
    - `'range_<start>_<end>'` - 指定范围（如 `'range_10_99'`）

- 方法:

  #### `generate_problem(self)`
  - 说明: 根据 modes 列表选择出题方式，随机选取一种模式生成题目，设置 `self.num1`、`self.num2`、`self.correct_answer`。

  #### `question_text(self)`
  - 返回值: 形如 `"12 x 34 = ?"` 的题目文本。

  #### `generate_nearby(self, near_num)`
  - 签名: `generate_nearby(self, near_num) -> tuple[int, int]`
  - 说明: 生成一个接近指定数字的乘法题目，偏移量在 -9 到 9 之间（不含0）。
  - 参数: `near_num` (`int`): 基准数字。
  - 返回值: `(num1, num2)` 乘法题目的两个数字。

  #### `generate_multiply_num(self, multiplicand)`
  - 签名: `generate_multiply_num(self, multiplicand) -> tuple[int, int]`
  - 说明: 生成一个乘数为指定数字的乘法题目。
  - 参数: `multiplicand` (`int`): 指定的乘数。
  - 返回值: `(num, multiplicand)` 元组。

  #### `generate_square(self)`
  - 签名: `generate_square(self) -> tuple[int, int]`
  - 说明: 生成一个数的平方题目。
  - 返回值: `(num, num)` 同一个数字组成的元组。

  #### `generate_square_with_5(self)`
  - 签名: `generate_square_with_5(self) -> tuple[int, int]`
  - 说明: 生成个位为 5 的数的平方题目。
  - 返回值: `(num, num)` 个位为 5 的同一个数字。

  #### `generate_varied_digit_sum_10(self)`
  - 签名: `generate_varied_digit_sum_10(self) -> tuple[int, int]`
  - 说明: 生成个位数相加为 10、十位相同的两个数的乘积题目。
  - 返回值: `(num1, num2)` 元组。

  #### `generate_fixed_digit_sum_10(self)`
  - 签名: `generate_fixed_digit_sum_10(self) -> tuple[int, int]`
  - 说明: 生成十位数之和为 10、个位数相同的两个数的乘积题目。
  - 返回值: `(num1, num2)` 元组。

  #### `generate_square_difference(self, end_num)`
  - 签名: `generate_square_difference(self, end_num) -> tuple[int, int]`
  - 说明: 生成形如 `(a+b)(a-b)` 的速算乘法题目。
  - 参数: `end_num` (`int`): 基准数字的个位部分。
  - 返回值: `(a+b, a-b)` 元组。

  #### `generate_repeated_number_times_9(self)`
  - 签名: `generate_repeated_number_times_9(self) -> tuple[int, int]`
  - 说明: 生成重复数字乘以 9 的乘法题目。
  - 返回值: `(num1, num2)` 元组。

  #### `generate_random_problem(self)`
  - 签名: `generate_random_problem(self) -> tuple[int, int]`
  - 说明: 生成随机乘法题目。
  - 返回值: `(num1, num2)` 元组。

  #### `generate_range_problem(self, start, end)`
  - 签名: `generate_range_problem(self, start: int, end: int) -> tuple[int, int]`
  - 说明: 生成指定范围内的随机乘法题目。自动纠正 start/end 顺序。
  - 参数:
    - `start` (`int`): 范围起始值。
    - `end` (`int`): 范围结束值。
  - 返回值: `(num1, num2)` 元组。

- 用法示例:

```python
from celestialvault.instances.inst_quiz import MultiplicationQuiz

# 两位数乘法速算（包含平方和随机模式）
quiz = MultiplicationQuiz(digit_num=2, modes=["square", "random", "nearby100"])

# 指定范围练习
quiz = MultiplicationQuiz(digit_num=2, modes=["range_10_99"])

# 乘以11的速算
quiz = MultiplicationQuiz(digit_num=3, modes=["multiply11"])
```

- 关联: 继承 `QuizBase`。

---

### `DictationQuiz`

- 继承: `QuizBase`
- 说明: 单词听写测验，基于 `SymmetricMap` 双向映射出题。

- 构造函数: `__init__(self, word_map: SymmetricMap, random_mode: str = 'any')`
  - 参数:
    - `word_map` (`SymmetricMap`): 单词映射表。
    - `random_mode` (`str`): 随机出题模式，可选 `'forward'`（正向）、`'backward'`（反向）或 `'any'`（随机方向），默认 `'any'`。

- 方法:

  #### `generate_problem(self)`
  - 说明: 从 `word_map` 中通过 `random_pair(self.random_mode)` 随机选取一对配对，设置 `self.problem` 和 `self.correct_answer`。

  #### `question_text(self)`
  - 返回值: 形如 `"apple -> ?"` 的题目文本。

- 用法示例:

```python
from celestialvault.instances.inst_symmetric import SymmetricMap
from celestialvault.instances.inst_quiz import DictationQuiz

word_map = SymmetricMap.from_dict({"apple": "苹果", "banana": "香蕉", "cat": "猫"})
quiz = DictationQuiz(word_map, random_mode="any")
```

- 关联: 使用 `inst_symmetric.SymmetricMap` 作为单词映射表；继承 `QuizBase`。
