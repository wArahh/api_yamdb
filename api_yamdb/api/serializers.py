from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers, exceptions
from rest_framework.fields import CharField
from rest_framework.settings import api_settings
from rest_framework.validators import UniqueTogetherValidator

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import *
from .utils import get_confirmation_code, send_email


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


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = '__all__'


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
