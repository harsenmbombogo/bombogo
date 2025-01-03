import dj_database_url
from pathlib import Path
import os, json
from decouple import config
import pymysql
pymysql.install_as_MySQLdb()
from firebase_admin import initialize_app, credentials
import cloudinary
import cloudinary.uploader
import cloudinary.api


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

APPEND_SLASH=False

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='unsafe-secret-key')

REDIS_URL = config('REDIS_URL', "redis://localhost:6379")
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='localhost').split(',')

# CONFIRACAO DE CLOUDINARY
CLOUD_NAME_CLOUDINARY  = config('CLOUD_NAME')
API_KEY_CLOUDINARY = config('API_KEY')
API_SECRET_CLOUDINARY  = config('API_SECRET')


CSRF_TRUSTED_ORIGINS = [
    'https://bombogo.co.mz',
    'https://www.bombogo.co.mz',
]


# Configurações de segurança (apenas para produção)
# Redirecionamento de HTTP para HTTPS
SECURE_SSL_REDIRECT = True  # Garante redirecionamento para HTTPS
SESSION_COOKIE_SECURE = True  # Garante que cookies só sejam enviados via HTTPS
CSRF_COOKIE_SECURE = True  # Garante que o cookie CSRF seja enviado via HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary_storage',
    'cloudinary',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'home',
    'app',
    'channels',
    'django_celery_beat',
    'fcm_django',
]
# 'django-filter'
# 'corsheaders',
# Set up your Cloudinary credentials
cloudinary.config(
    cloud_name = CLOUD_NAME_CLOUDINARY,  # Replace with your cloud name
    api_key = API_KEY_CLOUDINARY,        # Replace with your API key
    api_secret = API_SECRET_CLOUDINARY   # Replace with your API secret
)

# Definir o armazenamento padrão de mídia
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Carregar as credenciais do Firebase a partir do arquivo .env
cred = credentials.Certificate({
    "type": config('FIREBASE_TYPE'),
    "project_id": config('FIREBASE_PROJECT_ID'),
    "private_key_id": config('FIREBASE_PRIVATE_KEY_ID'),
    "private_key": config('FIREBASE_PRIVATE_KEY').replace(r'\n', '\n'),
    "client_email": config('FIREBASE_CLIENT_EMAIL'),
    "client_id": config('FIREBASE_CLIENT_ID'),
    "auth_uri": config('FIREBASE_AUTH_URI'),
    "token_uri": config('FIREBASE_TOKEN_URI'),
    "auth_provider_x509_cert_url": config('FIREBASE_AUTH_PROVIDER_X509_CERT_URL'),
    "client_x509_cert_url": config('FIREBASE_CLIENT_X509_CERT_URL')
})

# Inicializar o Firebase Admin SDK
FIREBASE_MESSAGING_APP = initialize_app(cred, name='messaging')

FCM_DJANGO_SETTINGS = {
    "DEFAULT_FIREBASE_APP": FIREBASE_MESSAGING_APP,
    "APP_VERBOSE_NAME": "bombogo",
    "ONE_DEVICE_PER_USER": False,
    "DELETE_INACTIVE_DEVICES": True,
}



ASGI_APPLICATION = 'bomboapi.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                REDIS_URL
            ],
        },
    },
}



# Configurações do Celery
CELERY_BROKER_URL = REDIS_URL

# Use um backend para resultados (opcional, mas recomendado)
CELERY_RESULT_BACKEND = REDIS_URL

# Outras configurações do Celery
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# Configuração do Celery Beat (se você estiver usando tarefas agendadas)
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'




REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=31),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=31),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}




MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Coloque isso logo após SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'corsheaders.middleware.CorsMiddleware',

]

ROOT_URLCONF = 'bombogo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bombogo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases


# Configuração do banco de dados (MySQL usando dj-database-url)
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='mysql://usuario:senha@localhost:3306/meubanco')
    )
}

# Senha do banco de dados
DATABASES['default']['OPTIONS'] = {
    'charset': 'utf8mb4',
}



# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'pt'

TIME_ZONE = 'Africa/Maputo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# URL para servir os arquivos estáticos
STATIC_URL = '/static/'

# Diretório onde os arquivos estáticos serão coletados
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Diretórios adicionais para arquivos estáticos
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'app','static'),  # Local para arquivos estáticos do projeto
]


# Medias
MEDIA_URL = '/media/'

# MEDIA_ROOT = os.path.join(BASE_DIR,'media')
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



