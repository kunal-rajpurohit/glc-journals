@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
cd src
python manage.py runserver 0.0.0.0:8000
