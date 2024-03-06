from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets, mixins
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Comments, Genre, Review, Title, User
from .filters import GenreCategoryFilter
from .permissions import (
    AdminOnly,
    IsAdminOrReadOnly,
    IsAuthorOrAdminOrModerator
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    GetTokenSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleGetSerializer,
    TitleSerializer,
    UsersSerializer,
    UsersForUserSerializer
)
from .utils import get_confirmation_code, send_email
from .validators import (
    email_or_username_exists_or_free_validator
)


INVALID_CONFIRMATION_CODE = (
    'Неверный код подтверждения!'
    'Пройдите процедуру получения кода заново.'
)


class CategoryGenre(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    http_method_names = ('get', 'post', 'patch', 'delete',)
    permission_classes = (IsAuthorOrAdminOrModerator,)

    def get_queryset(self):
        return Review.objects.filter(
            title=get_object_or_404(
                Title,
                id=self.kwargs.get('title_id')
            )
        )

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=get_object_or_404(
                Title,
                id=self.kwargs.get('title_id')
            )
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrAdminOrModerator,)
    pagination_class = PageNumberPagination
    http_method_names = ('get', 'post', 'patch', 'delete',)

    def get_queryset(self):
        return Comments.objects.filter(
            review=get_object_or_404(
                Review,
                id=self.kwargs.get('review_id')
            )
        )

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class CategoryViewSet(CategoryGenre):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenre):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score')).all()
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    http_method_names = ('get', 'post', 'patch', 'delete',)
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
        GenreCategoryFilter,
    )
    filterset_fields = ('name', 'year', 'category__slug', 'genre__slug',)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleGetSerializer
        return TitleSerializer


@api_view(http_method_names=['POST'])
@permission_classes(permission_classes=[AllowAny])
def signup(request):
    confirmation_code = get_confirmation_code()
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    username = data['username']
    email = data['email']
    email_or_username_exists_or_free_validator(
        username=username, email=email, user_model=User
    )
    user, _ = User.objects.get_or_create(**data)
    user.confirmation_code = confirmation_code
    user.save()
    send_email(to_email=user.email, code=confirmation_code)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=['POST'])
@permission_classes(permission_classes=[AllowAny])
def token(request):
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    user = get_object_or_404(User, username=data['username'])
    if user.confirmation_code != data['confirmation_code']:
        user.confirmation_code = None
        user.save()
        raise ValidationError(
            INVALID_CONFIRMATION_CODE
        )
    access_token = AccessToken.for_user(user)
    user.confirmation_code = None
    user.save()
    return Response(
        {'token': str(access_token)},
        status=status.HTTP_200_OK
    )


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (AdminOnly,)
    pagination_class = PageNumberPagination
    http_method_names = ('get', 'post', 'patch', 'delete',)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated,)
    )
    def get_current_user_info(self, request):
        if request.method == 'PATCH':
            serializer = UsersForUserSerializer(
                request.user,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(UsersForUserSerializer(request.user).data)
