# WPF 通讯录 Demo — GUI 测试示例

一个 WPF 通讯录管理器，用作 `wpf-gui-testkit` 框架的第二个示例应用。

## 覆盖的控件类型

| 控件 | AutomationId | 测试验证点 |
|------|-------------|-----------|
| TextBox（搜索框） | `TxtSearch` | 实时过滤、清空恢复 |
| TextBox（表单输入） | `TxtName`, `TxtPhone`, `TxtEmail` | set_text 输入、预填编辑 |
| ListView + GridView | `ListContacts` | 列表存在性、子控件遍历 |
| ComboBox | `ComboGroup` | 键盘操作选择 |
| Button（主窗口） | `BtnAdd`, `BtnEdit`, `BtnDelete` | 点击触发对话框/删除 |
| Button（对话框） | `BtnSave`, `BtnCancel` | 保存/取消 |
| 对话框窗口 | `ContactDialog` | 窗口查找、关闭 |
| StatusBar | `TxtStatus` | 状态文本断言 |
| TextBlock（消息） | `TxtMessage` | 操作反馈提示 |

## 构建

```bash
cd WpfContacts
dotnet build -c Release
```

构建产物在 `WpfContacts/bin/Release/net9.0-windows/win-x64/WpfContacts.exe`

## 测试

```bash
# 设置被测应用路径
set WPF_TEST_APP_PATH=WpfContacts/bin/Release/net9.0-windows/win-x64/WpfContacts.exe
set WPF_TEST_APP_PROCESS_NAME=WpfContacts.exe
set WPF_TEST_MAIN_WINDOW_ID=MainWindow

# 运行测试
cd tests
pytest test_contacts.py -v
```

## 测试覆盖

### P0 — 核心功能（6 用例）

| 测试 | 说明 |
|------|------|
| test_window_launch | 窗口正常启动 |
| test_initial_contacts_displayed | 5 个预置联系人 |
| test_search_filter_contacts | 搜索框实时过滤 |
| test_search_clear_restores_all | 清空搜索恢复全量 |
| test_add_contact | 添加→填写表单→保存→验证 |
| test_edit_contact | 选中→编辑→修改→保存 |
| test_delete_contact | 选中→删除→验证数量减少 |

### P1 — 交互细节（3 用例）

| 测试 | 说明 |
|------|------|
| test_select_contact_updates_status | 按钮存在性 |
| test_add_dialog_cancel | 取消添加不改变列表 |
| test_all_buttons_exist | 所有控件存在性 |

### P2 — 边界场景（4 用例）

| 测试 | 说明 |
|------|------|
| test_search_empty_list | 搜索无结果 |
| test_edit_requires_selection | 未选中时编辑不触发 |
| test_delete_requires_selection | 未选中时删除不触发 |
| test_dialog_form_validation | 空白表单校验阻止 |

## UI 控件清单

| AutomationId | 控件类型 | 作用 |
|-------------|---------|------|
| `MainWindow` | Window | 主窗口 |
| `ContactDialog` | Window | 新增/编辑对话框 |
| `TxtSearch` | TextBox | 搜索框 |
| `ListContacts` | ListView | 联系人列表（GridView 四列） |
| `BtnAdd` | Button | 添加联系人 |
| `BtnEdit` | Button | 编辑联系人 |
| `BtnDelete` | Button | 删除联系人 |
| `TxtStatus` | TextBlock | 状态栏文本 |
| `TxtMessage` | TextBlock | 操作反馈消息 |
| `TxtName` | TextBox (Dialog) | 姓名输入 |
| `TxtPhone` | TextBox (Dialog) | 电话输入 |
| `TxtEmail` | TextBox (Dialog) | 邮箱输入 |
| `ComboGroup` | ComboBox (Dialog) | 分组选择 |
| `BtnSave` | Button (Dialog) | 保存 |
| `BtnCancel` | Button (Dialog) | 取消 |
