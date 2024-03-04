from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Comments, Genre, Review, Title, User
from .filters import GenreCategoryFilter
from .mixins import CreateViewSet, CategoryGenreMixin
from .permissions import (AdminOnly, IsAdminOrReadOnly,
                          IsAuthorOrAdminOrModerator)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetTokenSerializer,
                          ReviewSerializer, SignUpSerializer,
                          TitleGetSerializer, TitleSerializer, UsersSerializer)
from .utils import get_confirmation_code, send_email


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


class CategoryViewSet(CategoryGenreMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreMixin):
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


class AuthViewSet(CreateViewSet):
    @action(
        methods=['post'],
        detail=False,
        url_path='signup',
        permission_classes=(AllowAny,)
    )
    def signup(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        current_user, _ = User.objects.get_or_create(**data)
        confirmation_code = get_confirmation_code()
        current_user.set_confirmation_code(confirmation_code)
        current_user.save()
        send_email(to_email=current_user.email, code=confirmation_code)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post'],
        detail=False,
        url_path='token',
        permission_classes=[AllowAny]
    )
    def token(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        access_token = AccessToken.for_user(user)
        return Response(
            {'token': str(access_token)},
            status=status.HTTP_200_OK
        )


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (IsAuthenticated, AdminOnly)
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
        serializer = UsersSerializer(request.user)
        if request.method == 'PATCH':
            serializer = UsersSerializer(
                request.user,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.data)
