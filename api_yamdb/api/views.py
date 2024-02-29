from django.db.models import Avg
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Reviews, Comments, Category, Genre, Title, User

from .exceptions import PutMethodError
from .mixins import RCPermissions, CDLMixin, CreateViewSet
from .permissions import IsAdminOrReadOnly, AdminOnly
from .serializers import (
    ReviewSerializer,
    CommentSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    SignUpSerializer,
    GetTokenSerializer,
    UsersSerializer
)


class ReviewViewSet(RCPermissions):
    queryset = Reviews.objects.all()
    serializer_class = ReviewSerializer


class CommentViewSet(RCPermissions):
    queryset = Comments.objects.all()
    serializer_class = CommentSerializer


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
    queryset = Title.objects.annotate(
        average_score=Avg('rating__score')
    ).all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)


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
