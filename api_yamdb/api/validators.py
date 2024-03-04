import re

from django.conf import settings
from django.core.exceptions import ValidationError

INCORRECT_USERNAME = 'Имя {name} - недопустимо. Введите другое имя'
BAD_USERNAME = 'Неверный формат имени'


def username_validator(username):
    if not re.match(r'^[\w.@+-]+\Z', username):
        raise ValidationError(BAD_USERNAME)
    if username in settings.INVALID_USERNAME_CHARACTERS:
        raise ValidationError(INCORRECT_USERNAME.format(name=username))
