# Changelog

## v0.4.5 (2026-05-04)

- 🆕 **测爷第二轮评审修复** — 覆盖缺口全部补齐（5 项，0🔴）
  - ProgressBar 自动停止验证：从 0% 启动 → 等跑到 100% 自动停止 → Reset（P1）
  - Slider 边界值：`set_slider_value(0)` 和 `set_slider_value(100)`（P2，{HOME}+{RIGHT} 步进）
  - Expander 内 CheckBox 点击：展开后点击 `ChkAutoUpdate`（P1）
  - DatePicker 区域格式：`select_date` 改用 `^a`（Ctrl+A）全选替代 `^{HOME}`，不依赖区域格式（🟢）
  - Page Object 新增：`wait_until()` 通用轮询、`set_slider_value()`、`wait_progress_stopped()`、
    `click_auto_update_checkbox()`、`is_wifi_on()`
  - 测试总数：P0(7) + P1(6) + P2(5) = **18 测试用例**

## v0.4.4 (2026-05-04)

- 🐛 **测爷评审修复** — 修复 P3 测试分析的 5 项问题（0 🔴 / 4 🟡 / 1 🟢）
  - 新增 `DatePicker` 选择日期测试（P1），覆盖核心交互路径（🔴 覆盖缺口）
  - 新增 `ComboBox` 存在性测试（🔴 覆盖缺口，降级为 P2）
  - `Expander` 测试中用 `wait_expander_state()` 轮询替代 `time.sleep(0.3)`（🟡 flaky 风险）
  - 两个 `time.sleep(0.3)` → `page.wait_short(0.3)`（🟡 命名统一）
  - Page Object 新增 `select_date()`、`wait_short()`、`wait_expander_state()` 方法
  - 测爷误报：ToolBar 按钮无 Click 事件不是编译问题（有意设计，仅测存在性）

## v0.4.3 (2026-05-04)

- 🐛 **审爷评审修复** — 修复 P3 新增代码的 8 项问题（0 🔴 / 4 🟡 / 4 🟢）
  - `pytest_configure` 加 `@pytest.hookimpl(tryfirst=True)` 保护（🟡）
  - `UPDATE_BASELINE` 改为有条件赋值，避免 `getoption` 在非 pytest 环境中抛异常（🟡）
  - `test_progress_bar_start_reset` 增加进度推进验证 + sleep 延至 0.8s（🟡）
  - `visual_regression_fixture` → `visual_regression_check` 重命名（🟡 命名误导）
  - `test_date_picker_exists` 断言从 `"selected"` 改为 `"No date selected"`（🟢 过宽断言）
  - `ToggleWifi` → `ToggleWiFi` PascalCase 统一（🟢）
  - `ControlsPage.__init__` 预置 `_window`，去除惰性加载（🟢 性能优化）
  - README 中英文版新增 xdist 不兼容文档（🟢）
- 🔧 **ruff lint 清理** — 整个项目 `ruff check` 全部通过
  - 修复 `time` 未使用导入（calculator test）、`old_count` 未使用变量（contacts test）
  - 统一 `# noqa: F403` 写法到所有测试文件

## v0.4.2 (2026-05-04)

- 🆕 **新示例：WPF 控件展示（wpf-controls）** — 覆盖 10+ 控件类型，14 测试用例
  - ToggleButton (×3): Wi-Fi/Bluetooth/Airplane On/Off 切换
  - RadioButton (×3): Light/Dark/System 主题选择
  - Slider: 音量滑块 + 值显示
  - Expander: 展开/折叠 + 内含 CheckBox 可见性
  - DatePicker: 日期选择 + 状态文本
  - ProgressBar: Start/Reset 功能
  - ToolBar + Separator: 工具栏容器
  - GroupBox: 分组容器内含 ComboBox + CheckBox
  - 控件类型对比（P0: 7 / P1: 4 / P2: 3）
- 🆕 **截图 baseline 管理自动化** — `pytest --update-baseline` 选项
  - conftest 新增 `pytest_addoption` / `pytest_configure` 注册 `--update-baseline`
  - visual_diff.py 新增 `UPDATE_BASELINE` 全局标志
  - `visual_regression_fixture` 在 `--update-baseline` 时强制更新 baseline
  - UI 改版后只需 `pytest --update-baseline` 即可刷新所有基准图
