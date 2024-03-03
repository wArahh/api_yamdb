from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import AccessToken
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from reviews.models import Review, Comments, Category, Genre, Title, User
from django.db.models import Avg

from .filters import GenreCategoryFilter
from .exceptions import PutMethodError
from .mixins import RCPermissions, CDLMixin, CreateViewSet
from .permissions import IsAdminOrReadOnly, AdminOnly, IsAuthorOrAdminOrModerator
from .serializers import (
    ReviewSerializer,
    CommentSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    SignUpSerializer,
    GetTokenSerializer,
    UsersSerializer,
    TitleGetSerializer,
)


class ReviewViewSet(RCPermissions):
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    http_method_names = ('get', 'post', 'patch', 'delete',)
    queryset = Review.objects.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=get_object_or_404(
                Title, id=self.kwargs.get('title_id')
            )
        )


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrAdminOrModerator,)
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    http_method_names = ('get', 'post', 'patch', 'delete',)
    queryset = Comments.objects.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class CategoryViewSet(CDLMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CDLMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score')).all()
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete',)
    filter_backends = (
        DjangoFilterBackend,
        GenreCategoryFilter,
    )
    filterset_fields = ('name', 'year', 'category__slug', 'genre__slug',)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleGetSerializer
        return TitleSerializer


class SignUpViewSet(CreateViewSet):
    @action(
        methods=['post'],
        detail=False,
        url_path='signup',
        permission_classes=[AllowAny,]
    )
    def signup(self, request):
        if not User.objects.filter(**request.data).exists():
            serializer = SignUpSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        user = User.objects.get(**request.data)
        serializer = SignUpSerializer(
            data=request.data, instance=user, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
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
    serializer_class = UsersSerializer
    queryset = User.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated, AdminOnly)
    lookup_field = 'username'

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            raise PutMethodError()
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
