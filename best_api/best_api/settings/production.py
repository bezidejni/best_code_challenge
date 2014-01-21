import os
from .base import *

DEBUG = True

ALLOWED_HOSTS = [
    '.jukic.me',
    '.jukic.me.',
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'best_api'
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'best_api',
        'USER': 'api',
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

THIRD_PARTY_APPS += (
    'django_extensions',
)

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS
