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
│   ├── wpf-calculator/        # 示例：.NET 9 WPF 计算器（14 测试用例）
│   │   ├── WpfCalculator/     # 被测应用源码（C#）
│   │   └── tests/             # GUI 测试（pytest）
│   └── wpf-contacts/          # 示例：.NET 9 WPF 通讯录（13 测试用例，覆盖多种控件）
│       ├── WpfContacts/       # 被测应用源码（C#）
│       └── tests/             # GUI 测试（pytest）
├── pyproject.toml
├── README.md
└── LICENSE
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `WPF_TEST_APP_PATH` | (必填) | 被测应用 `.exe` 的完整路径 |
| `WPF_TEST_APP_PROCESS_NAME` | `app.exe` | 被测应用进程名（用于崩溃检测和进程清理，含子进程递归杀） |
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

### `VisualDiff(diff_output_dir="screenshots/diffs")`

| 方法 | 说明 |
|------|------|
| `compare(candidate_path, baseline_path)` → `DiffResult` | 比较截图，返回包含差异统计和阈值判定的结果 |
| `update_baseline(candidate_path, baseline_path)` | 将当前截图更新为新基准 |

### `DiffResult`

| 属性 | 说明 |
|------|------|
| `diff_pct` | 差异像素百分比 (0.0 ~ 1.0) |
| `diff_count` | 差异像素数 |
| `max_diff` | 单像素最大差异 (0~255) |
| `diff_image_path` | 差异高亮图路径（红色标记差异区域） |
| `passed` | baseline 存在且尺寸匹配 |
| `within_threshold(threshold)` | 差异是否在阈值内（默认 5%） |
| `summary()` | 人类可读摘要 |

## 如何让 WPF 应用可测试

wpf-gui-testkit 依赖 UI Automation (UIA) 框架来识别控件。WPF 项目默认支持 UIA，但有几个关键点需要配合。

### AutomationId 命名规范

每个可交互控件必须设置 `AutomationProperties.AutomationId`，否则 UIA 无法精准定位：

```xaml
<!-- ✅ 正确：有明确的 AutomationId -->
<Button AutomationProperties.AutomationId="BtnLogin" Content="登录" />
<TextBox AutomationProperties.AutomationId="TxtUsername" />
<ComboBox AutomationProperties.AutomationId="ComboCity" />
<Slider AutomationProperties.AutomationId="SliderVolume" />
<CheckBox AutomationProperties.AutomationId="ChkRemember" />

<!-- ❌ 错误：UIA 只能靠文本/索引模糊查找，测试脆弱 -->
<Button Content="登录" />
<TextBox />
```

**命名惯例：**
| 控件类型 | 前缀 | 示例 |
|---------|------|------|
| Button | `Btn` | `BtnLogin`, `BtnSave`, `BtnCancel` |
| TextBox | `Txt` | `TxtUsername`, `TxtPassword` |
| ComboBox | `Combo` | `ComboCategory`, `ComboLanguage` |
| Slider | `Slider` | `SliderVolume`, `SliderBrightness` |
| CheckBox | `Chk` | `ChkRemember`, `ChkAgree` |
| RadioButton | `Radio` | `RadioMale`, `RadioFemale` |
| TextBlock | `Txt`（作为标签） | `TxtStatus`, `TxtTitle` |
| ListBox/ListView | `List` | `ListStations`, `ListResults` |
| 顶层窗口 | `Window` | `MainWindow`, `SettingsWindow` |

### 子窗口定位

如果被测应用有弹出窗口（设置、关于、对话框），这些子窗口没有主窗口的 auto_id，需要通过标题定位：

```python
# 点击打开设置
main_page.click_element("BtnSettings")
time.sleep(0.5)

# 按标题找到子窗口
settings = main_page.app.window(title="设置")
assert settings.exists(), "设置窗口未弹出"

# 操作子窗口内的控件
checkbox = settings.child_window(title="启用通知", control_type="CheckBox")
checkbox.click_input()

# 关闭子窗口
settings.close()
```

### 窗口样式与 UIA 兼容性

| 窗口属性 | 影响 | 解决方案 |
|---------|------|---------|
| `WindowStyle=None` | UIA 按标题查找可能失败 | 优先用 `auto_id` 查找窗口 |
| `AllowsTransparency=True` | UIA `InvokePattern` **无法触发** Button 的 Command 绑定 | 见下文详细说明 |
| `Topmost=True` | 覆盖层拦截 UIA 点击 | 测试前先关闭覆盖窗口 |

### Avoid Pitfalls

