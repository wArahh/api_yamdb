from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers, exceptions
from rest_framework.fields import CharField
from rest_framework.settings import api_settings
from rest_framework.validators import UniqueTogetherValidator

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import *
from .utils import get_confirmation_code, send_email
from .exceptions import UserNotExistsError

import datetime as dt


INCORRECT_YEAR = ('Нельзя добавлять произведение,'
                  ' которое ещё не вышло!')


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = (
            'text',
            'score',
        )


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ('text',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    year = serializers.SerializerMethodField()
    genre = GenreSerializer(many=True)

    class Meta:
        fields = ("name", "year", "description", "genre", "category")
        model = Title

    def validate_year(self, value):
        year = dt.date.today().year
        if not (value <= year):
            raise serializers.ValidationError(INCORRECT_YEAR)
        return value


class SignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('email', 'username')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True}
        }
        validators = [
            UniqueTogetherValidator(
                queryset=get_user_model().objects.all(),
                fields=('email', 'username',),
            )
        ]

    def validate_username(self, username):
        if username.lower() == 'me':
            raise serializers.ValidationError(
                'Некорректное значение поля username'
            )
        return username

    def validate(self, data):
        User = get_user_model()
        if (
            User.objects.filter(email=data['email']).exists()
            and not User.objects.filter(username=data['username']).exists()
        ):
            raise serializers.ValidationError(
                'Email уже существует'
            )

        return data

    def create(self, validated_data):
        confirmation_code = get_confirmation_code()
        User = get_user_model()
        user = User(**validated_data)
        user.set_password(confirmation_code)
        user.save()
        print(f'data: {user.confirmation_code}={confirmation_code}')
        send_email(to_email=validated_data['email'], code=confirmation_code)
        return user

    def update(self, instance, validated_data):
        confirmation_code = get_confirmation_code()
        instance.set_password(confirmation_code)
        send_email(to_email=instance.email, code=confirmation_code)
        instance.save()
        print(f'update data: {instance.confirmation_code}={confirmation_code}')
        return instance


class GetTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('confirmation_code', 'username')
        extra_kwargs = {
            'confirmation_code': {'required': True},
            'username': {'required': True}
        }

    def validate_username(self, username):
        User = get_user_model()
        if not User.objects.filter(username=username).exists():
            raise UserNotExistsError()
        return username


class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'confirmation_code': {'required': False}
        }
        validators = [
            UniqueTogetherValidator(
                queryset=get_user_model().objects.all(),
                fields=('email', 'username',),
            )
        ]
