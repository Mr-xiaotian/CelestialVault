import random
import re

import ipywidgets as widgets
from IPython.display import clear_output, display

from .inst_symmetric import SymmetricMap


class QuizBase:
    """通用测验UI框架"""

    def __init__(self, title="测验", input_type="text"):
        """
        初始化测验 UI 框架。

        :param title: 测验标题。
        :param input_type: 输入类型，'text' 或 'int'。
        """
        self.title = title
        self.score = 0
        self.total_questions = 0
        self.history: list[tuple[str, int, bool]] = []

        self.generate_problem()

        # 组件
        self.question_label = widgets.Label(value=self.question_text())
        self.answer_input = (
            widgets.IntText(placeholder="输入答案")
            if input_type == "int"
            else widgets.Text(placeholder="输入答案")
        )
        self.check_button = widgets.Button(description="提交答案")
        self.next_button = widgets.Button(description="下一题", disabled=True)
        self.exit_button = widgets.Button(description="结束练习")
        self.output = widgets.Output()

        # 绑定事件
        # self.answer_input.observe(lambda change: self._on_enter(), names='value')
        self.check_button.on_click(self._check_answer)
        self.next_button.on_click(self._next_question)
        self.exit_button.on_click(self._exit_quiz)

        display(
            self.question_label,
            self.answer_input,
            self.check_button,
            self.next_button,
            self.exit_button,
            self.output,
        )

    def question_text(self) -> str:
        """
        返回当前题目的显示文本，子类必须实现。

        :return: 题目文本字符串。
        """
        raise NotImplementedError("子类必须实现此方法")

    def generate_problem(self):
        """
        生成一道新题目，子类必须实现此方法。
        """

    def _on_enter(self):
        if not self.check_button.disabled:
            self._check_answer(None)
        elif not self.next_button.disabled:
            self._next_question(None)

    def _check_answer(self, _):
        user_answer = self.answer_input.value

        is_correct = user_answer == self.correct_answer
        if is_correct:
            self.score += 1

        self.total_questions += 1
        self.history.append((self.question_text(), self.correct_answer, is_correct))

        with self.output:
            clear_output(wait=True)
            if is_correct:
                print(f"✅ 正确！答案是 {self.correct_answer}。")
            else:
                print(f"❌ 错误，正确答案是 {self.correct_answer}。")
            print(f"📊 当前得分：{self.score}/{self.total_questions}")

        self.check_button.disabled = True
        self.next_button.disabled = False

    def _next_question(self, _):
        self.output.clear_output()
        self.generate_problem()
        self.question_label.value = self.question_text()
        self.answer_input.value = (
            "" if isinstance(self.answer_input, widgets.Text) else 0
        )
        self.next_button.disabled = True
        self.check_button.disabled = False

    def _exit_quiz(self, _):
        summary = self._summary()
        with self.output:
            clear_output(wait=True)
            print(f"🎯 训练结束！正确率：{summary['accuracy']:.2f}%")
            print(f"总得分：{summary['score']}/{summary['total']}")

            table = widgets.HTML(
                """
                <table>
                    <tr><th>题目</th><th>正确答案</th><th>状态</th></tr>
                    {}
                </table>
                """.format(
                    "".join(
                        f"<tr><td>{q}</td><td>{a}</td><td>{'✅' if c else '❌'}</td></tr>"
                        for q, a, c in summary["history"]
                    )
                )
            )
            display(table)

        # 禁用控件
        for w in [
            self.answer_input,
            self.check_button,
            self.next_button,
            self.exit_button,
        ]:
            w.disabled = True

    def _summary(self):
        accuracy = (
            (self.score / self.total_questions * 100) if self.total_questions else 0
        )
        return {
            "score": self.score,
            "total": self.total_questions,
            "accuracy": accuracy,
            "history": self.history,
        }


