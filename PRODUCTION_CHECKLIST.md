# Production Deployment Checklist

Railway'e deploy etmeden önce bu checklist'i kontrol edin.

## 📋 Pre-Deployment Checklist

### 1. Kod Kontrolü
- [ ] Tüm değişiklikler commit edildi
- [ ] Test edildi ve çalışıyor
- [ ] Linter hataları yok
- [ ] Gereksiz console.log ve print statements kaldırıldı
- [ ] TODO ve FIXME notları gözden geçirildi

### 2. Environment Variables
- [ ] `.env.example` dosyası güncel
- [ ] Tüm gerekli environment variables tanımlandı
- [ ] SECRET_KEY güçlü ve unique (min 50 karakter)
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS doğru ayarlandı
- [ ] CSRF_TRUSTED_ORIGINS tanımlandı
- [ ] CORS_ALLOWED_ORIGINS tanımlandı
- [ ] Database URL yapılandırıldı (PostgreSQL)
- [ ] Superuser credentials ayarlandı

### 3. Django Settings
- [ ] `settings.py` production-ready
- [ ] `DEBUG = False` for production
- [ ] `ALLOWED_HOSTS` configured
- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] Static files yapılandırması tamam
- [ ] Database connection pooling aktif
- [ ] Logging yapılandırıldı

### 4. Database
- [ ] Migrations güncel
- [ ] Migration conflicts yok
- [ ] Database backup stratejisi planlandı
- [ ] PostgreSQL Railway'de oluşturuldu
- [ ] DATABASE_URL environment variable bağlandı

### 5. Static Files
- [ ] WhiteNoise middleware aktif
- [ ] STATIC_ROOT tanımlı
- [ ] STATICFILES_STORAGE ayarlandı
- [ ] `collectstatic` çalışıyor
- [ ] CSS/JS dosyaları erişilebilir

### 6. Dependencies
- [ ] `requirements.txt` güncel
- [ ] Tüm dependency versiyonları belirtilmiş
- [ ] Gereksiz dependencies kaldırıldı
- [ ] Security vulnerabilities kontrol edildi

### 7. Security
- [ ] SECRET_KEY production'da farklı
- [ ] Password policy uygulandı
- [ ] SQL injection koruması (Django ORM)
- [ ] XSS koruması aktif
- [ ] CSRF koruması aktif
- [ ] HTTPS zorunlu
- [ ] Secure headers yapılandırıldı
- [ ] Sensitive data loglanmıyor

### 8. Performance
- [ ] Database queries optimize edildi
- [ ] N+1 query problems çözüldü
- [ ] Static files compression aktif
- [ ] Gunicorn workers ayarlandı
- [ ] Connection pooling yapılandırıldı

### 9. Monitoring & Logging
- [ ] Logging yapılandırıldı
- [ ] Error tracking planlandı
- [ ] Health check endpoint eklendi (`/api/health/`)
- [ ] Railway metrics erişilebilir

### 10. Documentation
- [ ] README.md güncel
- [ ] DEPLOYMENT_GUIDE.md hazır
- [ ] API documentation mevcut
- [ ] Environment variables dokümante edildi

## 🚀 Deployment Steps

### Railway Deployment
- [ ] Railway projesi oluşturuldu
- [ ] GitHub repository bağlandı
- [ ] PostgreSQL servisi eklendi
- [ ] Environment variables ayarlandı
- [ ] Domain generate edildi
- [ ] HTTPS çalışıyor
- [ ] Migrations başarılı
- [ ] Superuser oluşturuldu
- [ ] Static files servis ediliyor

### Post-Deployment
- [ ] Ana sayfa açılıyor
- [ ] Login çalışıyor
- [ ] Admin panel erişilebilir
- [ ] API endpoints test edildi
- [ ] Database bağlantısı stabil
- [ ] Error tracking çalışıyor
- [ ] SSL certificate geçerli

## 🔍 Testing Checklist

### Functionality Tests
- [ ] User authentication
  - [ ] Login
  - [ ] Logout
  - [ ] Session management
- [ ] Dashboard
  - [ ] Data loading
  - [ ] Machine cards display
- [ ] Machine Management
  - [ ] List machines
  - [ ] Create machine (admin)
  - [ ] Update machine (admin)
  - [ ] Delete machine (admin)
- [ ] Tool Change
  - [ ] Create tool change record
  - [ ] View history
