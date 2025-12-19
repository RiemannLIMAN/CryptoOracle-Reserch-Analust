@echo off
setlocal

:: ========================================================
:: Configuration
:: ========================================================
:: Default virtual environment name
set "VENV_NAME=okx_research"

:: Check if a custom VENV name is provided in .env file
if exist .env (
    for /f "tokens=1,2 delims==" %%A in (.env) do (
        if "%%A"=="VENV_NAME" set "VENV_NAME=%%B"
    )
)
:: ========================================================

echo ========================================================
echo       OKX Research Analyst - Startup Script
echo       Virtual Environment: %VENV_NAME%
echo ========================================================

:: 1. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

:: 2. Check/Create Virtual Environment
if not exist "%VENV_NAME%" (
    echo [INFO] Virtual environment '%VENV_NAME%' not found. Creating...
    python -m venv "%VENV_NAME%"
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [INFO] Virtual environment created successfully.
)

:: 3. Activate Virtual Environment
echo [INFO] Activating virtual environment...
call "%VENV_NAME%\Scripts\activate"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

:: 4. Install/Update Dependencies
echo [INFO] Installing/Updating dependencies...
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

:: 5. Run the Application
echo [INFO] Starting application...
echo --------------------------------------------------------

if "%1"=="-d" goto :run_background
if "%1"=="--daemon" goto :run_background

:: Foreground Mode
python src\main.py %*
goto :cleanup

:run_background
:: Shift arguments not easily possible in simple batch goto logic with %*, 
:: so we manually handle the shift or just pass all if complex.
:: But %* includes the -d. Python script might treat "-d" as a query.
:: Simple workaround: We assume if -d is passed, the user might not be passing other args for daemon mode,
:: or we rely on main.py to ignore flags? No, main.py treats everything as query.
:: Let's use a small powershell helper or just pythonw for Windows background.

echo [INFO] Starting application in BACKGROUND mode (Minimized Window)...
:: Create logs directory if not exists
if not exist logs mkdir logs

:: Launch in a separate minimized window
:: We use `start` to launch.
:: We need to strip the first argument (-d). 
:: Batch argument parsing is painful. 
:: Let's just run it. The user query with -d is rarely used together.
:: Usually daemon mode is just `run.bat -d`.

:: Remove the first argument from %*? 
:: %* contains all arguments. 
:: We can iterate.
shift
:: Note: `shift` only affects %1, %2... it does NOT update %*.
:: So we have to reconstruct the command line or just pass nothing if it's daemon mode.
:: If user does `run.bat -d "query"`, it's tricky in batch.
:: Let's assume for daemon mode, we usually don't need a specific query (it runs scheduler).
:: So we just run python src\main.py without args if -d is present, OR we try to handle it.

start "OKX Analyst (Background)" /MIN python src\main.py
echo [INFO] Application is running in a minimized window.
echo [INFO] You can check logs in logs\okx_research.log
goto :cleanup

:cleanup
:: 6. Cleanup
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application exited with error code %errorlevel%.
)

echo.
echo [INFO] Done.
pause