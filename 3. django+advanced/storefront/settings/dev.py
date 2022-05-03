from .common import *


DEBUG = True

SECRET_KEY = 'django-insecure-p67g=kdh*j8zn58qlb8keeyo^uf$*fe81rcwgmftmpholdquhh'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'storefront3',
        'HOST': 'mysql',  # 'localhost' changed to service 'mysql' from docker
        'USER': 'root',
        'PASSWORD': 'bngflkngfgN%#$%gefbTUHYTRUJY42134^%v',
    }
}

# 'localhost' changed to service 'redis' from docker
CELERY_BROKER_URL = 'redis://redis:6379/1'

# for redis caching
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        # we are using database #2 because we used it previously on celery broker
        # '127.0.0.1' changed to service 'redis' from docker
        "LOCATION": "redis://redis:6379/2",
        'TIMEOUT': 10*60,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# 'localhost' changed to service 'smtp4dev' from docker
EMAIL_HOST = 'smtp4dev'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 2525
DEFAULT_FROM_EMAIL = 'from@test.com'

# to enable debug toolbar on docker
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: True
}
