# Local Development Guide

Bu rehber, projeyi local ortamda çalıştırmak için gerekli adımları içerir.

## 📋 Gereksinimler

- Python 3.12+ 
- pip (Python package manager)
- Git
- PostgreSQL (opsiyonel, SQLite kullanılabilir)

## 🚀 Hızlı Başlangıç

### Windows
```bash
quick_start.bat
```

### Linux/Mac
```bash
bash quick_start.sh
```

Bu script otomatik olarak:
- Virtual environment oluşturur
- Dependencies yükler
- SECRET_KEY generate eder
- Database migrate eder
- Superuser oluşturur
- Static files toplar

## 📝 Manuel Kurulum

### 1. Repository'yi Clone Edin
```bash
git clone <repository-url>
cd ayd_robotic
```

### 2. Virtual Environment Oluşturun
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Dependencies Yükleyin
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Environment Variables Ayarlayın

#### .env Dosyası Oluşturun
```bash
# backend/.env dosyasını oluşturun
cp backend/.env.example backend/.env
```

#### SECRET_KEY Generate Edin
```bash
cd backend
python generate_secret_key.py
```

Çıktıyı kopyalayıp `backend/.env` dosyasındaki `SECRET_KEY` değerine yapıştırın.

#### .env Dosyasını Düzenleyin
```env
# backend/.env
SECRET_KEY=yukarıda-oluşturduğunuz-key
DEBUG=True  # Local development için True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
CORS_ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# SQLite kullanılacak (DATABASE_URL belirtmeyin)
# PostgreSQL için:
# DATABASE_URL=postgresql://user:password@localhost:5432/ayd_robotic

DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin123
```

### 5. Database Setup

#### SQLite (Default - Kolay)
```bash
cd backend
python manage.py migrate
```

#### PostgreSQL (Opsiyonel - Production-like)
```bash
# PostgreSQL yükleyin ve database oluşturun
createdb ayd_robotic

# .env dosyasına ekleyin:
# DATABASE_URL=postgresql://user:password@localhost:5432/ayd_robotic

cd backend
python manage.py migrate
```

### 6. Superuser Oluşturun

#### Otomatik (Environment Variables'dan)
```bash
cd backend
python manage.py create_superuser
```

#### Manuel
```bash
cd backend
python manage.py createsuperuser
# Username, email, password girin
```

### 7. Test Data Oluşturun (Opsiyonel)
```bash
cd backend
python manage.py seed_production
```

Bu command oluşturur:
- 3 makine
- Her makine için 3 takım tipi
- Örnek takım değişim kayıtları
- Örnek üretim kayıtları

### 8. Static Files Toplayın
```bash
cd backend
python manage.py collectstatic --noinput
```

### 9. Development Server'ı Başlatın
```bash
cd backend
python manage.py runserver
```

Server çalışıyor: http://127.0.0.1:8000

## 🌐 Uygulama Erişimi

### Ana Sayfa
```
http://127.0.0.1:8000/
```

### Login Sayfası
```
http://127.0.0.1:8000/login/
```
- Username: admin (veya belirlediğiniz)
- Password: admin123 (veya belirlediğiniz)

### Admin Panel
```
http://127.0.0.1:8000/admin/
```
- Superuser credentials ile giriş yapın

### API Endpoints
```
http://127.0.0.1:8000/api/health/
http://127.0.0.1:8000/api/dashboard/
http://127.0.0.1:8000/api/machines/
http://127.0.0.1:8000/api/whoami/
```

## 🛠️ Development Workflow

### Code Changes
1. Değişiklik yapın
2. Server otomatik reload olur
3. Tarayıcıda test edin

### Database Changes
```bash
# Model değişikliği yaptınız
cd backend

# Migration oluşturun
python manage.py makemigrations

# Migration'ı uygulayın
python manage.py migrate

# Migration'ı geri alın (gerekirse)
python manage.py migrate production zero
```

### New Dependencies
```bash
# Yeni package yükleyin
pip install package-name

# requirements.txt güncelleyin
pip freeze > requirements.txt
```

### Shell Access
```bash
cd backend

# Django shell
python manage.py shell

# Database shell
python manage.py dbshell
```

## 🧪 Testing

### Run Tests
```bash
cd backend
python manage.py test
```

### Specific App Tests
```bash
cd backend
python manage.py test production
```

### With Coverage
```bash
pip install coverage
cd backend
coverage run --source='.' manage.py test
coverage report
coverage html  # HTML report
```

## 🐛 Debugging

### Django Debug Toolbar (Opsiyonel)
```bash
pip install django-debug-toolbar
```

`backend/core/settings.py` içine ekleyin:
```python
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']
```

### Logging
Log dosyaları console'da görünür. Detaylı logging için `settings.py` düzenleyin.

