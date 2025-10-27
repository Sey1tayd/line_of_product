release: cd backend && python manage.py collectstatic --noinput && python manage.py migrate && python manage.py create_superuser
web: cd backend && gunicorn core.wsgi:application --log-file - --bind 0.0.0.0:$PORT --workers 4 --threads 2 --timeout 120
