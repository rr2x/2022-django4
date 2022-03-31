from django.db import models
from django.contrib.auth.models import AbstractUser


# best practice is to define a custom User model at the beginning of project
# so that you don't need to drop the database in case you need to swap user class in future
# the following is a good placeholder:
#
#   class User(AbstractUser):
#      pass

class User(AbstractUser):
    email = models.EmailField(unique=True)
