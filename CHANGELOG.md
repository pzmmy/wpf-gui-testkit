# Changelog

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
