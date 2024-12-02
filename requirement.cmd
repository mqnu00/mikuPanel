@echo off
echo Installing pipreqs...
pip install pipreqs
if %errorlevel% neq 0 exit /b %errorlevel%

echo Generating requirements.txt...
pipreqs . --force
if %errorlevel% neq 0 exit /b %errorlevel%

echo Done.