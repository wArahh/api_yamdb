import re

from django.conf import settings
from django.core.exceptions import ValidationError as UsernameError
from rest_framework.serializers import (ValidationError
                                        as SerializerValidationError)

INCORRECT_USERNAME = 'Имя {name} - недопустимо. Введите другое имя'
BAD_USERNAME = 'Неверный формат имени'
INCORRECT_APPROVE_CODE = 'Неверный код подтверждения!'
EMAIL_EXISTS = 'Email уже существует'
USERNAME_EXISTS = 'Username уже существует'
USERNAME_NOT_EXIST = 'Пользователь {name} не найден'


def username_validator(username):
    if not re.match(r'^[\w.@+-]+\Z', username):
        raise UsernameError(BAD_USERNAME)
    if username in settings.INVALID_USERNAME_CHARACTERS:
        raise UsernameError(INCORRECT_USERNAME.format(name=username))


def code_validator(code_a, code_b):
    if code_a != code_b:
        raise SerializerValidationError(INCORRECT_APPROVE_CODE)


def email_exists_and_free_username_validator(username, email, user_model):
    if (
        user_model.objects.filter(email=email).exists()
        and not user_model.objects.filter(username=username).exists()
    ):
        raise SerializerValidationError(
            EMAIL_EXISTS
        )


def username_exists_and_free_email_validator(username, email, user_model):
    if (
        user_model.objects.filter(username=username).exists()
        and not user_model.objects.filter(email=email).exists()
    ):
        raise SerializerValidationError(
            USERNAME_EXISTS
        )