class MultiplicationQuiz(QuizBase):
    def __init__(self, digit_num: int, modes: list[str] = None):
        """
        初始化乘法速算测验。

        :param digit_num: 乘法数字的位数。
        :param modes: 出题模式列表，如 ['square', 'random'] 等。
        """
        self.digit_num = max(1, digit_num)
        self.modes = modes or ["random"]

        super().__init__(title="乘法速算", input_type="int")

    # ---------- 出题逻辑 ----------
    def generate_problem(self):
        """根据 self.modes 中的模式列表生成一道乘法题目，设置 num1、num2 和 correct_answer。"""
        mode_funcs = {
            "square": self.generate_square,
            "square_with_5": self.generate_square_with_5,
            "varied_digit_sum_10": self.generate_varied_digit_sum_10,
            "fixed_digit_sum_10": self.generate_fixed_digit_sum_10,
            "repeated_number_9": self.generate_repeated_number_times_9,
            "random": self.generate_random_problem,
        }

        problem_list = []
        for mode in self.modes:
            if mode.startswith("multiply"):
                multiplicand = int(re.search(r"\d+", mode).group())
                problem_list.append(self.generate_multiply_num(multiplicand))
            elif mode.startswith("nearby"):
                near_num = int(re.search(r"\d+", mode).group())
                problem_list.append(self.generate_nearby(near_num))
            elif mode.startswith("square_difference"):
                end_num = int(re.search(r"\d+", mode).group())
                problem_list.append(self.generate_square_difference(end_num))
            elif mode.startswith("range_"):
                match = re.findall(r"\d+", mode)
                if len(match) == 2:
                    start, end = map(int, match)
                    problem_list.append(self.generate_range_problem(start, end))
            elif mode in mode_funcs:
                problem_list.append(mode_funcs[mode]())

        if not problem_list:
            problem_list.append(self.generate_random_problem())

        self.num1, self.num2 = random.choice(problem_list)
        self.correct_answer = self.num1 * self.num2

    def question_text(self):
        """
        返回乘法题目的显示文本。

        :return: 格式为 "num1 × num2 = ?" 的字符串。
        """
        return f"{self.num1} × {self.num2} = ?"

    # ---------- 各种生成方法 ----------
    def generate_nearby(self, near_num):
        """
        生成一个接近指定数字的乘法题目。

        :param near_num: 基准数字。
        :return: (num1, num2) 乘法题目的两个数字。
        """
        near_0 = random.choice(list(range(-9, 0)) + list(range(1, 10)))
        near_1 = random.choice(list(range(-9, 0)) + list(range(1, 10)))
        return near_num + near_0, near_num + near_1

    def generate_multiply_num(self, multiplicand):
        """
        生成一个乘数为指定数字的乘法题目。

        :param multiplicand: 指定的乘数。
        :return: (num, multiplicand) 乘法题目的两个数字。
        """
        num = random.randint(10 ** (self.digit_num - 1), 10**self.digit_num - 1)
        return num, multiplicand

    def generate_square(self):
        """
        生成一个数的平方题目。

        :return: (num, num) 同一个数字组成的乘法题目。
        """
        num = (
            random.randint(10 ** (self.digit_num - 1), 10**self.digit_num - 1)
            if self.digit_num > 1
            else random.randint(1, 9)
        )
        return num, num

    def generate_square_with_5(self):
        """
        生成一个个位数为 5 的数的平方题目。

        :return: (num, num) 个位为 5 的同一个数字组成的乘法题目。
        """
        ten_place = (
            random.randint(10 ** (self.digit_num - 2), 10 ** (self.digit_num - 1) - 1)
            if self.digit_num > 1
            else 0
        )
        num = ten_place * 10 + 5
        return num, num

    def generate_varied_digit_sum_10(self):
        """
        生成个位数相加为 10 的两个数的乘积题目。

        :return: (num1, num2) 个位数之和为 10 的两个数字。
        """
        if self.digit_num < 2:
            return self.generate_random_problem()  # 避免个位数情况

        ten_place = random.randint(
            10 ** (self.digit_num - 2), 10 ** (self.digit_num - 1) - 1
        )  # 确保不会超出位数范围
        one_place_0 = random.randint(1, 9)
        one_place_1 = 10 - one_place_0
        num1 = ten_place * 10 + one_place_0
        num2 = ten_place * 10 + one_place_1
        return num1, num2

    def generate_fixed_digit_sum_10(self):
        """
        生成十位数相加为 10、个位数相同的两个数的乘积题目。

        :return: (num1, num2) 十位之和为 10 且个位相同的两个数字。
        """
        if self.digit_num < 2:
            return self.generate_random_problem()

        ten_place0 = random.randint(1, 9)
        ten_place1 = 10 - ten_place0
        one_place = random.randint(0, 9)
        num1 = ten_place0 * 10 + one_place
        num2 = ten_place1 * 10 + one_place
        return num1, num2

    def generate_square_difference(self, end_num):
        """
        生成形如 (a+b)(a-b) 的速算乘法题目。

        :param end_num: 基准数字的个位部分。
        :return: (a+b, a-b) 乘法题目的两个数字。
        """
        base = (
            random.randint(10 ** (self.digit_num - 2), 10 ** (self.digit_num - 1)) * 10
        )  # 生成 xx0
        base += end_num

        # 生成 1-9 的随机数
        diff = random.randint(1, 9)

        # 返回 (a+b) 和 (a-b)
        return base + diff, base - diff

    def generate_repeated_number_times_9(self):
        """
        生成重复数字乘以 9 的乘法题目。

        :return: (num1, num2) 重复数字与 9 组成的乘法题目。
        """
        if self.digit_num < 2:
            return random.randint(2, 9), 9

        repeat_digit = random.randint(2, 9)  # 选择 2-9 的重复数字
        repeat_count = random.randint(
            self.digit_num, self.digit_num + 2
        )  # 重复次数为位数或位数加一

        repeat_num = int(
            str(repeat_digit) * repeat_count
        )  # 生成重复数，如 2222, 999, 66
        repeat_9 = int("9" * repeat_count)  # 重复次数乘以 9，如 999, 9999, 9
        return random.choice([[repeat_num, 9], [repeat_9, repeat_digit]])

    def generate_random_problem(self):
        """
        生成随机乘法题目。

        :return: (num1, num2) 随机生成的两个数字。
        """
        num1 = random.randint(1, 10**self.digit_num - 1)
        num2 = random.randint(1, 10**self.digit_num - 1)
        return num1, num2

    def generate_range_problem(self, start: int, end: int) -> tuple[int, int]:
        """
        生成指定范围内的随机乘法题目。

        :param start: 范围起始值。
        :param end: 范围结束值。
        :return: (num1, num2) 指定范围内随机生成的两个数字。
        """
        if start > end:
            start, end = end, start  # 自动纠正输入顺序
        num1 = random.randint(start, end)
        num2 = random.randint(start, end)
        return num1, num2


class DictationQuiz(QuizBase):
    def __init__(self, word_map: SymmetricMap, random_mode: str = "any"):
        """
        初始化单词听写测验。

        :param word_map: 单词映射表（SymmetricMap）。
        :param random_mode: 随机出题模式，可选 'forward'、'backward' 或 'any'。
        """
        self.word_map = word_map
        self.random_mode = random_mode

        super().__init__(title="单词听写", input_type="text")

    def generate_problem(self):
        """从单词映射表中随机抽取一对，设置 problem 和 correct_answer。"""
        self.problem, self.correct_answer = self.word_map.random_pair(self.random_mode)

    def question_text(self):
        """
        返回听写题目的显示文本。

        :return: 格式为 "problem -> ?" 的字符串。
        """
        return f"{self.problem} -> ?"
