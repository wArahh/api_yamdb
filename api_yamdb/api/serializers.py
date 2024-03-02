from .exceptions import UserNotExistsError, EmailExistsError

import datetime as dt

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from reviews.models import Review, Comments, Category, Genre, Title, User

from .utils import get_confirmation_code, send_email

INCORRECT_YEAR = ('Нельзя добавлять произведение,'
                  ' которое ещё не вышло!')
ZERO_SCORE = 'Оценка не может быть ниже нуля!'
MORE_TEN_SCORE = 'Оценка не может быть выше десяти!'
REPEAT_REVIEW = 'Нельзя создать два ревью на одно произведение'


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Review

    def validate_score(self, value):
        if value < 0:
            raise serializers.ValidationError(ZERO_SCORE)
        if value > 10:
            raise serializers.ValidationError(MORE_TEN_SCORE)
        return value

    def validate(self, data):
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')
        user = request.user
        review = Review.objects.filter(title=title_id, author=user).exists()
        if review and request.method == 'POST':
            raise ValidationError(REPEAT_REVIEW)
        return data


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comments
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'name',
            'slug',
        )
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Genre


class TitleGetSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer()
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category',
        )


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = (
            'name', 'year', 'description', 'genre', 'category',
        )

    def to_representation(self, title):
        serializer = TitleGetSerializer(title)
        return serializer.data


class SignUpSerializer(serializers.ModelSerializer):
    role = serializers.HiddenField(default='user')

    class Meta:
        model = User
        fields = ('email', 'username', 'role')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True}
        }
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
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
        user = User(**validated_data)
        user.set_confirmation_code(confirmation_code)
        user.save()
        send_email(to_email=validated_data['email'], code=confirmation_code)
        return user

    def update(self, instance, validated_data):
        confirmation_code = get_confirmation_code()
        instance.set_confirmation_code(confirmation_code)
        send_email(to_email=instance.email, code=confirmation_code)
        instance.save()
        print(f'code from update: {confirmation_code}')
        return instance


class GetTokenSerializer(serializers.Serializer):
    confirmation_code = serializers.CharField(required=True)
    username = serializers.CharField(required=True)

    class Meta:
        fields = ('confirmation_code', 'username')

    def validate(self, data):
        username = data['username']
        confirmation_code = data['confirmation_code']
        if not User.objects.filter(username=username).exists():
            raise UserNotExistsError()
        user = User.objects.get(username=username)

        if not user.check_confirmation_code(confirmation_code):
            raise serializers.ValidationError(
                'Неверный код подтверждения!'
            )

        return user


class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'confirmation_code': {'required': False},
            'role': {'default': 'user'}
        }
        validators = [
            UniqueTogetherValidator(
                queryset=get_user_model().objects.all(),
                fields=('email', 'username',),
            )
        ]

    def validate_role(self, role):
        user = self.context['request'].user
        if (
            role != 'user'
            and not user.is_admin
            and not user.is_superuser
        ):
            raise serializers.ValidationError(
                'Вы не можете присвоить себе статус'
            )
        return role

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise EmailExistsError()
        return email
