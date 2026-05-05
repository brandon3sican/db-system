@echo off
title Database System
cd /d "%~dp0"
echo Starting Database System...
start /B python app.py
if errorlevel 1 (
    echo.
    echo Error occurred while starting application.
    pause
)
