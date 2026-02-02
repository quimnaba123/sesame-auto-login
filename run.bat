@echo off
REM Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python no está instalado. Por favor, instala Python y vuelve a intentarlo.
    pause
    exit /b
)

REM Create Venv
IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate

REM Install requirements
echo Installing requirements
pip install --upgrade pip
pip install -r requirements.txt

REM run main.py
echo Running main.py...
python main.py
pause 

REM Deactivating venv
echo Deactivating the virtual environment...
deactivate

echo Execution finished.

