"""
Django settings for school_saas project.
Production & Local Environment Ready.
"""

import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# 🚀 SECURITY & CORE SETTINGS
# ==========================================
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-ufq6ti6&r^zpmdf3y6q0rsv!7c8ni*uqw=(s1q$y5hukpno40%')

# DEBUG = True rakha hai local ke liye, Render par isko env variable se False karenge
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

# ==========================================
# 📦 APPLICATIONS
# ==========================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Custom Apps
    'core',
    'accounts',
    'students',
    'fees',
    'attendance',
    'academics',
    'exams',
    'expenses',
]

# ==========================================
# 🛡️ MIDDLEWARE (Whitenoise added for static files)
# ==========================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # 🚀 For Static Files on Live Server
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'school_saas.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.institute_labels',
            ],
        },
    },
]

WSGI_APPLICATION = 'school_saas.wsgi.application'

# ==========================================
# 🗄️ DATABASE CONFIGURATION (NeonDB PostgreSQL)
# ==========================================
# Aapka NeonDB URL yahan default set kar diya hai.
# Agar local par chalaoge ya live par, yeh sidha PostgreSQL se connect hoga!
NEON_DB_URL = "postgresql://neondb_owner:npg_U02FlQmnfpyh@ep-proud-glade-apwf2daz.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require"

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', NEON_DB_URL),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ==========================================
# 🔐 AUTHENTICATION & PASSWORD VALIDATION
# ==========================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

AUTH_USER_MODEL = 'accounts.CustomUser'
LOGIN_URL = 'login'

# ==========================================
# 🌍 INTERNATIONALIZATION
# ==========================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata' # Indian Time
USE_I18N = True
USE_TZ = True

# ==========================================
# 📂 STATIC & MEDIA FILES
# ==========================================
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==========================================
# 📧 EMAIL SMTP CONFIGURATION (For OTP)
# ==========================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
# Yahan apni actual email aur App Password daalna (Local test ke liye)
# Live server par inko Environment Variables (Render) me set karna
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'your_email@gmail.com') 
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'your_app_password_here')

# ==========================================
# HTTPS FORCE (For Live Server)
# ==========================================
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    
    
    # ==========================================
# 🛡️ CSRF TRUSTED ORIGINS (For Render POST Requests)
# ==========================================
CSRF_TRUSTED_ORIGINS = [
    'https://smart-school-saas.onrender.com',
    'https://*.onrender.com',
]