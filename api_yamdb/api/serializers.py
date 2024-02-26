import datetime as dt

from django.contrib.auth import get_user_model
from rest_framework import exceptions, serializers
from rest_framework.settings import api_settings
from rest_framework.validators import UniqueTogetherValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import *

from .utils import get_confirmation_code, send_email

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
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    year = serializers.SerializerMethodField()
    genre = GenreSerializer(many=True)

    class Meta:
        fields = '__all__'
        model = Title


class SignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('email', 'username')
        validators = [
            UniqueTogetherValidator(
                queryset=get_user_model().objects.all(),
                fields=('email', 'username',),
            )
        ]

    def create(self, validated_data):
        confirmation_code = get_confirmation_code()
        User = get_user_model()
        user = User(**validated_data)
        user.set_password(confirmation_code)
        user.save()
        send_email(to_email=validated_data['email'], code=confirmation_code)
        return user


class GetTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('confirmation_code', 'username')
        # extra_kwargs = {'confirmation_code': {'write_only': True}}

    def validate(self, data):
        User = get_user_model()
        user = User.objects.get(username=data['username'])
        if user.confirmation_code != data['confirmation_code']:
            raise serializers.ValidationError(
                'Не верный код'
            )
        return data

    def validate_year(self, value):
        year = dt.date.today().year
        if not (value <= year):
            raise serializers.ValidationError(INCORRECT_YEAR)
        return value
