@echo off
REM This copy is PRE-SETUP: the database already has the press, all 9 journals,
REM sample issues/articles and your superuser account built in.
REM This script only needs to install Python packages. Needs Python 3.10-3.12.
cd /d "%~dp0"
if not exist .venv (py -3.12 -m venv .venv || py -3 -m venv .venv)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo DONE. Now double-click run.bat and open http://localhost:8000/
echo Log in with the email kunalrajpurohit@glcmumbai.example
echo and the password you were given separately.
echo (Janeway logs in by email, not by a plain username.)
echo Change the password the first time you log in.
pause
