from .common import *


DEBUG = True

SECRET_KEY = 'django-insecure-p67g=kdh*j8zn58qlb8keeyo^uf$*fe81rcwgmftmpholdquhh'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'storefront3',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': 'bngflkngfgN%#$%gefbTUHYTRUJY42134^%v',
    }
}

CELERY_BROKER_URL = 'redis://localhost:6379/1'

# for redis caching
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        # we are using database #2 because we used it previously on celery broker
        "LOCATION": "redis://127.0.0.1:6379/2",
        'TIMEOUT': 10*60,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 2525
DEFAULT_FROM_EMAIL = 'from@test.com'
