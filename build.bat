@echo off
echo ========================================
echo    Clocker - Build Script
echo ========================================
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo.

REM Build the executable with admin manifest
echo Building executable...
pyinstaller --onefile --windowed --name "Clocker" --icon=NONE --uac-admin --add-data "clocker_config.json;." --hidden-import=tkcalendar --hidden-import=babel.numbers clocker.py

echo.
echo ========================================
echo Build complete!
echo Executable: dist\Clocker.exe
echo ========================================
echo.
echo The executable will automatically request
echo administrator privileges when launched.
echo.
pause
