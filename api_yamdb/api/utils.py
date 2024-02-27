import random

from django.contrib.auth import get_user_model
from django.core.mail import send_mail as send


def get_confirmation_code():
    code = ''
    while (
        len(code) != 20
    ):
        code += str(random.randint(0, 9))

    return code


def send_email(to_email, code):
    send(
        subject='Код для получения токена',
        message=f'Ваш код для получения токена: {code}',
        from_email='from@example.com',
        recipient_list=[f'{to_email}']
    )
