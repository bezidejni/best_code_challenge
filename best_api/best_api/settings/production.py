import os
from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    '.jukic.me',
    '.jukic.me.',
]

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
