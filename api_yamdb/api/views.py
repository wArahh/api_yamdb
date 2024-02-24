from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import *
from .serializers import *


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Reviews.objects.all()
    serializer_class = ReviewSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comments.objects.all()
    serializer_class = CommentSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer


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
