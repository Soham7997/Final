@echo off
REM Simple redirect to the main batch file
REM This allows easier execution from File Explorer

cd /d "%~dp0"
call start_all.bat
