# WPF Contacts Demo — GUI Test Example

A WPF contacts manager app, serving as the second example application for `wpf-gui-testkit`.

## Covered Control Types

| Control | AutomationId | Test Verification |
|---------|-------------|-------------------|
| TextBox (search) | `TxtSearch` | Real-time filtering, clear restores |
| TextBox (form input) | `TxtName`, `TxtPhone`, `TxtEmail` | set_text input, pre-fill edit |
| ListView + GridView | `ListContacts` | List existence, child control traversal |
| ComboBox | `ComboGroup` | Keyboard selection |
| Button (main window) | `BtnAdd`, `BtnEdit`, `BtnDelete` | Click triggers dialog / delete |
| Button (dialog) | `BtnSave`, `BtnCancel` | Save / cancel |
| Dialog window | `ContactDialog` | Window lookup, close |
| StatusBar | `TxtStatus` | Status text assertion |
| TextBlock (message) | `TxtMessage` | Operation feedback |

## Build

```bash
cd WpfContacts
dotnet build -c Release
```

Output at `WpfContacts/bin/Release/net9.0-windows/win-x64/WpfContacts.exe`

## Test

```bash
# Set environment variables
set WPF_TEST_APP_PATH=WpfContacts/bin/Release/net9.0-windows/win-x64/WpfContacts.exe
set WPF_TEST_APP_PROCESS_NAME=WpfContacts.exe
set WPF_TEST_MAIN_WINDOW_ID=MainWindow

# Run tests
cd tests
pytest test_contacts.py -v
```

## Test Coverage

### P0 — Core Functions (7 tests)

| Test | Description |
|------|-------------|
| test_window_launch | Window starts correctly |
| test_initial_contacts_displayed | 5 preset contacts loaded |
| test_search_filter_contacts | Real-time search filtering |
| test_search_clear_restores_all | Clear search restores full list |
| test_add_contact | Add → fill form → save → verify |
| test_edit_contact | Select → edit → modify → save |
| test_delete_contact | Select → delete → verify count decreased |

### P1 — Interaction Details (3 tests)

| Test | Description |
|------|-------------|
| test_select_contact_updates_status | Button existence check |
| test_add_dialog_cancel | Cancel doesn't change list |
| test_all_buttons_exist | All control availability |

### P2 — Edge Cases (4 tests)

| Test | Description |
|------|-------------|
| test_search_empty_list | Search with no results |
| test_edit_requires_selection | Edit not triggered without selection |
| test_delete_requires_selection | Delete not triggered without selection |
| test_dialog_form_validation | Blank form validation |

## UI Control Reference

| AutomationId | Control Type | Purpose |
|-------------|-------------|---------|
| `MainWindow` | Window | Main window |
| `ContactDialog` | Window | Add/edit dialog |
| `TxtSearch` | TextBox | Search box |
| `ListContacts` | ListView | Contact list (GridView, 4 columns) |
| `BtnAdd` | Button | Add contact |
| `BtnEdit` | Button | Edit contact |
| `BtnDelete` | Button | Delete contact |
| `TxtStatus` | TextBlock | Status bar text |
| `TxtMessage` | TextBlock | Operation feedback |
| `TxtName` | TextBox (Dialog) | Name input |
| `TxtPhone` | TextBox (Dialog) | Phone input |
| `TxtEmail` | TextBox (Dialog) | Email input |
| `ComboGroup` | ComboBox (Dialog) | Group selection |
| `BtnSave` | Button (Dialog) | Save |
| `BtnCancel` | Button (Dialog) | Cancel |
