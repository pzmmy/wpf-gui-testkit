"""wpf_calculator_page.py — 计算器 Page Object"""
from wpf_testkit.core.base_page import BasePage


class CalculatorPage(BasePage):
    """WPF 计算器主界面 Page Object。"""

    BTN_0 = "Btn0"
    BTN_1 = "Btn1"
    BTN_2 = "Btn2"
    BTN_3 = "Btn3"
    BTN_4 = "Btn4"
    BTN_5 = "Btn5"
    BTN_6 = "Btn6"
    BTN_7 = "Btn7"
    BTN_8 = "Btn8"
    BTN_9 = "Btn9"
    BTN_PLUS = "BtnPlus"
    BTN_MINUS = "BtnMinus"
    BTN_MULTIPLY = "BtnMultiply"
    BTN_DIVIDE = "BtnDivide"
    BTN_EQUALS = "BtnEquals"
    BTN_CLEAR = "BtnClear"
    BTN_DECIMAL = "BtnDecimal"
    BTN_NEGATE = "BtnNegate"
    BTN_BACKSPACE = "BtnBackspace"
    DISPLAY = "DisplayText"

    @property
    def window(self):
        if self._window is None:
            self._window = self.app.window(auto_id="MainWindow")
        return self._window

    def enter_number(self, number: int):
        """输入一个数字（0-9）。"""
        btn_map = {
            0: self.BTN_0, 1: self.BTN_1, 2: self.BTN_2, 3: self.BTN_3,
            4: self.BTN_4, 5: self.BTN_5, 6: self.BTN_6, 7: self.BTN_7,
            8: self.BTN_8, 9: self.BTN_9,
        }
        btn_id = btn_map.get(number)
        if btn_id:
            self.click_element(btn_id)

    def enter_digits(self, digits: str):
        """依次输入多位数字。"""
        for ch in digits:
            if ch.isdigit():
                self.enter_number(int(ch))
            elif ch == '.':
                self.click_element(self.BTN_DECIMAL)
            elif ch == '-':
                self.click_element(self.BTN_NEGATE)

    def click_operator(self, op: str):
        """点击运算符。"""
        btn_map = {
            '+': self.BTN_PLUS,
            '-': self.BTN_MINUS,
            '*': self.BTN_MULTIPLY,
            '×': self.BTN_MULTIPLY,
            '/': self.BTN_DIVIDE,
            '÷': self.BTN_DIVIDE,
        }
        btn_id = btn_map.get(op)
        if btn_id:
            self.click_element(btn_id)

    def click_equals(self):
        """点击等号。"""
        self.click_element(self.BTN_EQUALS)

    def click_clear(self):
        """点击清除。"""
        self.click_element(self.BTN_CLEAR)

    def get_display_text(self) -> str:
        """获取显示屏文本。"""
        return self.get_text(self.DISPLAY)

    def assert_display(self, expected: str):
        """断言显示屏文本。"""
        actual = self.get_display_text()
        assert actual == expected, f"期望 '{expected}'，实际 '{actual}'"

    def compute(self, expression: str) -> str:
        """输入表达式并计算结果。

        格式: '1+2', '3*4', '10/2'
        返回: 显示屏文本
        """
        if '+' in expression:
            a, b = expression.split('+')
            self.enter_digits(a.strip())
            self.click_operator('+')
            self.enter_digits(b.strip())
        elif '-' in expression:
            a, b = expression.split('-', 1)
            self.enter_digits(a.strip())
            self.click_operator('-')
            self.enter_digits(b.strip())
        elif '*' in expression or '×' in expression:
            sep = '*' if '*' in expression else '×'
            a, b = expression.split(sep)
            self.enter_digits(a.strip())
            self.click_operator('×')
            self.enter_digits(b.strip())
        elif '/' in expression or '÷' in expression:
            sep = '/' if '/' in expression else '÷'
            a, b = expression.split(sep)
            self.enter_digits(a.strip())
            self.click_operator('÷')
            self.enter_digits(b.strip())

        self.click_equals()
        return self.get_display_text()

    def press_keys(self, keys: str):
        """通过键盘组合键输入。

        格式: '123+456=' 或 '10/2='
        """
        for ch in keys:
            if ch.isdigit():
                self.enter_number(int(ch))
            elif ch == '.':
                self.click_element(self.BTN_DECIMAL)
            elif ch in '+-*/':
                op_map = {'+': '+', '-': '-', '*': '×', '/': '÷'}
                self.click_operator(op_map[ch])
            elif ch == '=':
                self.click_equals()
            elif ch == 'C':
                self.click_clear()
