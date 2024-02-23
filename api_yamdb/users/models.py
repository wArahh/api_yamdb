from django.contrib.auth.models import AbstractUser
from django.db import models

CHOICES = (
    ('user', 'пользователь'),
    ('moderator', 'модератор'),
    ('admin', 'администратор'),
)


class User(AbstractUser):
    confirmation_code = models.CharField(unique=True, max_length=200)
    bio = models.TextField(verbose_name='Биография', blank=True, null=True)
    role = models.CharField(choices=CHOICES, default='user', max_length=150)
