@echo off
python "%~dp0..\cli\mg.py" %*
exit /b %errorlevel%
