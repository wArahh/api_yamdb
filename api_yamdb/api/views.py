from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import *

from .mixins import *
from .permissions import *
from .serializers import *


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


class GenreViewSet(CDLMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitleSerializer
    queryset = Title.objects.annotate(
        average_score=Avg('rating__score')
    ).all()
    permission_classes = (IsAdminOrReadOnly,)


class SignUpViewSet(CreateViewSet):

    @action(
        methods=['post'],
        detail=False,
        url_path='signup',
        permission_classes=[permissions.AllowAny]
    )
    def signup(self, request):
        User = get_user_model()
        if not User.objects.filter(**request.data).exists():
            serializer = SignUpSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        user = User.objects.get(**request.data)
        serializer = SignUpSerializer(data=request.data, instance=user, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post'],
        detail=False,
        url_path='token',
        permission_classes=[permissions.AllowAny]
    )
    def token(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        access_token = AccessToken.for_user(user)
        return Response({'token': str(access_token)}, status=status.HTTP_200_OK)


class UsersViewSet(viewsets.ModelViewSet):
    serializer_class = UsersSerializer
    queryset = get_user_model().objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    pagination_class = PageNumberPagination
    permission_classes = (permissions.IsAuthenticated, AdminOnly)
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
