# AYD Robotic Production Management System

Django tabanlı üretim takip ve yönetim sistemi. Bu proje Railway platformunda deploy edilmeye hazır haldedir.

## 🚀 Railway'de Deployment

### Ön Gereksinimler
- Railway hesabı (https://railway.app)
- GitHub/GitLab repository bağlantısı

### Adım 1: Railway Projesi Oluşturma

1. Railway.app'e giriş yapın
2. "New Project" butonuna tıklayın
3. "Deploy from GitHub repo" seçeneğini seçin
4. Bu repository'yi seçin

### Adım 2: PostgreSQL Database Ekleme

1. Railway projenizde "New" butonuna tıklayın
2. "Database" → "Add PostgreSQL" seçin
3. PostgreSQL servisi otomatik olarak `DATABASE_URL` environment variable'ını sağlayacaktır

### Adım 3: Environment Variables Ayarlama

Railway projenizde "Variables" sekmesine gidin ve aşağıdaki değişkenleri ekleyin:

```env
# Zorunlu Değişkenler
SECRET_KEY=your-super-secret-key-here-min-50-chars
DEBUG=False
ALLOWED_HOSTS=.railway.app
CSRF_TRUSTED_ORIGINS=https://your-app-name.up.railway.app
CORS_ALLOWED_ORIGINS=https://your-app-name.up.railway.app

# Superuser Credentials (İlk deployment için)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@yourdomain.com
DJANGO_SUPERUSER_PASSWORD=güçlü-bir-şifre-buraya

# Opsiyonel
DJANGO_LOG_LEVEL=INFO
```

**Önemli Notlar:**
- `SECRET_KEY` için güçlü, rastgele bir string kullanın (minimum 50 karakter)
- `ALLOWED_HOSTS` ve `CSRF_TRUSTED_ORIGINS` değerlerini Railway'den aldığınız domain ile güncelleyin
- `DJANGO_SUPERUSER_PASSWORD` için güçlü bir şifre belirleyin

### Adım 4: Deploy

Railway otomatik olarak projenizi deploy edecektir. Deploy süreci:

1. **Build Phase**: Dependencies yüklenir ve static dosyalar toplanır
2. **Release Phase**: Database migration çalıştırılır ve superuser oluşturulur
3. **Run Phase**: Gunicorn web server başlatılır

### Adım 5: Domain Alma

1. Railway projenizde "Settings" → "Domains" kısmına gidin
2. "Generate Domain" butonuna tıklayın
3. Aldığınız domain'i `CSRF_TRUSTED_ORIGINS` ve `CORS_ALLOWED_ORIGINS` değişkenlerine ekleyin

## 🔧 Local Development

### Kurulum

1. **Virtual Environment Oluşturma**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Dependencies Yükleme**
```bash
pip install -r requirements.txt
```

3. **Environment Variables**
```bash
cp .env.example .env
# .env dosyasını düzenleyin
```

4. **Database Migration**
```bash
cd backend
python manage.py migrate
```

5. **Superuser Oluşturma**
```bash
python manage.py createsuperuser
```

6. **Development Server**
```bash
python manage.py runserver
```

### Test Data Oluşturma
```bash
python manage.py seed_production
```

## 📁 Proje Yapısı

```
ayd_robotic/
├── backend/
│   ├── core/                  # Django project settings
│   │   ├── settings.py       # Production-ready settings
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── production/            # Main application
│   │   ├── models.py         # Database models
│   │   ├── views.py          # API endpoints
│   │   ├── serializers.py    # DRF serializers
│   │   ├── urls.py
│   │   └── management/
│   │       └── commands/
│   │           ├── create_superuser.py
│   │           └── seed_production.py
│   ├── templates/            # HTML templates
│   └── manage.py
├── Procfile                  # Railway/Heroku deployment
├── nixpacks.toml            # Nixpacks configuration
├── runtime.txt              # Python version
├── requirements.txt         # Python dependencies
└── .env.example            # Environment variables template
```

## 🔒 Güvenlik

Production ortamında aşağıdaki güvenlik önlemleri aktiftir:

- ✅ HTTPS yönlendirmesi (SECURE_SSL_REDIRECT)
- ✅ Secure cookies (SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE)
- ✅ XSS koruması (SECURE_BROWSER_XSS_FILTER)
- ✅ Content type sniffing koruması (SECURE_CONTENT_TYPE_NOSNIFF)
- ✅ Clickjacking koruması (X_FRAME_OPTIONS)
- ✅ HSTS (HTTP Strict Transport Security)
- ✅ CORS yapılandırması

## 📊 Features

### Makine Yönetimi
- Makine tanımlaları ve takip
- Takım değişim kayıtları (Tool Change)
- Günlük üretim sayaçları

### Üretim Takibi
- Günlük üretim miktarları
- Çalışma seansları (Work Sessions)
- Kullanıcı bazlı üretim takibi

### Malzeme Yönetimi
- Malzeme tipi tanımlamaları
- Giriş/Çıkış takibi
- Stok özeti

### Admin Paneli
- Activity log görüntüleme
- Kullanıcı yönetimi
- Makine ve takım tipi CRUD operasyonları

## 🛠️ API Endpoints

### Public Endpoints
- `GET /api/dashboard/` - Dashboard verileri
- `GET /api/machines/` - Makine listesi
- `POST /api/login/` - Kullanıcı girişi
- `POST /api/logout/` - Çıkış
- `GET /api/whoami/` - Mevcut kullanıcı bilgisi

### Tool Change
- `POST /api/tool-change/` - Takım değişimi kaydı

### Production
- `POST /api/daily-production/` - Günlük üretim kaydı
- `POST /api/work-session/` - Çalışma seansı kaydı
- `GET /api/machines/<id>/` - Makine detayları

### Material Management
- `GET /api/materials/types/` - Malzeme tipleri
- `GET /api/materials/stock/` - Stok özeti
- `POST /api/materials/entry/` - Malzeme girişi
- `POST /api/materials/shipment/` - Malzeme çıkışı

### Admin (Requires Authentication)
- `POST /api/admin/machines/` - Makine oluştur
- `PUT /api/admin/machines/<id>/` - Makine güncelle
- `DELETE /api/admin/machines/<id>/delete/` - Makine sil
- `POST /api/admin/tooltypes/` - Takım tipi oluştur
- `DELETE /api/admin/tooltypes/<id>/delete/` - Takım tipi sil
- `GET /api/admin/activity-logs/` - Activity logs

## 🐛 Troubleshooting

### Static Files Gösterilmiyor
```bash
cd backend
python manage.py collectstatic --noinput
```

### Database Migration Hataları
```bash
cd backend
python manage.py migrate --run-syncdb
```

### Railway Logs Kontrol
```bash
railway logs
```

### Environment Variables Kontrol
Railway dashboard'da "Variables" sekmesinden tüm değişkenlerin doğru tanımlandığından emin olun.

## 📝 Database Schema

### Core Models
- **Machine**: Üretim makineleri
- **ToolType**: Takım tipleri
- **ToolChangeBatch**: Takım değişim kayıtları
- **DailyProduction**: Günlük üretim kayıtları
- **WorkSession**: Çalışma seansları
- **ActivityLog**: Sistem aktivite logları
- **MaterialType**: Malzeme tipleri
- **MaterialEntry**: Malzeme giriş kayıtları
- **MaterialShipment**: Malzeme sevkiyat kayıtları

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

Bu proje özel lisans altındadır.

## 📧 İletişim

Sorularınız için: admin@yourdomain.com

## 🔄 Version History

### v1.0.0 (2025-10-27)
- ✨ İlk production release
- ✅ Railway deployment desteği
- ✅ PostgreSQL database desteği
- ✅ Production güvenlik ayarları
- ✅ CORS yapılandırması
- ✅ Static files serving (WhiteNoise)
- ✅ Gunicorn web server
- ✅ Otomatik migrations ve superuser oluşturma

