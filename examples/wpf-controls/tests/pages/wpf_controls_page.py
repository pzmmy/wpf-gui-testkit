"""wpf_controls_page.py — WPF Controls Demo Page Object

涵盖控件类型：ToggleButton, RadioButton, Slider, Expander,
DatePicker, ProgressBar, ToolBar, GroupBox, ComboBox, CheckBox.
"""
import time
from wpf_testkit.core.base_page import BasePage


class ControlsPage(BasePage):
    """WPF 控件演示主界面 Page Object。"""

    # ── 主窗口 ──
    WINDOW = "MainWindow"

    # ── ToggleButton ──
    TOGGLE_WIFI = "ToggleWiFi"
    TOGGLE_BLUETOOTH = "ToggleBluetooth"
    TOGGLE_AIRPLANE = "ToggleAirplane"
    TXT_TOGGLE_STATUS = "TxtToggleStatus"

    # ── RadioButton ──
    RADIO_LIGHT = "RadioLight"
    RADIO_DARK = "RadioDark"
    RADIO_SYSTEM = "RadioSystem"
    TXT_RADIO_STATUS = "TxtRadioStatus"

    # ── Slider ──
    SLIDER_VOLUME = "SliderVolume"
    TXT_SLIDER_VALUE = "TxtSliderValue"

    # ── Expander ──
    EXPANDER_ADVANCED = "ExpanderAdvanced"
    CHK_AUTO_UPDATE = "ChkAutoUpdate"
    CHK_USAGE_DATA = "ChkUsageData"
    TXT_EXPANDER_STATUS = "TxtExpanderStatus"

    # ── DatePicker ──
    DATE_PICKER_START = "DatePickerStart"
    TXT_DATE_STATUS = "TxtDateStatus"

    # ── ProgressBar ──
    PROGRESS_BAR = "ProgressBarDemo"
    BTN_PROGRESS_START = "BtnProgressStart"
    BTN_PROGRESS_RESET = "BtnProgressReset"
    TXT_PROGRESS_STATUS = "TxtProgressStatus"

    # ── ToolBar ──
    TOOLBAR_MAIN = "ToolBarMain"
    BTN_TOOL_NEW = "BtnToolNew"
    BTN_TOOL_SAVE = "BtnToolSave"
    BTN_TOOL_DELETE = "BtnToolDelete"

    # ── GroupBox ──
    GROUP_BOX_PREFS = "GroupBoxPrefs"
    CHK_NOTIFY = "ChkNotify"
    COMBO_LANGUAGE = "ComboLanguage"
    TXT_GROUPBOX_STATUS = "TxtGroupBoxStatus"

    def __init__(self, app):
        super().__init__(app)
        self._window = self.app.window(auto_id=self.WINDOW)

    @property
    def window(self):
        return self._window

    # ── 帮助方法 ──

    @staticmethod
    def wait_short(seconds: float = 0.3):
        """等待 UI 渲染完成。"""
        time.sleep(seconds)

    # ════════════════════════════════════════════
    # ToggleButton
    # ════════════════════════════════════════════

    def toggle_wifi(self):
        """点击 Wi-Fi ToggleButton。"""
        self.click_element(self.TOGGLE_WIFI)

    def toggle_bluetooth(self):
        """点击 Bluetooth ToggleButton。"""
        self.click_element(self.TOGGLE_BLUETOOTH)

    def get_toggle_status(self) -> str:
        """获取 ToggleButton 状态文本。"""
        return self.get_text(self.TXT_TOGGLE_STATUS)

    # ════════════════════════════════════════════
    # RadioButton
    # ════════════════════════════════════════════

    def select_theme(self, theme: str):
        """选择主题（Light/Dark/System）。"""
        btn_map = {
            "Light": self.RADIO_LIGHT,
            "Dark": self.RADIO_DARK,
            "System": self.RADIO_SYSTEM,
        }
        btn_id = btn_map.get(theme)
        if btn_id:
            self.click_element(btn_id)

    def get_radio_status(self) -> str:
        """获取 RadioButton 状态文本。"""
        return self.get_text(self.TXT_RADIO_STATUS)

    # ════════════════════════════════════════════
    # Slider
    # ════════════════════════════════════════════

    def get_slider_value(self) -> int:
        """获取 Slider 当前值。"""
        text = self.get_text(self.TXT_SLIDER_VALUE)
        try:
            return int(text)
        except (ValueError, TypeError):
            return -1

    # ════════════════════════════════════════════
    # Expander
    # ════════════════════════════════════════════

    def toggle_expander(self):
        """展开/折叠 Expander。"""
        self.click_element(self.EXPANDER_ADVANCED)

    def get_expander_status(self) -> str:
        """获取 Expander 状态文本。"""
        return self.get_text(self.TXT_EXPANDER_STATUS)

    def wait_expander_state(self, expected_state: str, timeout: float = 5.0):
        """轮询等待 Expander 到达指定状态（Expanded/Collapsed）。"""
        deadline = time.time() + timeout
        while time.time() < deadline:
            status = self.get_expander_status()
            if expected_state in status:
                return True
            time.sleep(0.2)
        return False

    # ════════════════════════════════════════════
    # DatePicker
    # ════════════════════════════════════════════

    def get_date_status(self) -> str:
        """获取 DatePicker 状态文本。"""
        return self.get_text(self.TXT_DATE_STATUS)

    def select_date(self, date_str: str):
        """通过键盘输入选中日期（格式 yyyy-MM-dd）。"""
        ctrl = self.window.child_window(auto_id=self.DATE_PICKER_START)
        ctrl.set_focus()
        ctrl.type_keys("^{HOME}")  # Ctrl+Home 选中全部
        self.wait_short(0.1)
        ctrl.type_keys(date_str)
        self.wait_short(0.1)
        ctrl.type_keys("{ENTER}")

    # ════════════════════════════════════════════
    # ProgressBar
    # ════════════════════════════════════════════

    def click_progress_start(self):
        """点击 ProgressBar Start 按钮。"""
        self.click_element(self.BTN_PROGRESS_START)

    def click_progress_reset(self):
        """点击 ProgressBar Reset 按钮。"""
        self.click_element(self.BTN_PROGRESS_RESET)

    def get_progress_status(self) -> str:
        """获取 ProgressBar 状态文本。"""
        return self.get_text(self.TXT_PROGRESS_STATUS)
