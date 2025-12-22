@echo off
setlocal

set APP_NAME=DEScriptsMLOStudio
set RELEASE_DIR=release\%APP_NAME%

if exist release rmdir /s /q release

pyinstaller --noconsole --onedir --name "%APP_NAME%" ui.py

mkdir "%RELEASE_DIR%"
xcopy /E /I /Y "dist\%APP_NAME%\*" "%RELEASE_DIR%" >nul
xcopy /I /Y module_library.json "%RELEASE_DIR%" >nul
xcopy /E /I /Y assets "%RELEASE_DIR%\assets" >nul

echo Release created at %RELEASE_DIR%
endlocal
