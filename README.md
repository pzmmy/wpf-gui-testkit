# WPF GUI TestKit

[![PyPI](https://img.shields.io/pypi/v/wpf-gui-testkit)](https://pypi.org/project/wpf-gui-testkit/)
[![Python](https://img.shields.io/pypi/pyversions/wpf-gui-testkit)](https://pypi.org/project/wpf-gui-testkit/)
[![License](https://img.shields.io/pypi/l/wpf-gui-testkit)](LICENSE)

**通用 WPF GUI 自动化测试框架 — `pip install` 即用，零外部服务依赖。**

基于 Python + pywinauto (UIA backend) + pytest，不需要 WinAppDriver、Appium 或其他外部服务。

---

## 特点

- 🎯 **四级点击兜底** — `click() → click_input() → invoke() → set_focus + ENTER`，覆盖所有 WPF 控件模板（Button/RadioButton/ToggleButton/ListBoxItem 等）
- 🛡️ **崩溃守护** — 自动检测被测应用意外退出，记录截图和日志
- 📸 **失败自动截图** — 测试失败时自动保存桌面截图
- 🧹 **进程隔离** — 每条用例独立启动/清理，不留残留进程或配置
- 🔌 **零服务依赖** — 不需要 WinAppDriver、Appium、Selenium Grid 或其他外部服务

## 安装

```bash
pip install wpf-gui-testkit
```

## 快速开始

### 1. 创建 Page Object `main_page.py`

```python
from wpf_testkit.core.base_page import BasePage


class LoginPage(BasePage):
    """用户登录窗口 Page Object（示例）。"""

    @property
    def window(self):
        if self._window is None:
            self._window = self.app.window(auto_id="MainWindow")
        return self._window

    def enter_username(self, text: str):
        self.set_text("TxtUsername", text)

    def enter_password(self, text: str):
        self.set_text("TxtPassword", text)

    def click_login(self):
        self.click_element("BtnLogin")

    def get_status_text(self) -> str:
        return self.get_text("TxtStatus")
```

### 2. 创建测试文件 `test_login.py`

```python
import pytest
from main_page import LoginPage


class TestLogin:
    def test_window_launch(self, main_window):
        """验证主窗口启动后可见。"""
        assert main_window.exists()
        assert main_window.is_visible()

    def test_login_form(self, app_launch, main_window):
        """验证表单交互：输入凭据 → 点击登录 → 检查状态。"""
        page = LoginPage(app_launch)
        page.enter_username("admin")
        page.enter_password("123456")
        page.click_login()
        page.wait_element_visible("TxtStatus", timeout=5)
        assert "成功" in page.get_status_text()
```

### 3. 配置环境变量

```bash
# 被测应用路径（必填）
set WPF_TEST_APP_PATH=C:\path\to\YourWpfApp.exe

# 被测应用进程名（用于崩溃检测和进程清理）
set WPF_TEST_APP_PROCESS_NAME=YourWpfApp.exe

# 主窗口 AutomationProperties.AutomationId
set WPF_TEST_MAIN_WINDOW_ID=MainWindow

# %APPDATA% 下的应用数据目录名（可选，用于测试间清理残留配置）
set WPF_TEST_APP_DATA_DIR=YourWpfApp
```

### 4. 运行测试

```bash
pytest test_login.py -v
```

---

## 项目结构

```
wpf-gui-testkit/
├── wpf_testkit/
│   ├── __init__.py            # 版本号
│   ├── exceptions.py          # 自定义异常（ElementNotFound, CommandInvoke, CrashDetected）
│   ├── core/
│   │   ├── base_page.py       # Page Object 基类（四级点击兜底、等待、断言、截图）
│   │   └── conftest.py        # pytest fixtures（app_launch, main_window, crash_daemon 等）
│   └── utils/
│       ├── crash_daemon.py    # 崩溃守护线程（每 2 秒检测进程存活）
│       ├── screenshot.py      # 截图管理器（全屏/ROI/失败截图 + 自动清理）
│       ├── uia_helpers.py     # UIA 辅助工具（控件树转储、窗口查找）
│       └── dpi_utils.py       # DPI 缩放适配
├── examples/
│   └── wpf-calculator/        # 示例：.NET 8 WPF 计算器（14 测试用例）
│       ├── WpfCalculator/     # 被测应用源码（C#）
│       └── tests/             # GUI 测试（pytest）
├── pyproject.toml
├── README.md
└── LICENSE
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `WPF_TEST_APP_PATH` | (必填) | 被测应用 `.exe` 的完整路径 |
| `WPF_TEST_APP_PROCESS_NAME` | `app.exe` | 被测应用进程名（用于崩溃检测和进程清理） |
| `WPF_TEST_APP_DATA_DIR` | (空) | `%APPDATA%` 下的应用数据目录名（测试间清理用） |
| `WPF_TEST_MAIN_WINDOW_ID` | `MainWindow` | 主窗口 `AutomationProperties.AutomationId` |

## API 参考

### `BasePage(app)`

| 方法 | 说明 |
|------|------|
| `wait_visible(timeout=15)` | 等待窗口可见 |
| `wait_enabled(timeout=10)` | 等待窗口可用 |
| `wait_element_visible(auto_id, timeout=10)` | 等待指定控件可见 |
| `click_element(auto_id, timeout=10)` | 点击控件，自动四级降级 |
| `click_input_element(auto_id, timeout=10)` | 用 `click_input` 方式点击 |
| `set_text(auto_id, text, timeout=10)` | 文本框输入 |
| `get_text(auto_id)` | 获取控件文本 |
| `is_element_visible(auto_id)` | 判断控件是否可见 |
| `get_element_rectangle(auto_id)` | 获取控件矩形区域 |
| `invoke_command(command_name, command_mapping=None)` | 通过 UIA InvokePattern 触发 WPF Command |
| `screenshot(name, save_dir)` | 保存窗口截图 |
| `assert_element_exists(auto_id)` | 断言控件存在 |
| `assert_element_text_contains(auto_id, expected)` | 断言文本包含 |

## 已知限制

- **WPF `AllowsTransparency=True` 的窗口** — UIA `InvokePattern` 可能无法触发 WPF Command 绑定。建议在 XAML 中使用 `Click` 事件处理器 + `BeginInvoke` 替代 `Command` 绑定
- **窗口 `WindowStyle=None`** — 需自定义关闭按钮和拖拽事件，UIA 查找窗口时用 `auto_id` 而非 `title`
- **中文编码** — 在命令行运行需 `set PYTHONIOENCODING=utf-8`

## 示例：WPF 计算器

`examples/wpf-calculator/` 提供了完整的实战示例：
- 被测应用：.NET 8 WPF 计算器（14 个 P0/P1/P2 分级测试用例）
- Page Object：`tests/pages/wpf_calculator_page.py`
- 测试用例：`tests/test_calculator.py`

```bash
cd examples/wpf-calculator
set WPF_TEST_APP_PATH=C:\path\to\WpfCalculator.exe
pytest -v
```

## License

MIT
