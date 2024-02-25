from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models

CHOICES = (
    ('user', 'пользователь'),
    ('moderator', 'модератор'),
    ('admin', 'администратор'),
)


class User(AbstractUser):
    confirmation_code = models.CharField(max_length=200, blank=True)
    bio = models.TextField(verbose_name='Биография', blank=True, null=True)
    role = models.CharField(choices=CHOICES, default='user', max_length=150)
    password = models.CharField(max_length=255, blank=True, null=True)

    def set_password(self, confirmation_code):
        self.confirmation_code = make_password(confirmation_code)
