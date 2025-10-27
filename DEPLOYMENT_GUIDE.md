# Railway Deployment Rehberi

Bu rehber, AYD Robotic Production Management sistemini Railway platformunda adım adım deploy etmenizi sağlayacaktır.

## 📋 Ön Hazırlık

### 1. Railway Hesabı Oluşturma
- [Railway.app](https://railway.app) adresine gidin
- GitHub hesabınız ile giriş yapın
- Ücretsiz plan 500 saat/ay kullanım sağlar (küçük projeler için yeterlidir)

### 2. Repository Hazırlığı
```bash
# Değişikliklerinizi commit edin
git add .
git commit -m "Railway deployment ready"
git push origin main
```

## 🚀 Deployment Adımları

### Adım 1: Yeni Proje Oluşturma

1. Railway dashboard'a gidin: https://railway.app/dashboard
2. **"New Project"** butonuna tıklayın
3. **"Deploy from GitHub repo"** seçeneğini seçin
4. Repository listesinden **ayd_robotic** projesini seçin
5. Railway otomatik olarak projeyi algılayacak ve build başlatacaktır

### Adım 2: PostgreSQL Database Ekleme

1. Proje sayfanızda **"New"** butonuna tıklayın
2. **"Database"** → **"Add PostgreSQL"** seçin
3. PostgreSQL servisi otomatik olarak oluşturulacaktır
4. Railway otomatik olarak `DATABASE_URL` environment variable'ını backend servisinize bağlayacaktır

### Adım 3: Environment Variables Ayarlama

#### SECRET_KEY Oluşturma
Railway dashboard'da terminal açın veya local terminalinizde çalıştırın:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### Variables Ekleme

Backend servisinize tıklayın ve **"Variables"** sekmesine gidin. Aşağıdaki değişkenleri ekleyin:

##### Zorunlu Değişkenler:

```env
SECRET_KEY=yukarıda-oluşturduğunuz-secret-key-buraya
DEBUG=False
ALLOWED_HOSTS=.railway.app,.up.railway.app
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@yourdomain.com
DJANGO_SUPERUSER_PASSWORD=güçlü-şifre-buraya-123!@#
```

##### Domain Ayarlandıktan Sonra Eklenecekler:

```env
CSRF_TRUSTED_ORIGINS=https://your-app-name.up.railway.app
CORS_ALLOWED_ORIGINS=https://your-app-name.up.railway.app
```

##### Opsiyonel:

```env
DJANGO_LOG_LEVEL=INFO
```

### Adım 4: Domain Alma ve Ayarlama

1. Backend servisinize tıklayın
2. **"Settings"** → **"Networking"** → **"Public Networking"** kısmına gidin
3. **"Generate Domain"** butonuna tıklayın
4. Örnek domain: `ayd-robotic-production.up.railway.app`

#### Domain'i Environment Variables'a Ekleyin:

```env
CSRF_TRUSTED_ORIGINS=https://ayd-robotic-production.up.railway.app
CORS_ALLOWED_ORIGINS=https://ayd-robotic-production.up.railway.app
```

**ÖNEMLİ:** Variables'ı güncelledikten sonra Railway otomatik olarak yeniden deploy edecektir.

### Adım 5: Deployment'ı İzleme

1. **"Deployments"** sekmesine gidin
2. En son deployment'a tıklayın
3. **"View Logs"** ile deploy sürecini izleyin

Başarılı bir deployment şu aşamalardan geçer:
- ✅ **Building**: Dependencies yüklenir
- ✅ **Release**: Migrations çalışır, superuser oluşturulur
- ✅ **Running**: Gunicorn server başlar

### Adım 6: İlk Giriş

1. Domain adresinize gidin: `https://ayd-robotic-production.up.railway.app`
2. `/login` sayfasına gidin
3. Environment variables'da tanımladığınız username ve password ile giriş yapın
4. `/admin` paneline erişebilirsiniz

## 🔍 Verification Checklist

Deployment'ınızın başarılı olduğunu doğrulamak için:

- [ ] Ana sayfa açılıyor mu?
- [ ] `/login` sayfası çalışıyor mu?
- [ ] Superuser ile giriş yapabildiniz mi?
- [ ] `/admin` paneline erişebildiniz mi?
- [ ] API endpoint'leri çalışıyor mu? (`/api/dashboard/`)
- [ ] Static dosyalar yükleniyor mu? (CSS, JS)

## 🐛 Sorun Giderme

### 1. Static Dosyalar Yüklenmiyor

**Çözüm:**
```bash
# Railway terminal'den veya local:
cd backend
python manage.py collectstatic --noinput
```

Railway'de otomatik olarak `Procfile` içinde yapılıyor ancak manuel kontrol için:
- Railway dashboard → Service → Settings → Deploy Trigger → Manuel restart

### 2. "Bad Request (400)" Hatası

**Sebep:** `ALLOWED_HOSTS` veya `CSRF_TRUSTED_ORIGINS` yanlış yapılandırılmış.

**Çözüm:**
```env
ALLOWED_HOSTS=.railway.app,.up.railway.app,your-actual-domain.up.railway.app
CSRF_TRUSTED_ORIGINS=https://your-actual-domain.up.railway.app
```

### 3. Database Connection Hatası

**Kontrol:**
- Railway dashboard'da PostgreSQL servisi çalışıyor mu?
- `DATABASE_URL` variable otomatik olarak eklendi mi?
- Backend servisi PostgreSQL servisine bağlı mı? (Reference variable)

**Çözüm:**
- PostgreSQL servisine tıklayın
- "Variables" sekmesinde `DATABASE_URL` değişkenini kopyalayın
- Backend servisinin variables'ına manuel ekleyin: `${{Postgres.DATABASE_URL}}`

### 4. Migration Hataları

**Railway terminal'den:**
```bash
cd backend
python manage.py migrate --run-syncdb
python manage.py create_superuser
```

### 5. 502 Bad Gateway

**Sebep:** Server başlamamış olabilir.

**Kontrol:**
- Logs'larda hata var mı?
- Gunicorn düzgün başladı mı?
- PORT variable'ı otomatik eklendi mi?

### 6. Superuser Oluşturulamadı

**Manuel Oluşturma:**
Railway terminal'den:
```bash
cd backend
python manage.py createsuperuser
```

Veya custom command:
```bash
cd backend
python manage.py create_superuser
```

## 📊 Railway Dashboard Kullanımı

### Logs Görüntüleme
```
Service → Deployments → Latest → View Logs
```

### Database Yönetimi
```
PostgreSQL Service → Data → Connect
```

### Environment Variables Güncelleme
```
Service → Variables → + New Variable
```

### Yeniden Deploy
```
Service → Settings → Redeploy
```

### Ölçüm Metrikleri
```
Service → Metrics → CPU, Memory, Network
```

## 💡 İpuçları

### 1. Custom Domain Ekleme
Railway'de custom domain (örn: production.yourdomain.com) ekleyebilirsiniz:
```
Service → Settings → Networking → Custom Domain → Add
```

### 2. Otomatik Deployment
Her `git push` otomatik olarak Railway'de yeni deployment tetikler. Bunu devre dışı bırakmak için:
```
Service → Settings → Deployment → Disable Auto Deploy
```

### 3. Scheduled Tasks (Cron Jobs)
Railway'de cron jobs için ayrı bir servis oluşturabilirsiniz:
```yaml
# Procfile içinde
worker: cd backend && python manage.py your_scheduled_command
```

### 4. Multiple Environments
Development ve Production ortamları için farklı Railway projeleri oluşturabilirsiniz:
- `ayd-robotic-dev` (Development)
- `ayd-robotic-prod` (Production)

### 5. Backup Stratejisi
PostgreSQL için Railway otomatik backup yapar, ancak manuel backup da alabilirsiniz:
```
PostgreSQL Service → Data → Backup
```

## 🔒 Güvenlik Önerileri

1. **SECRET_KEY**: Mutlaka güçlü ve unique bir key kullanın
2. **SUPERUSER_PASSWORD**: Güçlü şifre + 2FA aktif edin
3. **DEBUG**: Production'da her zaman `False` olmalı
4. **ALLOWED_HOSTS**: Sadece kendi domainlerinizi ekleyin
5. **Environment Variables**: Hassas bilgileri asla kod içinde tutmayın

## 📈 Performans Optimizasyonu

### Gunicorn Workers
`Procfile` içinde worker sayısını ayarlayabilirsiniz:
```
web: cd backend && gunicorn core.wsgi:application --workers 4 --threads 2 --timeout 120
```

**Formula:** `workers = (2 x CPU_cores) + 1`

Railway free tier: 1 CPU → 2-3 worker yeterlidir

### Database Connection Pooling
`settings.py` içinde zaten yapılandırılmış:
```python
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,  # 10 dakika connection pooling
    )
}
```

### Static Files Compression
WhiteNoise zaten compression kullanıyor (brotli/gzip)

## 🎯 Sonraki Adımlar

1. **Monitoring**: Railway metrics ile CPU/Memory kullanımını izleyin
2. **Logging**: Django logging yapılandırması ile hata takibi yapın
3. **Testing**: Production ortamında kapsamlı test yapın
4. **Backup**: Düzenli database backup stratejisi oluşturun
5. **Documentation**: Takımınız için kullanım kılavuzu hazırlayın

## 📞 Destek

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Django Documentation: https://docs.djangoproject.com

## ✅ Deployment Checklist

Deployment öncesi kontrol listesi:

- [ ] Tüm environment variables ayarlandı
- [ ] SECRET_KEY güçlü ve unique
- [ ] DEBUG=False
- [ ] PostgreSQL database eklendi
- [ ] ALLOWED_HOSTS doğru yapılandırıldı
- [ ] CSRF_TRUSTED_ORIGINS doğru yapılandırıldı
- [ ] Superuser credentials ayarlandı
- [ ] requirements.txt güncel
- [ ] Migrations çalışıyor
- [ ] Static files toplaniyor
- [ ] Logs kontrol edildi
- [ ] Ana sayfa açılıyor
- [ ] Login çalışıyor
- [ ] Admin panel erişilebilir

---

**Tebrikler! 🎉** Projeniz artık Railway'de canlıda!

