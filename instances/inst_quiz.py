import random
import ipywidgets as widgets
from IPython.display import display, clear_output

class MultiplicationQuiz:
    def __init__(self, n, m):
        self.n = max(1, n)  # 处理 n=0 的情况
        self.m = max(1, m)  # 处理 m=0 的情况
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
        """生成新的乘法题目"""
        num1 = random.randint(10**(self.n-1), 10**self.n - 1)
        num2 = random.randint(10**(self.m-1), 10**self.m - 1)
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

