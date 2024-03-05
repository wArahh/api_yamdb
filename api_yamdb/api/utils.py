import random

from django.conf import settings
from django.core.mail import send_mail as send


def get_confirmation_code():
    return ''.join(
        random.choices(
            settings.CONFIRMATION_CODE_CHARACTERS,
            k=settings.CONFIRMATION_CODE_LENGTH
        )
    )


def send_email(to_email, code):
    send(
        subject='Код для получения токена',
        message=f'Ваш код для получения токена: {code}',
        from_email=settings.YAMDB_EMAIL,
        recipient_list=[to_email]
    )
