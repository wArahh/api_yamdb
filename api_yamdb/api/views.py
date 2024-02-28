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


class CreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    pass


class SignUpViewSet(CreateViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = SignUpSerializer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'access': str(refresh.access_token),
    }


class GetTokenViewSet(APIView):
    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        User = get_user_model()
        serializer.is_valid()
        user = User.objects.get(username=serializer.data['username'])
        return Response(get_tokens_for_user(user))
