#!/bin/bash
# Railway startup script
# This runs migrations and starts the server

set -e

echo "🚀 Starting deployment..."

cd backend

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

# Create superuser if needed
echo "👤 Creating superuser (if needed)..."
python manage.py create_superuser || echo "Superuser already exists"

# Start Gunicorn
echo "🌐 Starting Gunicorn server..."
exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --threads 2 \
    --timeout 120 \
    --log-file - \
    --access-logfile - \
    --error-logfile -

