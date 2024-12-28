@echo off

REM Check if venv exists, if not create it
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate the virtual environment
call .venv\Scripts\activate.bat

REM Check if requirements are installed
pip freeze > temp_requirements.txt
fc /b requirements.txt temp_requirements.txt > nul
if errorlevel 1 (
    echo Installing requirements...
    pip install -r requirements.txt
)
del temp_requirements.txt

REM Run the main.py script
echo Running main.py...
python main.py

REM Deactivate the virtual environment
deactivate
