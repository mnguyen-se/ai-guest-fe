@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
python collect_daily.py >> collect_log.txt 2>&1