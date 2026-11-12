@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Falta el entorno Python. Consulta PANEL_WEB.md.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -X utf8 bittle_web.py
pause
