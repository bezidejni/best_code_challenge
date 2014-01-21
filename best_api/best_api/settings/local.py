from .base import *

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'best_api'
    }
}

THIRD_PARTY_APPS += (
    'django_extensions',
    'debug_toolbar',
)

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS
