@echo off
title HO_SO_BOT - FastAPI server
call venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
