# instances/inst_quiz.py

## 源文件
- `src/celestialvault/instances/inst_quiz.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- `import random`
- `import re`
- `import ipywidgets as widgets`
- `from IPython.display import clear_output, display`
- `from .inst_symmetric import SymmetricMap`

## 模块常量
- 无

## 顶层函数
- 无

## 类
### `QuizBase`
- 继承: `object`
- 说明: 通用测验UI框架
- 方法:
  - `def __init__(self, title = '测验', input_type = 'text')`
  - `def question_text(self) -> str`
  - `def generate_problem(self)`
  - `def _on_enter(self)`
  - `def _check_answer(self, _)`
  - `def _next_question(self, _)`
  - `def _exit_quiz(self, _)`
  - `def _summary(self)`

### `MultiplicationQuiz`
- 继承: `QuizBase`
- 说明: 无模块级文档字符串。
- 方法:
  - `def __init__(self, digit_num: int, modes: list[str] = None)`
  - `def generate_problem(self)`
  - `def question_text(self)`
  - `def generate_nearby(self, near_num)`
  - `def generate_multiply_num(self, multiplicand)`
  - `def generate_square(self)`
  - `def generate_square_with_5(self)`
  - `def generate_varied_digit_sum_10(self)`
  - `def generate_fixed_digit_sum_10(self)`
  - `def generate_square_difference(self, end_num)`
  - `def generate_repeated_number_times_9(self)`
  - `def generate_random_problem(self)`
  - `def generate_range_problem(self, start: int, end: int) -> tuple[int, int]`

### `DictationQuiz`
- 继承: `QuizBase`
- 说明: 无模块级文档字符串。
- 方法:
  - `def __init__(self, word_map: SymmetricMap, random_mode: str = 'any')`
  - `def generate_problem(self)`
  - `def question_text(self)`
