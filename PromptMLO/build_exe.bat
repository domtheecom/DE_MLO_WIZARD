@echo off
setlocal

python -m pip install --upgrade pyinstaller
pyinstaller --onefile --noconsole --name PromptMLO_Studio app.py

echo Build complete. EXE is in the dist folder.
endlocal
