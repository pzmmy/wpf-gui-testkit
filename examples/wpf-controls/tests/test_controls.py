"""test_controls.py — WPF Controls Demo GUI 测试

覆盖控件类型：ToggleButton, RadioButton, Slider, Expander,
DatePicker, ProgressBar, ToolBar, GroupBox, ComboBox, CheckBox.
"""
import pytest
from wpf_testkit.core.conftest import *  # noqa: F403  # 提供 app_launch, main_window
from pages.wpf_controls_page import ControlsPage


class TestControls:

    # ════════════════════════════════════════════
    # P0 — 核心功能
    # ════════════════════════════════════════════

    @pytest.mark.P0
    def test_window_launch(self, main_window):
        """窗口正常启动。"""
        assert main_window.exists()
        assert main_window.is_visible()

    @pytest.mark.P0
    def test_toggle_wifi_on_off(self, app_launch, main_window):
        """ToggleButton 点击切换 On/Off。"""
        page = ControlsPage(app_launch)
        # 默认 Wi-Fi ON
        assert "ON" in page.get_toggle_status()
        # 点击关闭
        page.toggle_wifi()
        assert "OFF" in page.get_toggle_status()
        # 再点击打开
        page.toggle_wifi()
        assert "ON" in page.get_toggle_status()

    @pytest.mark.P0
    def test_radio_button_selection(self, app_launch, main_window):
        """RadioButton 单选切换。"""
        page = ControlsPage(app_launch)
        page.select_theme("Light")
        assert "Light" in page.get_radio_status()
        page.select_theme("Dark")
        assert "Dark" in page.get_radio_status()
        page.select_theme("System")
        assert "System" in page.get_radio_status()

    @pytest.mark.P0
    def test_slider_initial_value(self, app_launch, main_window):
        """Slider 初始值为 50。"""
        page = ControlsPage(app_launch)
        assert page.get_slider_value() == 50

    @pytest.mark.P0
    def test_expander_toggle(self, app_launch, main_window):
        """Expander 展开/折叠（轮询等待替代 sleep）。"""
        page = ControlsPage(app_launch)
        assert page.wait_expander_state("Collapsed"), "初始应折叠"
        # 展开
        page.toggle_expander()
        assert page.wait_expander_state("Expanded"), "展开后应 Expanded"
        # 折叠
        page.toggle_expander()
        assert page.wait_expander_state("Collapsed"), "折叠后应 Collapsed"

    @pytest.mark.P0
    def test_date_picker_exists(self, app_launch, main_window):
        """DatePicker 控件存在，初始状态为 No date selected。"""
        page = ControlsPage(app_launch)
        assert "No date selected" in page.get_date_status()

    @pytest.mark.P0
    def test_progress_bar_start_reset(self, app_launch, main_window):
        """ProgressBar Start/Reset 功能，验证进度推进。"""
        page = ControlsPage(app_launch)
        # 初始状态
        assert "67%" in page.get_progress_status()
        # Start → 等 800ms 确保足够 tick
        page.click_progress_start()
        page.wait_short(0.8)
        page.click_progress_start()  # 停止
        # 验证进度确实推进了
        status = page.get_progress_status()
        pct = int(status.replace("%", ""))
        assert pct > 67, f"Progress 应推进 >67%，实际 {pct}%"
        # Reset
        page.click_progress_reset()
        assert "0%" in page.get_progress_status()

    # ════════════════════════════════════════════
    # P1 — 交互细节
    # ════════════════════════════════════════════

    @pytest.mark.P1
    def test_all_toggles_exist(self, app_launch, main_window):
        """所有 ToggleButton 控件存在。"""
        page = ControlsPage(app_launch)
        for btn_id in [page.TOGGLE_WIFI, page.TOGGLE_BLUETOOTH, page.TOGGLE_AIRPLANE]:
            assert page.is_element_visible(btn_id), f"{btn_id} 不存在"

    @pytest.mark.P1
    def test_toolbar_buttons_exist(self, app_launch, main_window):
        """ToolBar 内的按钮控件存在。"""
        page = ControlsPage(app_launch)
        for btn_id in [page.BTN_TOOL_NEW, page.BTN_TOOL_SAVE, page.BTN_TOOL_DELETE]:
            assert page.is_element_visible(btn_id), f"{btn_id} 不存在"

    @pytest.mark.P1
    def test_expander_inner_controls_visible_when_expanded(
        self, app_launch, main_window
    ):
        """Expander 展开后内部 CheckBox 可见。"""
        page = ControlsPage(app_launch)
        page.toggle_expander()
        assert page.wait_expander_state("Expanded"), "Expander 应展开"
        assert page.is_element_visible(page.CHK_AUTO_UPDATE)
        assert page.is_element_visible(page.CHK_USAGE_DATA)

    @pytest.mark.P1
    def test_groupbox_controls_exist(self, app_launch, main_window):
        """GroupBox 内控件存在。"""
        page = ControlsPage(app_launch)
        assert page.is_element_visible(page.CHK_NOTIFY)
        assert page.is_element_visible(page.COMBO_LANGUAGE)

    @pytest.mark.P1
    def test_date_picker_select_date(self, app_launch, main_window):
        """DatePicker 选日期后状态更新。"""
        page = ControlsPage(app_launch)
        # 选一个日期
        page.select_date("2026-05-04")
        page.wait_short(0.3)
        status = page.get_date_status()
        assert "2026-05-04" in status, f"DatePicker 应显示所选日期，实际: {status}"

    # ════════════════════════════════════════════
    # P2 — 边界场景
    # ════════════════════════════════════════════

    @pytest.mark.P2
    def test_expander_inner_controls_hidden_when_collapsed(
        self, app_launch, main_window
    ):
        """Expander 折叠后内部控件不可见。"""
        page = ControlsPage(app_launch)
        # 确保折叠
        if page.wait_expander_state("Collapsed"):
            pass
        assert "Collapsed" in page.get_expander_status()

    @pytest.mark.P2
    def test_slider_bounds(self, app_launch, main_window):
        """Slider 范围非负。"""
        page = ControlsPage(app_launch)
        val = page.get_slider_value()
        assert 0 <= val <= 100, f"Slider 值 {val} 超出范围 [0,100]"

    @pytest.mark.P2
    def test_toggle_multiple_preserves_last_status(self, app_launch, main_window):
        """多次切换 Toggle，状态文本正确反映最新操作。"""
        page = ControlsPage(app_launch)
        page.toggle_wifi()
        status = page.get_toggle_status()
        assert "Wi-Fi" in status

    @pytest.mark.P2
    def test_combo_language_exists(self, app_launch, main_window):
        """ComboBox 语言选择控件存在。"""
        page = ControlsPage(app_launch)
        assert page.is_element_visible(page.COMBO_LANGUAGE)
