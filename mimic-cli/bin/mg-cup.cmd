@echo off
call "%~dp0mg.cmd" probe cup %*
exit /b %errorlevel%
