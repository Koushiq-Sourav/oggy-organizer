@echo off
REM Oggy Organizer local start. Keep this window open.
.venv\Scripts\python -m uvicorn src.main:app --host 127.0.0.1 --port 8001
pause
