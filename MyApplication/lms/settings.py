import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-jaoz$=owh#^$9k$@l0r*e14pm!#&43yul$#%titfs)g03#orha'
DEBUG = True
ALLOWED_HOSTS = []

# 🔐 Tenant Configuration
TENANT_MODEL = "lms_project.Institution"
TENANT_DOMAIN_MODEL = "lms_project.Domain"
PUBLIC_SCHEMA_NAME = "public"
TENANT_URLCONF = "lms_project.tenant_urls"
PUBLIC_SCHEMA_URLCONF = "lms.urls"

# 🔧 App Configuration
SHARED_APPS = [
    'django_tenants',
    'core',  # must come before auth
    'lms_project',
    'auditlog',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

TENANT_APPS = [
    'core',
    'django.contrib.auth',
    'django.contrib.admin',
    # other tenant-scoped apps
]

INSTALLED_APPS = SHARED_APPS + [app for app in TENANT_APPS if app not in SHARED_APPS] + [
    'corsheaders',
    'rest_framework',
]

# 🔐 Authentication
AUTH_USER_MODEL = 'core.User'
AUTHENTICATION_BACKENDS = [
    'core.backends.StrictEmailBackend',
    'core.backends.RegistrationNumberBackend',
]
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=24),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}


# 🌍 Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Dar_es_Salaam'
USE_I18N = True
USE_TZ = True

# 🧱 Middleware
MIDDLEWARE = [
    'django_tenants.middleware.TenantMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 🌐 URLs & Templates
ROOT_URLCONF = 'lms.urls'
WSGI_APPLICATION = 'lms.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# 🗄️ Database
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': 'lms_db',
        'USER': 'postgres',
        'PASSWORD': 'Hussein0910@',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'options': '-c search_path=public'
        }
    }
}

DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)

# 🔐 Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 📦 Static & Media
STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 🌍 CORS
CORS_ALLOW_ALL_ORIGINS = True

# 🧠 Default Primary Key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'