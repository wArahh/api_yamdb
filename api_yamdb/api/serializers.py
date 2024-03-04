from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comments, Genre, Review, Title, User
from .validators import username_validator

INCORRECT_YEAR = ('Нельзя добавлять произведение,'
                  ' которое ещё не вышло!')
SCORE_VALIDATE = 'Оценка не может быть ниже нуля и выше 10'
REPEAT_REVIEW = 'Нельзя создать два ревью на одно произведение'
STATUS_MYSELF = 'Вы не можете присвоить себе статус'
INCORRECT_APPROVE_CODE = 'Неверный код подтверждения!'
EMAIL_EXISTS = 'Email уже существует'
USERNAME_EXISTS = 'Username уже существует'


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    score = serializers.IntegerField(
        validators=[MinValueValidator(1),
                    MaxValueValidator(10)]
    )

    class Meta:
        fields = (
            'id',
            'text',
            'author',
            'score',
            'pub_date'
        )
        model = Review

    def validate(self, data):
        request = self.context['request']
        if request.method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            user = request.user
            review = (Review.objects.filter(
                title=title_id,
                author=user
            ).exists())
            if review:
                raise ValidationError(REPEAT_REVIEW)
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comments
        fields = (
            'id',
            'text',
            'author',
            'pub_date'
        )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'name',
            'slug',
        )
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = (
            'id',
        )
        model = Genre


class TitleGetSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer()
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )
        read_only_fields = fields


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
            'name',
            'year',
            'description',
            'genre',
            'category',
        )

    def to_representation(self, title):
        return TitleGetSerializer(title).data


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True, max_length=settings.USERNAME_MAX_LENGTH, validators=[username_validator]
    )
    email = serializers.EmailField(
        required=True, max_length=settings.EMAIL_MAX_LENGTH
    )

    class Meta:
        fields = (
            'email',
            'username',
        )

    def validate(self, data):
        email = data['email']
        username = data['username']
        if (
            User.objects.filter(email=email).exists()
            and not User.objects.filter(username=username).exists()
        ):
            raise serializers.ValidationError(
                EMAIL_EXISTS
            )
        if (
            User.objects.filter(username=username).exists()
            and not User.objects.filter(email=email).exists()
        ):
            raise serializers.ValidationError(
                USERNAME_EXISTS
            )

        return data


class GetTokenSerializer(serializers.Serializer):
    confirmation_code = serializers.CharField(
        required=True, max_length=settings.CONFIRMATION_CODE_LENGTH
    )
    username = serializers.CharField(
        required=True, max_length=settings.USERNAME_MAX_LENGTH, validators=[username_validator]
    )

    class Meta:
        fields = (
            'confirmation_code',
            'username',
        )

    def validate(self, data):
        username = data['username']
        confirmation_code = data['confirmation_code']
        user = get_object_or_404(User, username=username)
        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError(
                INCORRECT_APPROVE_CODE
            )
        user.confirmation_code = None
        user.save()
        return user


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
