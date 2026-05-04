# Changelog

## v0.1.0 (2026-05-03)

- 🎉 首次公开发布
- 🎯 BasePage: 四级点击兜底（click → click_input → invoke → set_focus+ENTER）
- 🛡️ CrashDaemon: 崩溃守护线程（2 秒轮询检测进程）
- 📸 ScreenshotManager: 全屏/ROI/失败截图 + 自动清理
- 🧹 conftest: 进程隔离、AppData 清理、失败截图钩子
- 🔧 示例: WPF 计算器 14 个 P0/P1/P2 分级测试
- 🐍 支持 Python 3.9+
- 📦 零外部服务依赖（不需要 WinAppDriver）
