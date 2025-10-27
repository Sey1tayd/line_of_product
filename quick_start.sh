#!/bin/bash
# Quick Start Script for Local Development
# Kullanım: bash quick_start.sh

set -e

echo "=================================="
echo "AYD Robotic - Quick Start Setup"
echo "=================================="
echo ""

# Check Python
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "❌ Python bulunamadı! Python 3.12+ gerekli."
    exit 1
fi

PYTHON_CMD=$(command -v python3 || command -v python)
echo "✅ Python bulundu: $($PYTHON_CMD --version)"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Virtual environment oluşturuluyor..."
    $PYTHON_CMD -m venv venv
    echo "✅ Virtual environment oluşturuldu"
fi

# Activate virtual environment
echo ""
echo "🔧 Virtual environment aktif ediliyor..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
echo "✅ Virtual environment aktif"

# Install requirements
echo ""
echo "📥 Dependencies yükleniyor..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies yüklendi"

# Check for .env file
if [ ! -f "backend/.env" ]; then
    echo ""
    echo "⚠️  backend/.env dosyası bulunamadı!"
    echo "📋 .env.example'dan kopyalanıyor..."
    cp backend/.env.example backend/.env
    echo "✅ backend/.env oluşturuldu"
    echo ""
    echo "🔑 SECRET_KEY oluşturuluyor..."
    SECRET_KEY=$($PYTHON_CMD -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    
    # Update .env with generated SECRET_KEY
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" backend/.env
    else
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" backend/.env
    fi
    
    # Set DEBUG to True for local development
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/DEBUG=False/DEBUG=True/" backend/.env
    else
        sed -i "s/DEBUG=False/DEBUG=True/" backend/.env
    fi
    
    echo "✅ SECRET_KEY oluşturuldu ve .env'e kaydedildi"
fi

# Navigate to backend
cd backend

# Run migrations
echo ""
echo "🗄️  Database migrations çalıştırılıyor..."
$PYTHON_CMD manage.py migrate
echo "✅ Migrations tamamlandı"

# Collect static files
echo ""
echo "📦 Static files toplanıyor..."
$PYTHON_CMD manage.py collectstatic --noinput
echo "✅ Static files toplandı"

# Create superuser if not exists
echo ""
echo "👤 Superuser kontrol ediliyor..."
$PYTHON_CMD manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superuser oluşturuldu (username: admin, password: admin123)')
else:
    print('✅ Superuser zaten mevcut')
"

# Seed data (optional)
echo ""
read -p "Test data oluşturulsun mu? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🌱 Test data oluşturuluyor..."
    $PYTHON_CMD manage.py seed_production
    echo "✅ Test data oluşturuldu"
fi

# Done
echo ""
echo "=================================="
echo "✅ Kurulum tamamlandı!"
echo "=================================="
echo ""
echo "🚀 Sunucuyu başlatmak için:"
echo "   cd backend"
echo "   python manage.py runserver"
echo ""
echo "🌐 Tarayıcınızda açın:"
echo "   http://127.0.0.1:8000"
echo ""
echo "🔐 Admin panel:"
echo "   http://127.0.0.1:8000/admin"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "=================================="

