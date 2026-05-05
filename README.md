# WPF GUI TestKit

[![PyPI](https://img.shields.io/pypi/v/wpf-gui-testkit)](https://pypi.org/project/wpf-gui-testkit/)
[![Python](https://img.shields.io/pypi/pyversions/wpf-gui-testkit)](https://pypi.org/project/wpf-gui-testkit/)
[![License](https://img.shields.io/pypi/l/wpf-gui-testkit)](LICENSE)

**通用 WPF GUI 自动化测试框架 — `pip install` 即用，零外部服务依赖。**

基于 Python + pywinauto (UIA backend) + pytest，不需要 WinAppDriver、Appium 或其他外部服务。

可选扩展：支持阿里百炼 Qwen2.5-VL 多模态大模型，通过截图分析替代脆弱的 UIA 控件枚举。

---

## 特点

- 🎯 **五级点击兜底** — `click() → click_input() → invoke() → set_focus + ENTER → Vision 坐标定位`，覆盖所有 WPF 控件模板和分层窗口
- 🛡️ **崩溃守护** — 自动检测被测应用意外退出，记录截图和日志，支持 Vision 自动分析崩溃对话框内容
- 👁️ **Vision 语义断言** — 通过多模态大模型从截图直接验证 UI 状态（弹窗是否打开、播放器是否正在播放、录音状态、错误提示检测等）
- 📸 **失败自动截图 + AI 分析** — 测试失败时自动保存截图并发送给 Vision 分析，结果写入同目录的 `_vision.txt`
- 🧹 **进程隔离** — 每条用例独立启动/清理，不留残留进程或配置
- 🔌 **零服务依赖** — 不需要 WinAppDriver、Appium、Selenium Grid 或其他外部服务
- 🔄 **多模型供应商支持** — Provider Adapter 模式，可切换阿里百炼/MiniMax/智谱/OpenAI 等任意多模态模型

## 安装

```bash
# 核心框架（零额外依赖）
pip install wpf-gui-testkit

# 包含 Vision 多模态大模型支持
pip install wpf-gui-testkit[vision]
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
│   ├── vision.py              # VisionAnalyzer + Provider Adapter（多模态大模型视觉分析）
│   ├── core/
│   │   ├── base_page.py       # Page Object 基类（五级点击兜底、等待、断言、截图、Vision 语义断言）
│   │   └── conftest.py        # pytest fixtures（app_launch, main_window, crash_daemon 等）
│   └── utils/
│       ├── crash_daemon.py    # 崩溃守护线程（每 2 秒检测进程存活 + Vision 崩溃分析）
│       ├── screenshot.py      # 截图管理器（全屏/ROI/失败截图 + Vision 自动分析 + 自动清理）
│       ├── visual_diff.py     # 视觉回归引擎（像素级 diff + Vision 语义差异过滤误报）
│       ├── uia_helpers.py     # UIA 辅助工具（控件树转储、窗口查找、Vision 控件描述增强）
│       ├── win32_dialogs.py   # Win32 系统对话框自动化（Open/Save FileDialog）
│       └── dpi_utils.py       # DPI 缩放适配
├── examples/
│   ├── wpf-calculator/        # 示例：.NET 9 WPF 计算器（14 测试用例）
│   │   ├── WpfCalculator/     # 被测应用源码（C#）
│   │   └── tests/             # GUI 测试（pytest）
│   ├── wpf-contacts/          # 示例：.NET 9 WPF 通讯录（13 测试用例，覆盖多种控件）
│   │   ├── WpfContacts/       # 被测应用源码（C#）
│   │   └── tests/             # GUI 测试（pytest）
│   └── wpf-controls/          # 示例：.NET 9 WPF 控件展示（14 测试用例）
│       ├── WpfControls/       # 被测应用源码（C#）
│       └── tests/             # GUI 测试（pytest）
├── tests/
│   └── unit/                  # 框架自测（纯逻辑，mock pywinauto，可在 WSL/CI 运行）
│       ├── test_wpf_testkit.py  # 68 测试用例：exceptions/screenshot/crash_daemon/base_page/uia_helpers/vision
│       └── test_visual_diff.py  # 12 测试用例：像素 diff + Vision 语义过滤
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
| `WPF_TEST_GUIDE_WINDOW_TITLE` | (空) | 首次启动引导页窗口标题（自动关闭用） |
| `ALIYUN_VISION_API_KEY` | (空) | Vision 多模态 API 密钥（[vision] 扩展使用） |
| `VISION_API_URL` | `https://dashscope.aliyuncs.com/...` | Vision API 端点（可切换其他供应商） |
| `VISION_MODEL` | `qwen2.5-vl-72b-instruct` | 多模态模型名称 |

## API 参考

### `BasePage(app)` — Page Object 基类

#### 等待

| 方法 | 说明 |
|------|------|
| `wait_visible(timeout=15)` | 等待窗口可见 |
| `wait_enabled(timeout=10)` | 等待窗口可用 |
| `wait_element_visible(auto_id, timeout=10)` | 等待指定控件可见 |

#### 点击操作

| 方法 | 说明 |
|------|------|
| `click_element(auto_id, timeout=10, debug=False)` | 点击控件，自动五级降级 |
| `click_input_element(auto_id, timeout=10)` | 用 `click_input` 方式点击 |
| `click_by_vision(description, timeout=10)` | **Vision 驱动**：通过描述定位无 AutomationId 的控件并点击 |
| `combo_select_by_text(auto_id, text, timeout=10)` | 从 ComboBox 中按键选择项 |

#### 输入与读取

| 方法 | 说明 |
|------|------|
| `set_text(auto_id, text)` | 文本框输入（Ctrl+A 清空后输入） |
| `get_text(auto_id)` | 获取控件文本 |
| `safe_text(ctrl)` | 安全获取控件文本，兼容 GBK 编码 |

#### 判断与断言

| 方法 | 说明 |
|------|------|
| `is_element_visible(auto_id)` | 判断控件是否可见 |
| `get_element_rectangle(auto_id)` | 获取控件矩形区域 |
| `invoke_command(command_name, command_mapping=None)` | 通过 UIA InvokePattern 触发 WPF Command |
| `assert_element_exists(auto_id)` | 断言控件存在 |
| `assert_element_text_contains(auto_id, expected)` | 断言文本包含 |

#### Vision 语义断言（需 [vision] 扩展）

| 方法 | 说明 |
|------|------|
| `vision_available` | 属性：Vision 是否可用 |
| `vision_healthy_check()` | 启动时检测 Vision API 可用性 |
| `vision_assert_dialog_open(dlg_name, timeout=10)` | 断言弹窗已打开（重试直到超时） |
| `vision_assert_playing(timeout=10)` | 断言播放器正在播放 |
| `vision_assert_recording(timeout=10)` | 断言正在录音 |
| `vision_assert_no_error()` | 断言截图中没有错误提示 |
| `vision_assert_dialog_closed(title, timeout=5)` | 断言弹窗已关闭 |
| `vision_capture_and_analyze(prompt, name, save_dir)` | 截图 + Vision 分析 + 保存（截图+分析文本） |
| `dump_controls_with_vision(fallback_on_empty=True)` | UIA 控件树 + Vision 描述（UIA 为 0 时自动启用） |

### `VisionAnalyzer` — 多模态视觉分析器

位于 `wpf_testkit/vision.py`，通过 Provider Adapter 模式支持任意多模态模型供应商。

```python
from wpf_testkit.vision import VisionAnalyzer, OpenAIVisionProvider

# 方式一：默认（阿里百炼 Qwen2.5-VL，需配置环境变量）
va = VisionAnalyzer()

# 方式二：自定义 Provider（可切换任意 OpenAI 兼容 API）
provider = OpenAIVisionProvider(
    api_url="https://api.minimaxi.com/v1/chat/completions",
    api_key="mm-xxx",
    model="minimax-vl-01",
)
va = VisionAnalyzer(provider=provider)

if va.available:
    result = va.analyze(img, "描述这张截图")
```

| 方法 | 说明 |
|------|------|
| `analyze(img, prompt, max_tokens=1024, detail="high")` | 通用截图分析 |
| `healthy_check()` | 检测 API 可用性（失败时自动禁用） |
| `find_control(img, description)` | 通过文字描述定位控件坐标 |
| `find_close_button(img)` | 定位关闭按钮坐标 |
| `compare_semantic(candidate_img, baseline_img)` | 语义比较两张截图（过滤非功能性差异） |

### `VisualDiff(diff_output_dir="screenshots/diffs")` — 视觉回归引擎

| 方法 | 说明 |
|------|------|
| `compare(candidate_path, baseline_path)` → `DiffResult` | 比较截图（像素超标时自动 Vision 语义分析） |
| `update_baseline(candidate_path, baseline_path)` | 将当前截图更新为新基准 |

### `DiffResult` — 视觉回归结果

| 属性 | 说明 |
|------|------|
| `diff_pct` | 差异像素百分比 (0.0 ~ 1.0) |
| `diff_count` | 差异像素数 |
| `max_diff` | 单像素最大差异 (0~255) |
| `diff_image_path` | 差异高亮图路径（红色标记差异区域） |
| `semantic_diff` | Vision 语义分析结果（像素超标时自动触发） |
| `semantic_acceptable` | Vision 判定为非实质性差异（如时间/滚动变化） |
| `passed` | baseline 存在且尺寸匹配 |
| `within_threshold(threshold)` | 差异是否在阈值内（默认 5%，含语义过滤） |
| `summary()` | 人类可读摘要（含 Vision 语义提示） |

### `ScreenshotManager(save_dir="screenshots")` — 截图管理器

| 方法 | 说明 |
|------|------|
| `capture(window, name)` | 截取窗口/桌面截图 |
| `capture_roi(window, name, region)` | 截取 ROI 区域 (x, y, w, h) |
| `capture_failure(window, test_name)` | 失败截图 + **自动 Vision 分析** |
| `cleanup_old(keep_days=7)` | 清理超过 N 天的截图 |

### `CrashDaemon(process_name, main_window_id, screenshot_dir)` — 崩溃守护

| 方法 | 说明 |
|------|------|
| `start()` | 启动守护线程（每 2 秒检测） |
| `stop()` | 停止守护线程 |
| `has_crashed` | 是否检测到崩溃 |
| `crash_log` | 崩溃日志文件路径 |
| `get_summary()` | 崩溃摘要（含 Vision 分析结果） |

## How to use Vision 扩展（多模态大模型）

### 配置

```bash
# 阿里百炼 API 密钥（必填）
set ALIYUN_VISION_API_KEY=sk-xxx

# 可选：切换其他供应商
set VISION_API_URL=https://api.other-provider.com/v1/chat/completions
set VISION_MODEL=other-vision-model
```

### Vision 第五级点击兜底

当 UIA 的四级降级全部失败时（典型：分层窗口 `AllowsTransparency=True`），自动启用 Vision 坐标定位：

```python
page.click_element("BtnSettings")  # 自动五级降级，无需额外代码
```

### Vision 语义断言

适合 UIA 无法获取状态的场景（如播放器按钮图标变化）：

```python
# 验证弹窗弹出（自动重试直到超时）
page.vision_assert_dialog_open("设置", timeout=10)

# 验证播放器正在播放
page.vision_assert_playing()

# 验证录音状态
page.vision_assert_recording()

# 一次性截图 + 分析 + 保存
desc = page.vision_capture_and_analyze(
    "描述这个对话框", name="about_dialog"
)
```

### 失败自动 Vision 分析

测试失败时，截图管理器自动将截图发给 Vision 分析，结果写入 `screenshots/failures/`：

```
screenshots/failures/test_login_failed_20260505_143022.png  # 原始截图
screenshots/failures/test_login_failed_20260505_143022_vision.txt  # Vision 分析
```

### 崩溃自动 Vision 分析

被测应用崩溃时，崩溃守护自动截图并分析错误对话框内容：

```
screenshots/crash_screen_20260505_143500.png              # 崩溃瞬间截图
screenshots/crash_screen_20260505_143500_vision.txt        # Vision 分析
```

### 视觉回归语义过滤

像素差异超标时自动 Vision 语义分析，过滤时钟/天气/滚动位置等非功能性误报：

```python
result = vd.compare("current.png", "baseline.png")
# 像素超标但 Vision 判定为"非实质性差异"（如时间变化），still passes
assert result.within_threshold(0.05), result.summary()
```

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
| `AllowsTransparency=True` | UIA `InvokePattern` **无法触发** Button 的 Command 绑定 | Vision 第五级点击兜底自动生效 |
| `Topmost=True` | 覆盖层拦截 UIA 点击 | 测试前先关闭覆盖窗口 |

### Avoid Pitfalls

1. **AllowsTransparency + Command 绑定失效**
   当 `WindowStyle=None` + `AllowsTransparency=True` 时，WPF 分层窗口的路由事件系统与 UIA `InvokePattern` 交互存在 BUG。`click()`、`click_input()`、`invoke()`、`set_focus+ENTER` 均无法触发按钮的 `Command` 绑定。此时 **Vision 第五级兜底自动启用**，无需修改被测应用代码。

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

wpf-gui-testkit 内置了基于 PIL 的截图比对引擎 + Vision 语义差异过滤。

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

    # 4. 断言差异在阈值内（像素超标时自动 Vision 语义过滤）
    assert result.within_threshold(0.05), result.summary()
```

### 生成差异高亮图

`compare()` 方法自动在 `screenshots/diffs/` 目录生成差异高亮图（红色半透明标记差异区域），方便人工审查。

### 使用场景

| 时机 | 操作 | 说明 |
|------|------|------|
| 首次运行 | 自动创建 baseline | 测试通过，baseline 已保存 |
| 正常运行 | 对比 baseline | 差异 > 5% 自动失败（Vision 语义过滤误报） |
| UI 改版后 | `pytest --update-baseline` | 强制更新所有 baseline |

## 已知限制

- **WPF `AllowsTransparency=True` 的窗口** — UIA `InvokePattern` 可能无法触发 WPF Command 绑定。Vision 第五级点击兜底自动处理此场景
- **窗口 `WindowStyle=None`** — 需自定义关闭按钮和拖拽事件，UIA 查找窗口时用 `auto_id` 而非 `title`
- **中文编码** — 在命令行运行需 `set PYTHONIOENCODING=utf-8`
- **视觉回归 + `pytest-xdist`** — baseline 目录不适用于并发写入。不要对 `--update-baseline` 或视觉回归测试使用 `-n auto`
- **Vision 依赖网络** — 多模态大模型需要稳定的互联网连接到 API 端点，网络问题会自动降级到传统 UIA 模式

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
