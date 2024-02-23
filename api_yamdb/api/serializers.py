from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
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
        validated_data['confirmation_code'] = confirmation_code
        user = get_user_model()
        user.objects.create(**validated_data)
        send_email(to_email=validated_data['email'], code=confirmation_code)
        return user
