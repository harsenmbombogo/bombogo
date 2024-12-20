import dj_database_url
from pathlib import Path
import os
from decouple import config

from firebase_admin import initialize_app, credentials
from google.auth import load_credentials_from_file

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent



APPEND_SLASH=False

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='unsafe-secret-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='localhost').split(',')

# Configurações de segurança (apenas para produção)
SECURE_SSL_REDIRECT = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Novos
    'rest_framework',
    'rest_framework_simplejwt',
    'app',
    'channels',
    'django_celery_beat',
    'fcm_django',
    # 'django-filter'
    # 'corsheaders',
]

class CustomFirebaseCredentials(credentials.ApplicationDefault):
    def __init__(self, account_file_path: str):
        super().__init__()
        self._account_file_path = account_file_path

    def _load_credential(self):
        if not self._g_credential:
            self._g_credential, self._project_id = load_credentials_from_file(self._account_file_path,
                                                                              scopes=credentials._scopes)



custom_credentials = CustomFirebaseCredentials(os.path.join(BASE_DIR,'app','firebase_credentials.json'))
FIREBASE_MESSAGING_APP = initialize_app(custom_credentials, name='messaging')

FCM_DJANGO_SETTINGS = {
     # an instance of firebase_admin.App to be used as default for all fcm-django requests
     # default: None (the default Firebase app)
    "DEFAULT_FIREBASE_APP": FIREBASE_MESSAGING_APP,
     # default: _('FCM Django')
    "APP_VERBOSE_NAME": "bombogo",
     # true if you want to have only one active device per registered user at a time
     # default: False
    "ONE_DEVICE_PER_USER": False,
     # devices to which notifications cannot be sent,
     # are deleted upon receiving error response from FCM
     # default: False
    "DELETE_INACTIVE_DEVICES": False,
}


ASGI_APPLICATION = 'bomboapi.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        #"BACKEND": "channels.db.DatabaseChannelLayer",

        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",  # Substitua pelo seu front-end se necessário
# ]


# Configurações do Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # ou qualquer outro broker que você esteja usando
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Outras configurações do Celery
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'




# Configuracacoes do twilio para verificacao do numero 

TWILIO_ACCOUNT_SID = 'USa88c283a83ce0a6c4fa9d749bb5d8e1b'
TWILIO_AUTH_TOKEN = 'e6dad094bd4d2e8a7b2dd254cb031b66'
TWILIO_PHONE_NUMBER = '+13342924420'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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
import pymysql
pymysql.install_as_MySQLdb()

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'bombogo',
#         'USER': 'root',
#         'PASSWORD': ' ',
#         'HOST': 'localhost',
#         'PORT': '3306',
#         # 'OPTIONS': {
#         #     'autocommit': True,  # Isso ajuda com transações
#         # },
#     }
# }

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

STATIC_URL = 'static/'
# Medias
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,'media')
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