- 📝 README 中英文版：新增 wpf-controls 到项目结构、`--update-baseline` 到工作流表

## v0.4.1 (2026-05-04)

- 🐛 **Calculator 测试修复** — 4 个失败全部归零（14/14 通过）
  - `MainWindow.xaml` 减号按钮 Content 从 `−` (U+2212 MINUS SIGN) 改为 `-` (U+002D HYPHEN-MINUS)，修复 C# `Operator_Click` 中 switch 匹配不到操作符的 bug
  - `enter_digits()` 移除 `-` → `BtnNegate` 的错误映射（操作符由 `click_operator` 统一处理）
  - `press_keys()` 末尾补上 `return self.get_display_text()`（之前返回 None）
  - `run_calc_tests.bat` 指向 `bin\Release\net8.0-windows\win-x64\`（之前指向旧路径 `bin\x64\Release\...`）
- 📝 **README.en.md 补全** — 新增 conftest fixtures 说明、guide window close 配置、app_connect 使用方式，与中文版功能对齐

## v0.4.0 (2026-05-04)

- 🆕 **视觉回归引擎（L3）** — `visual_diff.py`，零额外依赖
  - `VisualDiff.compare()` — 像素级差异计算（PIL ImageChops）
  - `DiffResult` — 差异统计（pct/count/max_diff）+ 阈值判定
  - 自动生成差异高亮图（红色标注差异区域）
  - `update_baseline()` — 首次运行自动创建基准
  - 18 个自测覆盖全部路径（含边界：缺失/尺寸/全同/全异/部分差异）
- 📝 README 新增：L3 视觉回归使用说明 + VisualDiff/DiffResult API 参考

## v0.3.0 (2026-05-04)

- 🆕 **新示例：WPF 通讯录（wpf-contacts）** — 覆盖更多控件类型
  - ListView + GridView（联系人列表）
  - TextBox 实时搜索过滤
  - ComboBox（分组选择）
  - 对话框窗口（ContactDialog：新增/编辑）
  - StatusBar / TextBlock 状态显示
  - 分层 P0/P1/P2 测试，共 **13 个测试用例**
- 📝 更新 README 项目结构

## v0.2.0 (2026-05-04)

- 🔧 **进程清理增强** — `kill_all_app()` 递归杀子进程 + 超时保护，防止 WPF 子进程残留
- ✅ **框架自测（32 用例全部通过）** — 为 exceptions/screenshot/crash_daemon/base_page/uia_helpers 编写 pytest，mock 掉平台依赖，可在无 Windows UIA 环境的 CI 中运行
- 📝 **WPF 测试配合指南** — README 新增 AutomationId 命名规范、子窗口定位、窗口样式兼容性、Avoid Pitfalls（AllowsTransparency+Command 失效、引导页覆盖、中文编码、ComboBox 操作等）
- 🔧 环境变量表说明更新（子进程递归杀）

## v0.1.1 (2026-05-04)

- 📝 **README 重写** — 快速开始示例改为通用表单场景（之前偏媒体播放器）
- 🔧 **默认路径移除** — `WPF_TEST_APP_PATH` 不再有内置默认值，必须通过环境变量显式设置
- 🔧 **默认值修复** — README 环境变量表中 `MAIN_WINDOW_ID` 默认值修正为 `MainWindow`（与代码一致）
- 🏗️ 总体定位调整：从"极简"调整为"通用"，示例更中立

## v0.1.0 (2026-05-03)

- 🎉 **首次公开发布**
  - BasePage: 四级点击兜底（click → click_input → invoke → set_focus+ENTER）
  - CrashDaemon: 崩溃守护线程（2 秒轮询检测进程）
  - ScreenshotManager: 全屏/ROI/失败截图 + 自动清理
  - conftest: 进程隔离、AppData 清理、失败截图钩子
  - 示例: WPF 计算器 14 个 P0/P1/P2 分级测试
- 🐍 支持 Python 3.9+
- 📦 零外部服务依赖（不需要 WinAppDriver）
