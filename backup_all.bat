@echo off
setlocal
REM ==== PHẢI SỬA CHO ĐÚNG 3 BIẾN NÀY ====
set REPO=F:\AI AUTOMATION\BOT_HO_SO
set DRIVE_TEMPLATES="G:\My Drive\BOT_HO_SO\templates"
set DRIVE_OUTPUTS="G:\My Drive\BOT_HO_SO\outputs"

REM ==== KHÔNG SỬA ====
set LOCAL_TEMPLATES=%REPO%\code\HO_SO_BOT\templates
set LOCAL_OUTPUTS=%REPO%\code\HO_SO_BOT\1_ChoDuyet

cd /d %REPO%
git add -A
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set DATE=%%c-%%a-%%b
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set TIME=%%a-%%b
git commit -m "backup: %DATE% %TIME%"
git push

xcopy "%LOCAL_TEMPLATES%\*" %DRIVE_TEMPLATES%\ /E /I /Y
xcopy "%LOCAL_OUTPUTS%\*" %DRIVE_OUTPUTS%\ /E /I /Y

echo Done. Git pushed and Drive folders updated.
pause
