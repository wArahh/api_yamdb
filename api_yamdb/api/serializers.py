from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers
from django.conf import settings

from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.validators import username_validator


INCORRECT_YEAR = ('Нельзя добавлять произведение,'
                  ' которое ещё не вышло!')
SCORE_VALIDATE = (f'Оценка не может быть ниже '
                  f'{settings.MIN_SCORE} '
                  f'и выше '
                  f'{settings.MAX_SCORE}')
REPEAT_REVIEW = 'Нельзя создать два ревью на одно произведение'
STATUS_MYSELF = 'Вы не можете присвоить себе статус'


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    score = serializers.IntegerField(
        validators=[MinValueValidator(settings.MIN_SCORE),
                    MaxValueValidator(settings.MAX_SCORE)]
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

    def validate(self, review):
        request = self.context['request']
        if request.method != 'POST':
            return review
        if Review.objects.filter(
            title=self.context['view'].kwargs.get('title_id'),
            author=request.user
        ).exists():
            raise ValidationError(REPEAT_REVIEW)
        return review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
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
        required=True, max_length=settings.USERNAME_MAX_LENGTH,
        validators=[username_validator]
    )
    email = serializers.EmailField(
        required=True, max_length=settings.EMAIL_MAX_LENGTH
    )


class GetTokenSerializer(serializers.Serializer):
    confirmation_code = serializers.CharField(
        required=True, max_length=settings.CONFIRMATION_CODE_LENGTH
    )
    username = serializers.CharField(
        required=True, max_length=settings.USERNAME_MAX_LENGTH,
        validators=(username_validator,)
    )


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


class UsersForUserSerializer(UsersSerializer):
    class Meta(UsersSerializer.Meta):
        read_only_fields = ('role',)
