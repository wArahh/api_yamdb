from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework import filters, viewsets, mixins, permissions, status
from django_filters.rest_framework import DjangoFilterBackend

from .permissions import IsAdminOrReadOnly, IsAuthorOrAdmin
from reviews.models import *
from .serializers import *
from .utils import *


class ReviewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Reviews.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthorOrAdmin]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]


class CommentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Comments.objects.all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthorOrAdmin]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]


class CreateListDestroyViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    lookup_field = 'slug'


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer


def get_tokens_for_user(user):
    refresh = AccessToken.for_user(user)

    return {
        'token': str(refresh),
    }


class CreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    pass


class ListCreateViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    pass


class SignUpViewSet(CreateViewSet):

    @action(methods=['post'], detail=False, url_path='signup', permission_classes=[permissions.AllowAny])
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

    @action(methods=['post'], detail=False, url_path='token', permission_classes=[permissions.AllowAny])
    def token(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response(get_tokens_for_user(user))


class UsersViewSet(ListCreateViewSet):
    serializer_class = UsersSerializer
    queryset = get_user_model().objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    pagination_class = PageNumberPagination
    permission_classes = (permissions.AllowAny,)




