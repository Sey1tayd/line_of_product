#!/bin/bash
# Railway'de çalıştırılacak fix script

echo "🔧 Fixing Railway deployment..."

# Navigate to backend
cd backend

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "🗄️ Running migrations..."
python manage.py migrate

echo "👤 Creating superuser..."
python manage.py create_superuser

echo "✅ Done! Restart the service."

