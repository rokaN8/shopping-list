@echo off
echo Setting up Shopping List App for Windows...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.7+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Python found. Version:
python --version

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo.
echo Installing Python packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install requirements.
    pause
    exit /b 1
)

REM Generate SSL certificates
echo.
echo Generating SSL certificates...
python generate_certs.py
if %errorlevel% neq 0 (
    echo WARNING: Failed to generate SSL certificates. HTTPS will not be available.
)

REM Set default credentials if not set
if "%SHOPPING_USERNAME%"=="" (
    set SHOPPING_USERNAME=admin
    echo Using default username: admin
)
if "%SHOPPING_PASSWORD%"=="" (
    set SHOPPING_PASSWORD=password123
    echo Using default password: password123
)

echo.
echo ===== SETUP COMPLETE =====
echo.
echo Your shopping list app is ready!
echo.
echo To start the app, run: run_windows.bat
echo.
echo Default credentials:
echo   Username: %SHOPPING_USERNAME%
echo   Password: %SHOPPING_PASSWORD%
echo.
echo The app will be available at:
echo   HTTPS: https://localhost:7666 (if certificates were generated)
echo   HTTP:  http://localhost:7666 (fallback)
echo.
echo To change credentials, set environment variables:
echo   set SHOPPING_USERNAME=your_username
echo   set SHOPPING_PASSWORD=your_password
echo.
pause