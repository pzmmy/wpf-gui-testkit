"""test_calculator.py — WPF 计算器 GUI 测试

覆盖：
- 基本运算：加减乘除
- 连续运算
- 清空/小数点/取反
- UI 验证
"""
import pytest
from wpf_testkit.core.conftest import *  # noqa: F403  # 提供 app_launch, main_window
from pages.wpf_calculator_page import CalculatorPage


class TestCalculator:

    # ================================================================
    #  基础功能
    # ================================================================

    @pytest.mark.P0
    def test_app_launch(self, main_window):
        """计算器窗口正常启动。"""
        assert main_window.exists(), "主窗口未出现"
        assert main_window.is_visible(), "主窗口不可见"

    @pytest.mark.P0
    def test_display_initially_zero(self, app_launch, main_window):
        """启动后显示屏显示 0。"""
        page = CalculatorPage(app_launch)
        page.assert_display("0")

    @pytest.mark.P0
    def test_addition(self, app_launch, main_window):
        """1 + 2 = 3"""
        page = CalculatorPage(app_launch)
        result = page.compute("1+2")
        assert result == "3", f"1+2 结果应为 3，实际 {result}"

    @pytest.mark.P1
    def test_subtraction(self, app_launch, main_window):
        """5 - 3 = 2"""
        page = CalculatorPage(app_launch)
        result = page.compute("5-3")
        assert result == "2", f"5-3 结果应为 2，实际 {result}"

    @pytest.mark.P1
    def test_multiplication(self, app_launch, main_window):
        """4 × 5 = 20"""
        page = CalculatorPage(app_launch)
        result = page.compute("4×5")
        assert result == "20", f"4×5 结果应为 20，实际 {result}"

    @pytest.mark.P1
    def test_division(self, app_launch, main_window):
        """10 ÷ 2 = 5"""
        page = CalculatorPage(app_launch)
        result = page.compute("10÷2")
        assert result == "5", f"10÷2 结果应为 5，实际 {result}"

    # ================================================================
    #  连续运算
    # ================================================================

    @pytest.mark.P1
    def test_chain_calculation(self, app_launch, main_window):
        """3 + 4 - 2 = 5"""
        page = CalculatorPage(app_launch)
        page.enter_digits("3")
        page.click_operator("+")
        page.enter_digits("4")
        page.click_operator("-")
        page.enter_digits("2")
        page.click_equals()
        page.assert_display("5")

    # ================================================================
    #  清空功能
    # ================================================================

    @pytest.mark.P1
    def test_clear(self, app_launch, main_window):
        """输入后清除返回 0。"""
        page = CalculatorPage(app_launch)
        page.enter_digits("123")
        page.click_clear()
        page.assert_display("0")

    # ================================================================
    #  小数点
    # ================================================================

    @pytest.mark.P1
    def test_decimal(self, app_launch, main_window):
        """3.5 + 1.5 = 5"""
        page = CalculatorPage(app_launch)
        page.enter_digits("3.5")
        page.click_operator("+")
        page.enter_digits("1.5")
        page.click_equals()
        page.assert_display("5")

    # ================================================================
    #  按钮存在性
    # ================================================================

    @pytest.mark.P0
    def test_all_buttons_exist(self, app_launch, main_window):
        """所有按钮控件都存在。"""
        page = CalculatorPage(app_launch)
        all_buttons = [
            page.BTN_0, page.BTN_1, page.BTN_2, page.BTN_3, page.BTN_4,
            page.BTN_5, page.BTN_6, page.BTN_7, page.BTN_8, page.BTN_9,
            page.BTN_PLUS, page.BTN_MINUS, page.BTN_MULTIPLY, page.BTN_DIVIDE,
            page.BTN_EQUALS, page.BTN_CLEAR, page.BTN_DECIMAL,
        ]
        for btn_id in all_buttons:
            assert page.is_element_visible(btn_id), f"按钮 {btn_id} 不存在"

    # ================================================================
    #  键盘输入
    # ================================================================

    @pytest.mark.P2
    def test_divide_by_zero(self, app_launch, main_window):
        """除零显示错误。"""
        page = CalculatorPage(app_launch)
        result = page.compute("5÷0")
        assert result in ("错误", "∞", "NaN"), f"除零结果应为错误，实际 {result}"

    # ================================================================
    #  取反
    # ================================================================

    @pytest.mark.P2
    def test_negate(self, app_launch, main_window):
        """5 → ± → -5 → ± → 5"""
        page = CalculatorPage(app_launch)
        page.enter_digits("5")
        page.click_element(page.BTN_NEGATE)
        page.assert_display("-5")
        page.click_element(page.BTN_NEGATE)
        page.assert_display("5")

    # ================================================================
    #  键盘输入
    # ================================================================

    @pytest.mark.P1
    def test_keyboard_input(self, app_launch, main_window):
        """通过 press_keys 输入 123+456= 结果应为 579"""
        page = CalculatorPage(app_launch)
        result = page.press_keys("123+456=")
        assert result == "579", f"键盘输入 123+456= 结果应为 579，实际 {result}"

    @pytest.mark.P2
    def test_keyboard_decimal(self, app_launch, main_window):
        """键盘输入 3.5+1.5= 结果应为 5"""
        page = CalculatorPage(app_launch)
        result = page.press_keys("3.5+1.5=")
        assert result == "5", f"3.5+1.5= 结果应为 5，实际 {result}"
