# WPF GUI TestKit

[![PyPI](https://img.shields.io/pypi/v/wpf-gui-testkit)](https://pypi.org/project/wpf-gui-testkit/)
[![Python](https://img.shields.io/pypi/pyversions/wpf-gui-testkit)](https://pypi.org/project/wpf-gui-testkit/)
[![License](https://img.shields.io/pypi/l/wpf-gui-testkit)](LICENSE)

**A lightweight WPF GUI automation testing framework — `pip install` ready, zero external service dependencies.**

> [中文版](README.md)

Built on Python + pywinauto (UIA backend) + pytest. No WinAppDriver, Appium, or any other external services required.

---

## Features

- 🎯 **4-level click fallback** — `click() → click_input() → invoke() → set_focus + ENTER`, works across all WPF control templates
- 🛡️ **Crash daemon** — Automatically detects unexpected app exit, records screenshots and logs
- 📸 **Auto screenshot on failure** — Saves desktop screenshot when a test fails
- 🧹 **Process isolation** — Each test case starts/cleans up independently, no leftover processes
- 🔌 **Zero service dependencies** — No WinAppDriver, Appium, Selenium Grid, or other external services

## Install

```bash
pip install wpf-gui-testkit
```

## Quick Start

### 1. Create a Page Object `main_page.py`

```python
from wpf_testkit.core.base_page import BasePage


class LoginPage(BasePage):
    """Login window Page Object (example)."""

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

### 2. Create a test file `test_login.py`

```python
import pytest
from main_page import LoginPage


class TestLogin:
    def test_window_launch(self, main_window):
        """Verify main window appears after launch."""
        assert main_window.exists()
        assert main_window.is_visible()

    def test_login_form(self, app_launch, main_window):
        """Verify form interaction: enter credentials → click login → check status."""
        page = LoginPage(app_launch)
        page.enter_username("admin")
        page.enter_password("123456")
        page.click_login()
        page.wait_element_visible("TxtStatus", timeout=5)
        assert "OK" in page.get_status_text()
```

### 3. Configure environment variables

```bash
# Path to the app under test (required)
set WPF_TEST_APP_PATH=C:\path\to\YourWpfApp.exe

# Process name of the app under test (used for crash detection & cleanup)
set WPF_TEST_APP_PROCESS_NAME=YourWpfApp.exe

# AutomationProperties.AutomationId of the main window
set WPF_TEST_MAIN_WINDOW_ID=MainWindow

# App data directory name under %%APPDATA%% (optional, clean up between runs)
set WPF_TEST_APP_DATA_DIR=YourWpfApp
```

### 4. Run tests

```bash
pytest test_login.py -v
```

---

## Project Structure

```
wpf-gui-testkit/
├── wpf_testkit/
│   ├── __init__.py            # Version
│   ├── exceptions.py          # Custom exceptions
│   ├── core/
│   │   ├── base_page.py       # Page Object base class
│   │   └── conftest.py        # pytest fixtures
│   └── utils/
│       ├── crash_daemon.py    # Crash monitor thread
│       ├── screenshot.py      # Screenshot manager
│       ├── uia_helpers.py     # UIA helper tools
│       └── dpi_utils.py       # DPI scaling
├── examples/
│   ├── wpf-calculator/        # Calculator demo (14 tests)
│   ├── wpf-contacts/          # Contacts manager demo (13 tests)
│   └── wpf-controls/          # Controls showcase demo (14 tests)
├── pyproject.toml
├── README.md
├── README.en.md
└── LICENSE
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WPF_TEST_APP_PATH` | (required) | Full path to the `.exe` under test |
| `WPF_TEST_APP_PROCESS_NAME` | `app.exe` | Process name (crash detection & cleanup, recursive child-kill) |
| `WPF_TEST_APP_DATA_DIR` | (empty) | App data dir name under `%APPDATA%` (cleanup between runs) |
| `WPF_TEST_MAIN_WINDOW_ID` | `MainWindow` | `AutomationProperties.AutomationId` of the main window |
| `WPF_TEST_GUIDE_WINDOW_TITLE` | (empty) | Title of the first-launch guide window to auto-close |

## API Reference

### `BasePage(app)`

| Method | Description |
|--------|-------------|
| `wait_visible(timeout=15)` | Wait until window is visible |
| `wait_enabled(timeout=10)` | Wait until window is enabled |
| `wait_element_visible(auto_id, timeout=10)` | Wait for a specific control to be visible |
| `click_element(auto_id, timeout=10)` | Click a control with 4-level fallback |
| `click_input_element(auto_id, timeout=10)` | Click using `click_input` method |
| `set_text(auto_id, text, timeout=10)` | Type text into a text box |
| `get_text(auto_id)` | Get text content of a control |
| `is_element_visible(auto_id)` | Check if a control is visible |
| `get_element_rectangle(auto_id)` | Get bounding rectangle of a control |
| `invoke_command(command_name, command_mapping=None)` | Trigger a WPF Command via UIA InvokePattern |
| `screenshot(name, save_dir)` | Save a screenshot of the window |
| `assert_element_exists(auto_id)` | Assert a control exists and is visible |
| `assert_element_text_contains(auto_id, expected)` | Assert control text contains expected string |

### `VisualDiff(diff_output_dir="screenshots/diffs")`

| Method | Description |
|--------|-------------|
| `compare(candidate_path, baseline_path)` → `DiffResult` | Compare two screenshots, returns stats & threshold check |
| `update_baseline(candidate_path, baseline_path)` | Promote current screenshot as new baseline |

### `DiffResult`

| Property | Description |
|----------|-------------|
| `diff_pct` | Percentage of differing pixels (0.0 ~ 1.0) |
| `diff_count` | Number of differing pixels |
| `max_diff` | Maximum single-pixel difference (0~255) |
| `diff_image_path` | Path to the diff highlight image (red overlay) |
| `passed` | Baseline exists and dimensions match |
| `within_threshold(threshold)` | Whether diff is within threshold (default 5%) |
| `summary()` | Human-readable summary |

## Making Your WPF App Testable

wpf-gui-testkit uses UI Automation (UIA) to locate controls. WPF supports UIA out of the box, but there are a few key points to get right.

### AutomationId Naming Convention

Every interactive control must have `AutomationProperties.AutomationId` set, otherwise UIA can't find it reliably:

```xaml
<!-- ✅ Correct: explicit AutomationId -->
<Button AutomationProperties.AutomationId="BtnLogin" Content="Login" />
<TextBox AutomationProperties.AutomationId="TxtUsername" />

<!-- ❌ Wrong: UIA falls back to fuzzy text/index matching — brittle -->
<Button Content="Login" />
<TextBox />
```

**Recommended prefix conventions:**

| Control Type | Prefix | Examples |
|-------------|--------|----------|
| Button | `Btn` | `BtnLogin`, `BtnSave`, `BtnCancel` |
| TextBox | `Txt` | `TxtUsername`, `TxtPassword` |
| ComboBox | `Combo` | `ComboCategory`, `ComboLanguage` |
| Slider | `Slider` | `SliderVolume`, `SliderBrightness` |
| CheckBox | `Chk` | `ChkRemember`, `ChkAgree` |
| RadioButton | `Radio` | `RadioMale`, `RadioFemale` |
| TextBlock | `Txt` (as label) | `TxtStatus`, `TxtTitle` |
| ListBox/ListView | `List` | `ListStations`, `ListResults` |
| Top-level Window | `Window` | `MainWindow`, `SettingsWindow` |

### Locating Child Windows

Pop-up windows (settings, about, dialogs) typically lack auto_id on the window itself. Find them by title:

```python
# Click to open settings
main_page.click_element("BtnSettings")
time.sleep(0.5)

# Find child window by title
settings = main_page.app.window(title="Settings")
assert settings.exists(), "Settings window did not appear"

# Interact with controls inside the child window
checkbox = settings.child_window(title="Enable notifications", control_type="CheckBox")
checkbox.click_input()

# Close
settings.close()
```

### Window Style & UIA Compatibility

| Window Property | Impact | Solution |
|----------------|--------|----------|
| `WindowStyle=None` | UIA title-based lookup may fail | Prefer `auto_id` for window lookup |
| `AllowsTransparency=True` | UIA `InvokePattern` **cannot trigger** Button's Command binding | See details below |
| `Topmost=True` | Overlay intercepts UIA clicks | Close overlay before testing |

### Common Pitfalls

1. **AllowsTransparency + Command binding broken**
   When `WindowStyle=None` + `AllowsTransparency=True`, the WPF layered window routing has a known bug with UIA `InvokePattern`. None of `click()`, `click_input()`, `invoke()`, or `set_focus+ENTER` can trigger Command-bound buttons.
   
   Fix: Use `Click` event in XAML and forward to ViewModel via `Dispatcher.BeginInvoke`:
   
   ```xaml
   <!-- ❌ Not testable -->
   <Button Command="{Binding OpenSettingsCommand}" />
   
   <!-- ✅ Testable -->
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

2. **Guide overlay blocks the main window**
   If your app shows a guide page on first launch with `Topmost=True`, it blocks all UIA clicks on the main window. Close it in the `app_launch` fixture:
   
   ```python
   try:
       guide = app.window(auto_id="GuideView")
       if guide.exists():
           guide.close()
           time.sleep(0.5)
   except:
       pass
   ```

3. **Chinese encoding breaks window lookup (Windows only)**
   When running from WSL/CI, Windows Python's stdout defaults to GBK. Chinese window titles get garbled. Use UTF-8 mode:
   ```bash
   set PYTHONIOENCODING=utf-8
   pytest -v
   ```

4. **ComboBox has no select() method**
   WPF ComboBox doesn't support `select()`. Use keyboard navigation instead:
   ```python
   combo = main_window.child_window(auto_id="ComboCity")
   combo.set_focus()
   combo.type_keys("%{DOWN}")  # Alt+↓ to expand
   combo.type_keys("{DOWN}")   # Select next item
   combo.type_keys("{ENTER}")
   ```

5. **Visibility=Collapsed controls are invisible to UIA**
   UIA does not expose auto_id for `Visibility=Collapsed` controls. You'll need to make them visible first, or search directly under the parent.

## pytest Fixtures (conftest.py)

The `wpf_testkit.core.conftest` module provides ready-to-use pytest fixtures. Simply import it in your test file:

```python
from wpf_testkit.core.conftest import *  # noqa
```

### Fixture Reference

| Fixture | Scope | Description |
|---------|-------|-------------|
| `session_cleanup` | session (autouse) | Kills any leftover processes and cleans `%APPDATA%` before and after the entire test session |
| `app_launch` | function | Starts a fresh app instance per test case. Kills old processes first, then starts `APP_PATH`, polls for the main window (up to 15s), and optionally closes a guide overlay window (see `GUIDE_WINDOW_TITLE`). Yields the `Application` object. |
| `app_connect` | function | Connects to an already-running app. Use when you don't want to restart the app between tests. |
| `main_window` | function | Returns the main window of the launched app (wraps `app_launch`). Polls up to 15s for the `MAIN_WINDOW_ID` auto_id. |
| `screenshot_manager` | function | Creates a `ScreenshotManager` instance with auto-cleanup of screenshots older than 7 days. |
| `auto_screenshot_on_failure` | function (autouse) | Automatically takes a desktop screenshot and saves to `screenshots/failures/` when a test fails. |
| `crash_daemon` | function (autouse) | Uses `app_launch`. Starts a background thread that polls the app process every 2 seconds. If the process disappears unexpectedly, records the crash and marks the test as failed. |

### Guide Window Close

If your app shows a first-launch guide overlay that blocks the main window, set the `WPF_TEST_GUIDE_WINDOW_TITLE` environment variable:

```bash
set WPF_TEST_GUIDE_WINDOW_TITLE=Welcome
```

The `app_launch` fixture will automatically find and close it via `FindWindowW` + `PostMessageW(WM_CLOSE)`.

### Controlling AppData Cleanup (session_cleanup)

Set `WPF_TEST_APP_DATA_DIR` to the directory name under `%APPDATA%` that your app uses:

```bash
set WPF_TEST_APP_DATA_DIR=MyApp
```

This directory will be wiped before each test by the `session_cleanup` fixture.

## Visual Regression Testing (L3)

wpf-gui-testkit includes a PIL-based screenshot comparison engine for catching UI appearance changes.

### Basic Usage

```python
from wpf_testkit.utils.visual_diff import VisualDiff

def test_visual_regression(app_launch, main_window, screenshot_manager):
    # 1. Take a screenshot
    shot = screenshot_manager.capture(main_window, "main_window")

    # 2. Compare against baseline
    vd = VisualDiff()
    result = vd.compare(shot, "screenshots/baseline/main_window.png")

    # 3. First run auto-creates baseline (doesn't fail)
    if result.baseline_missing:
        vd.update_baseline(shot, "screenshots/baseline/main_window.png")
        return

    # 4. Assert diff is within threshold
    assert result.within_threshold(0.05), result.summary()
```

### Diff Highlight Image

`compare()` automatically generates a diff highlight image at `screenshots/diffs/` with differing pixels marked in semi-transparent red for manual review.

### Workflow

| When | Action | Note |
|------|--------|------|
| First run | Auto-creates baseline | Test passes, baseline saved |
| Normal run | Compares against baseline | Fails if diff > 5% |
| After UI redesign | `pytest --update-baseline` | Force-updates all baselines |

## Known Limitations

- **WPF `AllowsTransparency=True` windows** — UIA `InvokePattern` may fail to trigger WPF Command bindings. Use `Click` event + `BeginInvoke` instead.
- **Window `WindowStyle=None`** — Requires custom close button and drag events. Use `auto_id` for window lookup, not `title`.
- **Chinese encoding** — On Windows, run `set PYTHONIOENCODING=utf-8` before pytest.
- **Visual regression + `pytest-xdist`** — Baseline directory is not safe for parallel writes. Do not use `-n auto` with `--update-baseline` or visual regression tests.

## Examples

### WPF Calculator

`examples/wpf-calculator/` — A .NET 9 WPF calculator (14 P0/P1/P2 tests).

Controls covered: Button (digits/operators), TextBlock (display).

```bash
cd examples/wpf-calculator
set WPF_TEST_APP_PATH=C:\path\to\WpfCalculator.exe
pytest -v
```

### WPF Contacts

`examples/wpf-contacts/` — A .NET 9 WPF contacts manager (13 P0/P1/P2 tests).

Controls covered: TextBox (search + form), ListView + GridView, ComboBox, dialog windows, StatusBar.

```bash
cd examples/wpf-contacts
set WPF_TEST_APP_PATH=C:\path\to\WpfContacts.exe
pytest -v
```

## License

MIT
