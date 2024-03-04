from django.conf import settings
from django.contrib.auth.models import AbstractUser

from api.validators import username_validator

USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'

CHOICES = (
    (USER, 'пользователь'),
    (MODERATOR, 'модератор'),
    (ADMIN, 'администратор'),
)


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
    )
    confirmation_code = models.CharField(
        verbose_name='код подтверждения',
        max_length=settings.CONFIRMATION_CODE_LENGTH,
        blank=True,
        null=True
    )
    bio = models.TextField(
        verbose_name='биография',
        blank=True,
        null=True
    )
    role = models.CharField(
        verbose_name='роль',
        choices=CHOICES,

    )

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    class Meta:
        ordering = ('date_joined',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