### Database Inspection
```bash
cd backend
python manage.py dbshell

# SQLite için
sqlite3 db.sqlite3
.tables
.schema production_machine
```

## 📊 Useful Commands

### Django Management
```bash
cd backend

# Create new app
python manage.py startapp app_name

# Check for issues
python manage.py check

# Show migrations
python manage.py showmigrations

# Create migration without applying
python manage.py makemigrations --dry-run

# SQL for migration
python manage.py sqlmigrate production 0001

# Flush database (DELETE ALL DATA!)
python manage.py flush
```

### User Management
```bash
cd backend

# Create superuser
python manage.py createsuperuser

# Change password
python manage.py changepassword username
```

### Static Files
```bash
cd backend

# Collect static files
python manage.py collectstatic

# Find static files
python manage.py findstatic filename.css
```

## 🔍 Troubleshooting

### Virtual Environment Not Activating
**Windows:**
```bash
# PowerShell execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Port Already in Use
```bash
# Windows - Find and kill process
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Use different port
python manage.py runserver 8080
```

### Module Not Found
```bash
# Ensure virtual environment is activated
# Reinstall requirements
pip install -r requirements.txt
```

### Database Locked (SQLite)
```bash
# Stop all servers
# Delete db.sqlite3
# Recreate database
python manage.py migrate
```

### Static Files Not Loading
```bash
cd backend
python manage.py collectstatic --noinput

# Check STATIC_ROOT in settings.py
# Ensure WhiteNoise middleware is active
```

### CSRF Token Missing
- Ensure `{% csrf_token %}` in forms
- Check CSRF_TRUSTED_ORIGINS in settings
- Clear browser cookies

## 🎨 Frontend Development

### Static Files Location
```
backend/
  staticfiles/           # Collected static files
  production/
    static/             # App-specific static
      production/
        css/
        js/
        img/
```

### Template Location
```
backend/
  templates/            # Project templates
    index.html
    login.html
    machine_detail.html
    sessions.html
```

### Template Development
1. Edit HTML files in `backend/templates/`
2. Save changes
3. Refresh browser (no restart needed)
4. For static file changes, run collectstatic

## 📱 API Development

### Testing API with curl
```bash
# Health check
curl http://localhost:8000/api/health/

# Dashboard data
curl http://localhost:8000/api/dashboard/

# Login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# With session
curl http://localhost:8000/api/whoami/ \
  --cookie "sessionid=<session-id>"
```

### Testing API with Postman
1. Import collection (create one)
2. Set base URL: `http://localhost:8000`
3. Test endpoints

### API Documentation
See `README.md` for full API endpoint list.

## 🔄 Git Workflow

### Daily Development
```bash
# Pull latest changes
git pull origin main

# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit
git add .
git commit -m "feat: your feature description"

# Push to remote
git push origin feature/your-feature

# Create Pull Request on GitHub
```

### Commit Message Convention
```
feat: new feature
fix: bug fix
docs: documentation
style: formatting
refactor: code restructuring
test: adding tests
chore: maintenance
```

## 🚀 Going to Production

Projeyi production'a almadan önce:

1. Tüm testler passing
2. Migrations güncel
3. No linter errors
4. Documentation güncel
5. `PRODUCTION_CHECKLIST.md` tamamlandı
6. `DEPLOYMENT_GUIDE.md` takip edildi

## 💡 Tips & Best Practices

### Development
- Virtual environment her zaman aktif
- Değişiklikler küçük ve sık commit
- Branch protection kullan
- Code review yap
- Test yaz

### Django
- DEBUG=True only for development
- Use Django ORM (SQL injection protection)
- CSRF protection aktif tut
- Sensitive data loglanmamalı
- Environment variables kullan

### Database
- Development için SQLite yeterli
- Production-like test için PostgreSQL
- Migrations version control'de
- Seed data development için
- Production data asla local'e alma

### Performance
- N+1 query'leri önle (select_related, prefetch_related)
- Database indexing düşün
- Query count monitor et
- Caching kullan (Redis)
- Lazy loading kullan

## 📚 Resources

### Django
- Official Docs: https://docs.djangoproject.com
- DRF Docs: https://www.django-rest-framework.org
- Django Best Practices: https://django-best-practices.readthedocs.io

### Python
- Python Docs: https://docs.python.org/3/
- PEP 8 Style Guide: https://pep8.org
- Python Package Index: https://pypi.org

### Tools
- Railway Docs: https://docs.railway.app
- PostgreSQL Docs: https://www.postgresql.org/docs/
- Git Docs: https://git-scm.com/doc

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Write tests
5. Update documentation
6. Submit Pull Request

## 📞 Getting Help

- Project README: `README.md`
- Deployment Guide: `DEPLOYMENT_GUIDE.md`
- Production Checklist: `PRODUCTION_CHECKLIST.md`
- Changelog: `CHANGELOG.md`

---

**Happy Coding! 🎉**

