import os
import dj_database_url
from .common import *

DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['djangobuy-prod.herokuapp.com']

DATABASES = {
    'default': dj_database_url.config()
}

REDIS_URL = os.environ['REDIS_URL']

CELERY_BROKER_URL = REDIS_URL

# for redis caching
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        # we are using database #2 because we used it previously on celery broker
        "LOCATION": REDIS_URL,
        'TIMEOUT': 10*60,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

EMAIL_HOST = os.environ['MAILGUN_SMTP_SERVER']
EMAIL_HOST_USER = os.environ['MAILGUN_SMTP_LOGIN']
EMAIL_HOST_PASSWORD = os.environ['MAILGUN_SMTP_PASSWORD']
EMAIL_PORT = os.environ['MAILGUN_SMTP_PORT']
