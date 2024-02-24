import random

from django.contrib.auth import get_user_model
from django.core.mail import send_mail as send


def get_confirmation_code():
    User = get_user_model()
    code = ''
    while (
        len(code) != 20 and not User.objects.filter(confirmation_code=code).exists()
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
