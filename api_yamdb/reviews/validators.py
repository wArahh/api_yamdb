import re

from django.conf import settings
from django.core.exceptions import ValidationError

INCORRECT_USERNAME = 'Имя {name} - недопустимо.'
BAD_USERNAME = (
    'Неверный формат имени. '
    'Запрещенные символы: {characters}'
)


def username_validator(username):
    bad_characters = re.sub(
        settings.USERNAME_PATTERN, '', username
    )
    if bad_characters:
        raise ValidationError(
            BAD_USERNAME.format(
                characters=''.join(set(bad_characters))
            )
        )

    if username in settings.BAD_USERNAME_WORDS:
        raise ValidationError(INCORRECT_USERNAME.format(name=username))

    return username
