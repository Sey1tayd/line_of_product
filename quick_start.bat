@echo off
REM Quick Start Script for Local Development (Windows)
REM Kullanim: quick_start.bat

echo ==================================
echo AYD Robotic - Quick Start Setup
echo ==================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python bulunamadi! Python 3.12+ gerekli.
    pause
    exit /b 1
)

echo + Python bulundu
python --version

REM Create virtual environment
if not exist "venv" (
    echo.
    echo Creating virtual environment...
    python -m venv venv
    echo + Virtual environment olusturuldu
)

REM Activate virtual environment
echo.
echo + Virtual environment aktif ediliyor...
call venv\Scripts\activate.bat

REM Install requirements
echo.
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo + Dependencies yuklendi

REM Check for .env file
if not exist "backend\.env" (
    echo.
    echo ! backend\.env dosyasi bulunamadi!
    echo Copying from .env.example...
    copy backend\.env.example backend\.env
    echo + backend\.env olusturuldu
    
    echo.
    echo Generating SECRET_KEY...
    python -c "from django.core.management.utils import get_random_secret_key; key = get_random_secret_key(); import os; content = open('backend/.env', 'r').read(); open('backend/.env', 'w').write(content.replace('your-secret-key-here-generate-a-strong-one', key).replace('DEBUG=False', 'DEBUG=True'))"
    echo + SECRET_KEY olusturuldu
)

REM Navigate to backend
cd backend

REM Run migrations
echo.
echo Running database migrations...
python manage.py migrate
echo + Migrations tamamlandi

REM Collect static files
echo.
echo Collecting static files...
python manage.py collectstatic --noinput
echo + Static files toplandi

REM Create superuser
echo.
echo Creating superuser...
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123') and print('+ Superuser olusturuldu')"

REM Ask for seed data
echo.
set /p SEED="Test data olusturulsun mu? (y/n): "
if /i "%SEED%"=="y" (
    echo Seed data olusturuluyor...
    python manage.py seed_production
    echo + Test data olusturuldu
)

REM Done
echo.
echo ==================================
echo + Kurulum tamamlandi!
echo ==================================
echo.
echo Sunucuyu baslatmak icin:
echo    cd backend
echo    python manage.py runserver
echo.
echo Tarayicinizda acin:
echo    http://127.0.0.1:8000
echo.
echo Admin panel:
echo    http://127.0.0.1:8000/admin
echo    Username: admin
echo    Password: admin123
echo.
echo ==================================
pause

