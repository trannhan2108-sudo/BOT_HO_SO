
@echo off
setlocal
REM Run from repo root
python tools\make_manifest.py
echo Manifest generated: MANIFEST.md
pause
