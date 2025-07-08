@echo off
echo Activating virtual environment...
call ..\.venv\Scripts\activate.bat

cd /d %~dp0

echo Starting Flask App...
set FLASK_APP=app
set FLASK_ENV=development
flask run
