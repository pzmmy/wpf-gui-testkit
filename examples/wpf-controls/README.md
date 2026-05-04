# WPF Controls Demo — GUI Test Example

A WPF controls showcase demo, covering 10+ control types for `wpf-gui-testkit` framework testing.

## Covered Control Types

| Control | AutomationId | Test Verification |
|---------|-------------|-------------------|
| ToggleButton (×3) | `ToggleWifi`, `ToggleBluetooth`, `ToggleAirplane` | Click toggle On/Off, existence |
| RadioButton (×3) | `RadioLight`, `RadioDark`, `RadioSystem` | Selection switching |
| Slider | `SliderVolume` | Initial value, bounds |
| Expander | `ExpanderAdvanced` | Expand/collapse, inner controls visibility |
| DatePicker | `DatePickerStart` | Existence, status text |
| ProgressBar | `ProgressBarDemo` | Start/Reset functionality |
| Button (×2) | `BtnProgressStart`, `BtnProgressReset` | Click triggers progress |
| ToolBar | `ToolBarMain` | Contains inner buttons |
| GroupBox | `GroupBoxPrefs` | Contains CheckBox + ComboBox |
| CheckBox (×4) | `ChkAutoUpdate`, `ChkUsageData`, `ChkNotify`, `ChkAutoUpdate` | Existence in Expander/GroupBox |
| ComboBox | `ComboLanguage` | Existence in GroupBox |
| Separator | `SepTool1` | Existence in ToolBar |

## Build

```bash
cd WpfControls
dotnet build -c Release
```

Output at `WpfControls/bin/Release/net9.0-windows/win-x64/WpfControls.exe`

## Test

```bash
# Set environment variables
set WPF_TEST_APP_PATH=WpfControls/bin/Release/net9.0-windows/win-x64/WpfControls.exe
set WPF_TEST_APP_PROCESS_NAME=WpfControls.exe
set WPF_TEST_MAIN_WINDOW_ID=MainWindow

# Run tests
cd tests
pytest test_controls.py -v
```

## Test Coverage

### P0 — Core Functions (7 tests)

| Test | Control | Description |
|------|---------|-------------|
| test_window_launch | Window | Main window exists and visible |
| test_toggle_wifi_on_off | ToggleButton | Click → On/Off → On |
| test_radio_button_selection | RadioButton | Light → Dark → System |
| test_slider_initial_value | Slider | Default value is 50 |
| test_expander_toggle | Expander | Expand → Collapsed → Expanded |
| test_date_picker_exists | DatePicker | Control exists |
| test_progress_bar_start_reset | ProgressBar | Start then Reset to 0% |

### P1 — Interaction Details (4 tests)

| Test | Control | Description |
|------|---------|-------------|
| test_all_toggles_exist | ToggleButton ×3 | All three present |
| test_toolbar_buttons_exist | ToolBar | New/Save/Delete buttons exist |
| test_expander_inner_controls_visible_when_expanded | Expander → CheckBox | Inner controls appear on expand |
| test_groupbox_controls_exist | GroupBox | CheckBox + ComboBox inside |

### P2 — Edge Cases (3 tests)

| Test | Control | Description |
|------|---------|-------------|
| test_expander_inner_controls_hidden_when_collapsed | Expander | Status shows Collapsed |
| test_slider_bounds | Slider | Value within [0, 100] |
| test_toggle_multiple_preserves_last_status | ToggleButton | Status reflects latest toggle |

## UI Control Reference

| AutomationId | Control Type | Purpose |
|-------------|-------------|---------|
| `MainWindow` | Window | Main window |
| `ToggleWifi` | ToggleButton | Wi-Fi on/off |
| `ToggleBluetooth` | ToggleButton | Bluetooth on/off |
| `ToggleAirplane` | ToggleButton | Airplane mode on/off |
| `TxtToggleStatus` | TextBlock | Toggle status display |
| `RadioLight` | RadioButton | Light theme |
| `RadioDark` | RadioButton | Dark theme |
| `RadioSystem` | RadioButton | System theme |
| `TxtRadioStatus` | TextBlock | Radio status display |
| `SliderVolume` | Slider | Volume slider |
| `TxtSliderValue` | TextBlock | Slider value display |
| `ExpanderAdvanced` | Expander | Advanced settings expander |
| `ChkAutoUpdate` | CheckBox | Auto-update toggle |
| `ChkUsageData` | CheckBox | Usage data toggle |
| `TxtExpanderStatus` | TextBlock | Expander status |
| `DatePickerStart` | DatePicker | Date selector |
| `TxtDateStatus` | TextBlock | Date status display |
| `ProgressBarDemo` | ProgressBar | Progress indicator |
| `BtnProgressStart` | Button | Start/stop progress |
| `BtnProgressReset` | Button | Reset progress to 0 |
| `TxtProgressStatus` | TextBlock | Progress % display |
| `ToolBarMain` | ToolBar | Toolbar container |
| `BtnToolNew` | Button | New (toolbar) |
| `BtnToolSave` | Button | Save (toolbar) |
| `BtnToolDelete` | Button | Delete (toolbar) |
| `GroupBoxPrefs` | GroupBox | Preferences container |
| `ChkNotify` | CheckBox | Notify toggle |
| `ComboLanguage` | ComboBox | Language selection |
| `TxtGroupBoxStatus` | TextBlock | GroupBox status |
