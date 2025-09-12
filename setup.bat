@echo off
REM Employee Management System Setup Script for Windows

echo ====================================
echo Employee Management System Setup
echo ====================================

echo.
echo Step 1: Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment. Make sure Python is installed.
    pause
    exit /b 1
)

echo.
echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 3: Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo Step 4: Copying environment file...
if not exist .env (
    copy .env.example .env
    echo Environment file created. Please update .env with your settings.
) else (
    echo .env file already exists.
)

echo.
echo Step 5: Running Django migrations (for admin interface)...
python manage.py migrate

echo.
echo ====================================
echo Setup completed successfully!
echo ====================================
echo.
echo Step 6: Starting Django server...
start "Django Server" cmd /k "python manage.py runserver"

echo.
echo Step 7: Opening frontend...
timeout /t 3 /nobreak > nul
start "" "frontend\index.html"

echo.
echo ====================================
echo Setup completed successfully!
echo ====================================
echo.
echo Django API server is running at: http://localhost:8000/employees/
echo Frontend is opened in your default browser
echo.
echo Press any key to exit setup...
pause > nul
