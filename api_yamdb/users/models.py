from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models

USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'

CHOICES = (
    (USER, 'пользователь'),
    (MODERATOR, 'модератор'),
    (ADMIN, 'администратор'),
)


class User(AbstractUser):
    confirmation_code = models.CharField(verbose_name='код подтверждения', max_length=200, blank=True)
    bio = models.TextField(verbose_name='биография', blank=True, null=True)
    role = models.CharField(verbose_name='роль', choices=CHOICES, default=USER, max_length=150)
    password = models.CharField(max_length=255, blank=True, null=True)

    def set_password(self, confirmation_code):
        self.confirmation_code = make_password(confirmation_code)

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
