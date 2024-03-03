import re
from .exceptions import EmailExistsError

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from reviews.models import Review, Comments, Category, Genre, Title, User


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


class SignUpSerializer(serializers.Serializer):
    role = serializers.HiddenField(default='user')
    username = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True, max_length=254)

    class Meta:
        fields = ('email', 'username', 'role')

    def validate_username(self, username):
        if not re.match(r'^[\w.@+-]+\Z', username) or username.lower() == 'me':
            raise serializers.ValidationError(
                'Некорректное значение поля username'
            )
        return username

    def validate(self, data):
        email = data['email']
        username = data['username']
        if (
            User.objects.filter(email=email).exists()
            and not User.objects.filter(username=username).exists()
        ):
            raise serializers.ValidationError(
                'Email уже существует'
            )
        if (
            User.objects.filter(username=username).exists()
            and not User.objects.filter(email=email).exists()
        ):
            raise serializers.ValidationError(
                'Username уже существует'
            )

        return data


class GetTokenSerializer(serializers.Serializer):
    confirmation_code = serializers.CharField(required=True, max_length=20)
    username = serializers.CharField(required=True, max_length=150)

    class Meta:
        fields = ('confirmation_code', 'username')

    def validate(self, data):
        username = data['username']
        confirmation_code = data['confirmation_code']
        user = get_object_or_404(User, username=username)
        if not user.check_confirmation_code(confirmation_code):
            raise serializers.ValidationError(
                'Неверный код подтверждения!'
            )
        user.confirmation_code = None
        user.save()
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
