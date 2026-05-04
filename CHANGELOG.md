# Changelog

## v0.3.0 (2026-05-04)

- 🆕 **新示例：WPF 通讯录（wpf-contacts）** — 覆盖更多控件类型
  - ListView + GridView（联系人列表）
  - TextBox 实时搜索过滤
  - ComboBox（分组选择）
  - 对话框窗口（ContactDialog：新增/编辑）
  - StatusBar / TextBlock 状态显示
  - 分层 P0/P1/P2 测试，共 **13 个测试用例**
- 🔧 更新 README 项目结构

## v0.2.0 (2026-05-04)

- 🔧 **进程清理增强** — `kill_all_app()` 递归杀子进程 + 超时保护，防止 WPF 子进程残留
- ✅ **框架自测（32 用例全部通过）** — 为 exceptions/screenshot/crash_daemon/base_page/uia_helpers 编写 pytest，mock 掉平台依赖，可在无 Windows UIA 环境的 CI 中运行
- 📝 **WPF 测试配合指南** — README 新增 AutomationId 命名规范、子窗口定位、窗口样式兼容性、Avoid Pitfalls（AllowsTransparency+Command 失效、引导页覆盖、中文编码、ComboBox 操作等）
- 🔧 环境变量表说明更新（子进程递归杀）

## v0.1.1 (2026-05-04)

- 📝 **README 重写**：快速开始示例改为通用表单场景（之前偏媒体播放器）
- 🔧 **默认路径移除**：`WPF_TEST_APP_PATH` 不再有内置默认值，必须通过环境变量显式设置
- 🔧 **默认值修复**：README 环境变量表中 `MAIN_WINDOW_ID` 默认值修正为 `MainWindow`（与代码一致）
- 🏗️ 总体定位调整：从"极简"调整为"通用"，示例更中立

## v0.1.0 (2026-05-03)

- 🎉 首次公开发布
- 🎯 BasePage: 四级点击兜底（click → click_input → invoke → set_focus+ENTER）
- 🛡️ CrashDaemon: 崩溃守护线程（2 秒轮询检测进程）
- 📸 ScreenshotManager: 全屏/ROI/失败截图 + 自动清理
- 🧹 conftest: 进程隔离、AppData 清理、失败截图钩子
- 🔧 示例: WPF 计算器 14 个 P0/P1/P2 分级测试
- 🐍 支持 Python 3.9+
- 📦 零外部服务依赖（不需要 WinAppDriver）