1. **AllowsTransparency + Command 绑定失效**
   当 `WindowStyle=None` + `AllowsTransparency=True` 时，WPF 分层窗口的路由事件系统与 UIA `InvokePattern` 交互存在 BUG。`click()`、`click_input()`、`invoke()`、`set_focus+ENTER` 均无法触发按钮的 `Command` 绑定。
   
   解决方案：在 XAML 中改用 `Click` 事件，code-behind 通过 `Dispatcher.BeginInvoke` 转发到 ViewModel：
   
   ```xaml
   <!-- ❌ 不可测试 -->
   <Button Command="{Binding OpenSettingsCommand}" />
   
   <!-- ✅ 可测试 -->
   <Button Click="OnSettingsClick" />
   ```
   
   ```csharp
   private void OnSettingsClick(object sender, RoutedEventArgs e)
   {
       Dispatcher.BeginInvoke(new Action(() =>
       {
           if (DataContext is ViewModels.MainViewModel vm)
               vm.OpenSettingsCommand.Execute(null);
       }));
   }
   ```

2. **引导页/弹出层覆盖主界面**
   如果应用首次启动有引导页（`Topmost=True`），它会覆盖主界面使点击穿透。在 `app_launch` fixture 中关闭它：
   
   ```python
   try:
       guide = app.window(auto_id="GuideView")
       if guide.exists():
           guide.close()
           time.sleep(0.5)
   except:
       pass
   ```

3. **中文编码导致窗口查找失败**
   从 WSL/CI 运行 Windows Python 时，stdout 编码默认为 GBK。中文窗口标题会乱码，需要用 UTF-8 模式：
   ```bash
   set PYTHONIOENCODING=utf-8
   pytest -v
   ```

4. **ComboBox 没有 select() 方法**
   WPF ComboBox 不支持 `select()`，用键盘操作替代：
   ```python
   combo = main_window.child_window(auto_id="ComboCity")
   combo.set_focus()
   combo.type_keys("%{DOWN}")  # Alt+↓ 展开列表
   combo.type_keys("{DOWN}")   # 选择下一项
   combo.type_keys("{ENTER}")
   ```

5. **Visibility=Collapsed 控件不可查找**
   `Visibility=Collapsed` 的控件 UIA 不暴露 auto_id。需要在同一父级下直接查找子控件，或先让控件可见。

## 视觉回归测试（L3）

wpf-gui-testkit 内置了基于 PIL 的截图比对引擎，用于捕获 UI 外观变化。

### 基本用法

```python
from wpf_testkit.utils.visual_diff import VisualDiff

def test_visual_regression(app_launch, main_window, screenshot_manager):
    # 1. 截图
    shot = screenshot_manager.capture(main_window, "main_window")

    # 2. 与 baseline 对比
    vd = VisualDiff()
    result = vd.compare(shot, "screenshots/baseline/main_window.png")

    # 3. 首次运行自动创建 baseline（不会失败）
    if result.baseline_missing:
        vd.update_baseline(shot, "screenshots/baseline/main_window.png")
        return

    # 4. 断言差异在阈值内
    assert result.within_threshold(0.05), result.summary()
```

### 生成差异高亮图

`compare()` 方法自动在 `screenshots/diffs/` 目录生成差异高亮图（红色半透明标记差异区域），方便人工审查。

### 使用场景

| 时机 | 操作 | 说明 |
|------|------|------|
| 首次运行 | 自动创建 baseline | 不失败，仅记录基准图 |
| 正常 CI | 对比 baseline | 差异 > 5% 自动失败 |
| UI 改版后 | 手动更新 baseline | 删除旧 baseline 重新跑一次即可 |

## 已知限制

- **WPF `AllowsTransparency=True` 的窗口** — UIA `InvokePattern` 可能无法触发 WPF Command 绑定。建议在 XAML 中使用 `Click` 事件处理器 + `BeginInvoke` 替代 `Command` 绑定
- **窗口 `WindowStyle=None`** — 需自定义关闭按钮和拖拽事件，UIA 查找窗口时用 `auto_id` 而非 `title`
- **中文编码** — 在命令行运行需 `set PYTHONIOENCODING=utf-8`

## 示例

### WPF 计算器

`examples/wpf-calculator/` 提供了基准测试示例：
- 被测应用：.NET 9 WPF 计算器（14 个 P0/P1/P2 分级测试用例）
- Page Object：`tests/pages/wpf_calculator_page.py`
- 测试用例：`tests/test_calculator.py`

覆盖控件类型：Button（数字/运算符）、TextBlock（显示屏）

```bash
cd examples/wpf-calculator
set WPF_TEST_APP_PATH=C:\path\to\WpfCalculator.exe
pytest -v
```

### WPF 通讯录

`examples/wpf-contacts/` 提供了高级控件测试示例：
- 被测应用：.NET 9 WPF 通讯录管理器（13 个 P0/P1/P2 分级测试用例）
- Page Object：`tests/pages/wpf_contacts_page.py`
- 测试用例：`tests/test_contacts.py`

覆盖控件类型：TextBox（搜索框+表单）、ListView+GridView（列表）、ComboBox、对话框窗口、StatusBar

```bash
cd examples/wpf-contacts
set WPF_TEST_APP_PATH=C:\path\to\WpfContacts.exe
pytest -v
```

## License

MIT
