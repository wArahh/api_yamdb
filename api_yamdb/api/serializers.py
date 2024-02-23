from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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
        send_email(to_email=validated_data['email'], code=confirmation_code)
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['confirmation_code'] = user.confirmation_code
        del token['password']

        return token
