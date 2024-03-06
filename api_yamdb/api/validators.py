from django.db.models import Q
from rest_framework.serializers import ValidationError


EMAIL_EXISTS = 'Email уже существует'
USERNAME_EXISTS = 'Username уже существует'


def email_or_username_exists_or_free_validator(username, email, user_model):
    if (
        user_model.objects
        .filter(
            Q(username=username) & ~Q(email=email)
        )
        .exists()
    ):
        raise ValidationError(
            USERNAME_EXISTS
        )

    if (
        user_model.objects
        .filter(
            Q(email=email) & ~Q(username=username)
        )
        .exists()
    ):
        raise ValidationError(
            EMAIL_EXISTS
        )
