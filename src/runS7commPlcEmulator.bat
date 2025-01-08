echo "Running S7comm PLC emulator [s7commPlcApp.py]"
@echo off
call workon vEnv3.8

REM Check if the environment activation was successful
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment vEnv3.8
    exit /b %errorlevel%
)

REM Run the Python script
call s7commPlcEmulator\s7commPlcApp.py