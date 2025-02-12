import random
import ipywidgets as widgets
from IPython.display import display, clear_output

class MultiplicationQuiz:
    def __init__(self, digit_num, mode: list = ["random"]):
        self.digit_num = max(1, digit_num)
        self.mode = mode

        self.num1, self.num2 = self.generate_problem()
        self.score = 0
        self.total_questions = 0
        self.history = []

        # 创建 UI 组件
        self.output = widgets.Output()
        self.question_label = widgets.Label(value=f"{self.num1} × {self.num2} = ?")
        self.answer_input = widgets.IntText(placeholder="输入答案")
        self.check_button = widgets.Button(description="提交答案")
        self.next_button = widgets.Button(description="下一题", disabled=True)
        self.exit_button = widgets.Button(description="结束练习")

        # 绑定事件
        self.check_button.on_click(self.check_answer)
        self.next_button.on_click(self.next_question)
        self.exit_button.on_click(self.exit_quiz)

        # 显示组件
        display(self.question_label, self.answer_input, self.check_button, self.next_button, self.exit_button, self.output)

    def generate_problem(self):
        """根据模式生成不同的乘法题目"""
        problem_list = []
        if "square_with_5" in self.mode:
            problem_list.append(self.generate_square_with_5())
        if "varied_digit_sum_10" in self.mode:
            problem_list.append(self.generate_varied_digit_sum_10_multiplication())
        if "fixed_digit_sum_10" in self.mode:
            problem_list.append(self.generate_fixed_digit_sum_10_multiplication())
        if "random" in self.mode:
            problem_list.append(self.generate_random_problem())

        return random.choice(problem_list)
    
    def generate_square_with_5(self):
        """生成一个两位数的平方，个位数为5"""
        ten_place = random.randint(1, 10**(self.digit_num-1) - 1)
        num = ten_place * 10 + 5
        return num, num

    def generate_varied_digit_sum_10_multiplication(self):
        """生成个位数相加为10的数的乘积题目"""
        ten_place = random.randint(1, 10**(self.digit_num-1) - 1)

        tens1 = random.randint(1, 9)
        num1 = ten_place * 10 + tens1 # 例如 14, 26, 37, ...

        tens2 = 10 - tens1
        num2 = ten_place * 10 + tens2 # 例如 16, 24, 33, ...
        return num1, num2

    def generate_fixed_digit_sum_10_multiplication(self):
        """生成十位数相加为10的数的乘积题目"""
        one_place = random.randint(1, 9)

        tens1 = random.randint(1, 9)
        num1 = tens1 * 10 + one_place  # 例如14, 26, 37, ...
        
        tens2 = 10 - tens1
        num2 = tens2 * 10 + one_place  # 例如94, 86, 77, ...
        return num1, num2

    def generate_random_problem(self):
        """生成随机乘法题目"""
        num1 = random.randint(1, 10**self.digit_num - 1)
        num2 = random.randint(1, 10**self.digit_num - 1)
        return num1, num2

    def check_answer(self, _):
        """检查用户输入的答案"""
        user_answer = self.answer_input.value
        correct_answer = self.num1 * self.num2
        self.total_questions += 1
        self.check_button.disabled = True
        answer_correct = user_answer == correct_answer

        with self.output:
            clear_output(wait=True)
            if answer_correct:
                print(f"✅ 正确！答案是 {correct_answer}")
                self.score += 1
                self.next_button.disabled = False 
            else:
                print(f"❌ 错误，正确答案是 {correct_answer}。")
                self.next_button.disabled = False  
            print(f"📊 当前得分：{self.score}/{self.total_questions}")

        self.history.append((self.question_label.value, correct_answer, answer_correct))

    def next_question(self, _):
        """生成新的题目"""
        self.output.clear_output()

        self.num1, self.num2 = self.generate_problem()
        self.question_label.value = f"{self.num1} × {self.num2} = ?"
        self.answer_input.value = 0
        self.next_button.disabled = True
        self.check_button.disabled = False

        with self.output:
            clear_output(wait=True)

    def exit_quiz(self, _):
        """结束练习"""
        if self.total_questions > 0:
            accuracy = (self.score / self.total_questions) * 100
        else:
            accuracy = 0
        with self.output:
            clear_output(wait=True)
            print(f"🎯 训练结束！\n最终得分：{self.score}/{self.total_questions}（正确率：{accuracy:.2f}%）")
            print("历史记录：", self.history)
        self.question_label.value = "日积跬步 × 日行不缀 = ?"
        self.answer_input.disabled = True
        self.check_button.disabled = True
        self.next_button.disabled = True
        self.exit_button.disabled = True

