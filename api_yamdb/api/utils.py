import random

from django.conf import settings
from django.core.mail import send_mail as send


def get_confirmation_code():
    code = ''
    for _ in range(settings.CONFIRMATION_CODE_LENGTH):
        code += str(random.randint(0, 9))
    return code


def send_email(to_email, code):
    send(
        subject='Код для получения токена',
        message=f'Ваш код для получения токена: {code}',
        from_email=settings.YAMDB_EMAIL,
        recipient_list=[to_email]
    )
