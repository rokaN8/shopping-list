@echo off
echo Starting Shopping List App...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found.
    echo Please run setup_windows.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set default credentials if not set
if "%SHOPPING_USERNAME%"=="" set SHOPPING_USERNAME=admin
if "%SHOPPING_PASSWORD%"=="" set SHOPPING_PASSWORD=password123

echo Credentials:
echo   Username: %SHOPPING_USERNAME%
echo   Password: %SHOPPING_PASSWORD%
echo.

REM Check for SSL certificates
if exist "certs\cert.pem" (
    if exist "certs\key.pem" (
        echo SSL certificates found. Starting HTTPS server...
        echo App will be available at: https://localhost:7666
    ) else (
        echo SSL key not found. Starting HTTP server...
        echo App will be available at: http://localhost:7666
    )
) else (
    echo SSL certificates not found. Starting HTTP server...
    echo App will be available at: http://localhost:7666
    echo Run 'python generate_certs.py' to enable HTTPS.
)

echo.
echo Press Ctrl+C to stop the server.
echo.

REM Start the application
python app.py