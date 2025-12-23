@echo off
setlocal

python -m venv .venv
call .venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt

pyinstaller --noconfirm --clean --name "DE Scripts MLO Studio" --windowed app\main.py

echo Build complete. Output is in dist\
endlocal
