@echo off
setlocal

cd /d "%~dp0"

echo Checking Python virtual environment...
if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    py -3 -m venv .venv
)

echo Activating virtual environment...
call ".venv\Scripts\activate.bat"

echo Installing Python requirements...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Installing Node packages...
call npm install

echo Building CSS...
call npm run build

echo Opening browser...
start "" http://127.0.0.1:5000

echo Starting Flask app...
python checkin_backend\run.py