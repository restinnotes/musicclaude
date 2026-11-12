@echo off
call "%~dp0mg.cmd" ask %*
exit /b %errorlevel%
