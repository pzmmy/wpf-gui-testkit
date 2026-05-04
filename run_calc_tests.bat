@echo off
chcp 65001 >nul
setlocal

set "TEST_DIR=C:\Users\12442\projects\wpf-gui-testkit"
set "APP_PATH=%TEST_DIR%\examples\wpf-calculator\WpfCalculator\bin\Release\net8.0-windows\win-x64\WpfCalculator.exe"

cd /d "%TEST_DIR%"

echo === kill previous calculator process ===
taskkill /f /im WpfCalculator.exe 2>nul
timeout /t 2 /nobreak 2>nul

echo === run calculator tests ===
set "WPF_TEST_APP_PATH=%APP_PATH%"
set "WPF_TEST_MAIN_WINDOW_ID=MainWindow"
set "WPF_TEST_APP_PROCESS_NAME=WpfCalculator.exe"

C:\Python\Python310\python.exe -m pytest examples/wpf-calculator/tests/test_calculator.py -v --tb=short 2>&1

echo === cleanup ===
taskkill /f /im WpfCalculator.exe 2>nul
echo === DONE ===
