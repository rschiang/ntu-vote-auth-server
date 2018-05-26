"""
Django settings for NTU Vote authentication server.
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Read configuration file

CONFIG_FILE = os.environ.get('CONFIG_FILE', 'core/config/default.yml')
with open(os.path.join(BASE_DIR, CONFIG_FILE), 'r') as f:
    import yaml
    CONFIG = yaml.load(f)

# Project-wide settings

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = CONFIG['secret']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = CONFIG['debug']

# HTTP configuration

if 'host' in CONFIG:
    ALLOWED_HOSTS = [CONFIG['host']]

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'rest_framework',
    'core',
    'account',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

WSGI_APPLICATION = 'core.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'account.authentication.AccountTokenAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '30/minute',
        'strict': '3/minute',
    },
    'EXCEPTION_HANDLER': 'core.views.rest_exception_handler',
}

# Authentication

AUTH_USER_MODEL = 'account.User'

# Templates

TEMPLATE_DEBUG = DEBUG

# Database

DATABASES = {}

if CONFIG['database']['engine'] == 'psql':
    # Enable the use of external database
    # You may install additional dependencies like this:
    #     apt-get install python3-dev libpq-dev
    #     pip install psycopg2
    DATABASES['default'] = { k.upper(): v for k, v in CONFIG['database']}
    DATABASES['default']['engine'] = 'django.db.backends.postgresql_psycopg2'
else:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, CONFIG['database']['file']),
    }

# Internationalization

LANGUAGE_CODE = 'zh-tw'
TIME_ZONE = 'Asia/Taipei'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Logging

LOGGING_DIR = os.path.join(BASE_DIR, CONFIG.get('log', '.'))
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'debug_log', 'mail_admins'],
            'level': 'DEBUG',
        },
        'django.security': {
            'handlers': ['console', 'security_log', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'py.warnings': {
            'handlers': ['console', 'debug_log'],
        },
        'vote': {
            'handlers': ['vote_log'],
            'level': 'DEBUG',
        },
    },
    'formatters': {
        'default': {
            'format': '[{asctime}] {levelname}: {message}',
            'style': '{'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'debug_log': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGGING_DIR, 'debug.log'),
            'formatter': 'default',
        },
        'security_log': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGGING_DIR, 'security.log'),
            'formatter': 'default',
        },
        'vote_log': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGGING_DIR, 'vote.log'),
            'formatter': 'default',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
}

# Mail

if 'mail' in CONFIG:
    EMAIL_HOST = CONFIG['mail'].get('host', 'localhost')
    EMAIL_PORT = CONFIG['mail'].get('port', 25)
    EMAIL_HOST_USER = CONFIG['mail'].get('user', '')
    EMAIL_HOST_PASSWORD = CONFIG['mail'].get('password', '')
    if CONFIG['mail'].get('tls'):
        EMAIL_USE_TLS = True
    elif CONFIG['mail'].get('ssl'):
        EMAIL_USE_SSL = True
    SERVER_EMAIL = CONFIG['mail']['from']
    DEFAULT_FROM_EMAIL = SERVER_EMAIL
    EMAIL_SUBJECT_PREFIX = '[vote-auth] '
    ADMINS = list(CONFIG['admin'].items())

# Cache

if 'cache' in CONFIG:
    CACHES = {
        'default': {
            'BACKEND': ({
                'db': 'django.core.cache.backends.db.DatabaseCache',
                'file': 'django.core.cache.backends.filebased.FileBasedCache',
                'memcached': 'django.core.cache.backends.memcached.MemcachedCache',
            }).get(CONFIG['cache']['backend']),
            'LOCATION': CONFIG['cache'].get('location', '')
        }
    }

# NTU Vote specific settings

# REST API declaration
API_VERSION = '4'

# External service configurations
VOTE_HOST = CONFIG['vote']['host']
VOTE_API_KEY = CONFIG['vote']['key']
VOTE_API_URL = CONFIG['vote']['url']
ACA_API_USER = CONFIG['aca']['user']
ACA_API_PASSWORD = CONFIG['aca']['password']
ACA_API_URL = CONFIG['aca']['url']

# Security enforcements (strict, quirk, off)
CARD_VALIDATION_MODE = CONFIG['security']
CARD_VALIDATION_STRICT = (CARD_VALIDATION_MODE == 'strict')
CARD_VALIDATION_QUIRK = (CARD_VALIDATION_MODE == 'quirk')
CARD_VALIDATION_OFF = (CARD_VALIDATION_MODE == 'off')

# Election meta information
UNDERGRADUATE_CODE = "BTE"
GRADUATE_CODE = "RAPJMDCFQ"
GENERAL_CODE = "BRDMF"
