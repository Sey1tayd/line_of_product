release: cd backend && python manage.py migrate && python manage.py create_superuser
web: cd backend && gunicorn core.wsgi:application --log-file - --bind 0.0.0.0:$PORT
