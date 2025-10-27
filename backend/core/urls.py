"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie
from production.views import machine_detail

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('production.urls')),
    # Public routes
    path('login/', ensure_csrf_cookie(TemplateView.as_view(template_name='login.html')), name='login-page'),
    # Ensure CSRF cookie is set for frontend POSTs (serves backend/templates/index.html)
    path('', ensure_csrf_cookie(TemplateView.as_view(template_name='index.html'))),
    path('sessions/', ensure_csrf_cookie(TemplateView.as_view(template_name='sessions.html')), name='sessions-page'),
    path('machine/<int:machine_id>/', ensure_csrf_cookie(TemplateView.as_view(template_name='machine_detail.html')), name='machine-detail-page'),
]