- [ ] Production Tracking
  - [ ] Daily production records
  - [ ] Work sessions
- [ ] Material Management
  - [ ] Material types
  - [ ] Stock entries
  - [ ] Stock shipments
  - [ ] Stock summary
- [ ] Activity Logs
  - [ ] View logs (admin)
  - [ ] Filter logs

### Performance Tests
- [ ] Page load time < 2 seconds
- [ ] API response time < 500ms
- [ ] Database query time acceptable
- [ ] Static files load quickly
- [ ] No memory leaks

### Security Tests
- [ ] HTTPS enforced
- [ ] CSRF protection working
- [ ] XSS protection working
- [ ] Authentication required for protected routes
- [ ] Admin-only endpoints protected
- [ ] SQL injection attempts blocked

## 📊 Monitoring Setup

### Railway Dashboard
- [ ] CPU usage monitored
- [ ] Memory usage monitored
- [ ] Network traffic monitored
- [ ] Error rate tracked
- [ ] Deploy history visible

### Application Metrics
- [ ] Request count
- [ ] Response times
- [ ] Error rate
- [ ] Database connections
- [ ] Active users

## 🔐 Security Hardening

### Application Level
- [x] Django security middleware aktif
- [x] SECURE_SSL_REDIRECT enabled
- [x] SESSION_COOKIE_SECURE enabled
- [x] CSRF_COOKIE_SECURE enabled
- [x] SECURE_BROWSER_XSS_FILTER enabled
- [x] SECURE_CONTENT_TYPE_NOSNIFF enabled
- [x] X_FRAME_OPTIONS set to DENY
- [x] HSTS enabled

### Platform Level
- [ ] Railway environment variables güvenli
- [ ] Database password güçlü
- [ ] Backup encryption aktif
- [ ] Access control yapılandırıldı

## 💾 Backup Strategy

### Database Backups
- [ ] Otomatik backup aktif (Railway)
- [ ] Manuel backup alındı
- [ ] Backup restore test edildi
- [ ] Backup retention policy belirlendi

### Code Backups
- [ ] Git repository güncel
- [ ] Branch protection rules aktif
- [ ] Release tags oluşturuldu

## 📈 Scaling Considerations

### Current Setup
- Railway free tier: 500 saat/ay
- Gunicorn: 4 workers, 2 threads
- PostgreSQL: Railway managed
- Static files: WhiteNoise

### When to Scale
- [ ] CPU usage > 70% sustained
- [ ] Memory usage > 80%
- [ ] Response time > 1 second
- [ ] Free tier limit approaching
- [ ] User base growing

### Scaling Options
- [ ] Upgrade Railway plan
- [ ] Increase Gunicorn workers
- [ ] Add Redis caching
- [ ] Implement CDN for static files
- [ ] Database read replicas

## 🐛 Troubleshooting Reference

### Common Issues

#### Static Files Not Loading
```bash
cd backend
python manage.py collectstatic --noinput
```

#### Database Connection Error
- Check PostgreSQL service status
- Verify DATABASE_URL variable
- Check connection pooling settings

#### 400 Bad Request
- Verify ALLOWED_HOSTS
- Check CSRF_TRUSTED_ORIGINS
- Ensure correct domain in settings

#### 502 Bad Gateway
- Check Railway logs
- Verify Gunicorn is running
- Check PORT variable

#### Migration Errors
```bash
cd backend
python manage.py migrate --run-syncdb
```

## ✅ Final Verification

### Before Going Live
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Team trained
- [ ] Rollback plan ready
- [ ] Support contact info documented
- [ ] Monitoring alerts configured

### After Going Live
- [ ] Monitor for 24 hours
- [ ] Check error logs
- [ ] Verify user feedback
- [ ] Performance metrics acceptable
- [ ] Backup verified

## 📞 Emergency Contacts

### Technical
- Railway Support: https://railway.app/help
- Django Documentation: https://docs.djangoproject.com
- Project Repository: [Your GitHub URL]

### Team
- Project Lead: [Name/Email]
- DevOps: [Name/Email]
- Database Admin: [Name/Email]

## 📝 Sign-Off

- [ ] Developer: _________________ Date: _________
- [ ] QA: _________________ Date: _________
- [ ] DevOps: _________________ Date: _________
- [ ] Project Manager: _________________ Date: _________

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-27  
**Next Review**: [Set date for next review]

