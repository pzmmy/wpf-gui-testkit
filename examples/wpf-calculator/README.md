# WPF 计算器 Demo — GUI 测试示例

一个极简的 WPF 计算器，用作 `wpf-gui-testkit` 框架的示例应用。

## 构建

```bash
cd WpfCalculator
dotnet build -c Release
```

构建产物在 `WpfCalculator/bin/Release/net8.0-windows/win-x64/WpfCalculator.exe`

## 测试

```bash
# 设置被测应用路径
set WPF_TEST_APP_PATH=WpfCalculator/bin/Release/net8.0-windows/win-x64/WpfCalculator.exe
set WPF_TEST_APP_PROCESS_NAME=WpfCalculator.exe
set WPF_TEST_MAIN_WINDOW_ID=MainWindow

# 运行测试
cd tests
pytest test_calculator.py -v
```

## 测试覆盖

| 标记 | 测试 | 说明 |
|------|------|------|
| P0 | test_app_launch | 窗口正常启动 |
| P0 | test_display_initially_zero | 初始显示 0 |
| P0 | test_addition | 1 + 2 = 3 |
| P0 | test_all_buttons_exist | 所有按钮存在 |
| P1 | test_subtraction | 5 - 3 = 2 |
| P1 | test_multiplication | 4 × 5 = 20 |
| P1 | test_division | 10 ÷ 2 = 5 |
| P1 | test_chain_calculation | 3 + 4 - 2 = 5 |
| P1 | test_clear | 清除返回 0 |
| P1 | test_decimal | 3.5 + 1.5 = 5 |
| P2 | test_divide_by_zero | 除零错误 |

## UI 控件清单

| AutomationId | 控件 | 作用 |
|-------------|------|------|
| DisplayText | TextBlock | 结果显示 |
| Btn0-Btn9 | Button | 数字 0-9 |
| BtnPlus | Button | 加号 |
| BtnMinus | Button | 减号 |
| BtnMultiply | Button | 乘号 |
| BtnDivide | Button | 除号 |
| BtnEquals | Button | 等号 |
| BtnClear | Button | 清除 |
| BtnDecimal | Button | 小数点 |
| BtnNegate | Button | 取反 |
| BtnBackspace | Button | 退格 |
