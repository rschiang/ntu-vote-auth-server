# -*- coding: utf-8 -*-

"""
Django settings for core project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Update configurations from local settings if applicable
if 'SETTINGS_FILE' in os.environ:
    import json
    with open(os.environ['SETTINGS_FILE']) as f:
        os.environ.update(json.load(f))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('APP_SECRET_KEY', 'LoremIpsum')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = False
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'rest_framework',
    'core',
    'account',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
#    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'core.urls'

WSGI_APPLICATION = 'core.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Enable the use of external database
# You may install additional dependencies like this:
#     apt-get install python3-dev libpq-dev
#     pip install psycopg2

if os.environ.get('DATABASE_USER'):
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DATABASE_NAME', 'vote'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST', ''),
        'PORT': os.environ.get('DATABASE_PORT', ''),
    }

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'zh-tw'
TIME_ZONE = 'Asia/Taipei'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

# Logging
from .log import LOGGING_DIR, LOGGING

# API declarations
API_VERSION = '3'

# App configurations
API_KEY = os.environ.get('VOTE_API_KEY', 'test_api_key')
ACA_API_USER = os.environ.get('ACA_API_USER')
ACA_API_PASSWORD = os.environ.get('ACA_API_PASSWORD')
ACA_API_URL = os.environ.get('ACA_API_URL')

# Callback domain
CALLBACK_DOMAIN = os.environ.get('CALLBACK_DOMAIN')

# Security enforcements
ENFORCE_CARD_VALIDATION = True
ENFORCE_EVENT_DATE = (os.environ.get('ENFORCE_EVENT') == '1')

# Session
SESSION_MAX_RESPOND_TIME = os.environ.get('SESSION_MAX_RESPOND_TIME', 60)
SESSION_EXPIRE_TIME = os.environ.get('SESSION_EXPIRE_TIME', 6000)

# Meta
# All election meta information
from .meta import *
