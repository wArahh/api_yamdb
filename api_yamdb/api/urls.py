from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    signup,
    TitleViewSet,
    token,
    UsersViewSet
)

router_v1 = SimpleRouter()
router_v1.register(
    r'titles',
    TitleViewSet,
    basename='titles'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='review'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment'
)
router_v1.register(
    r'users',
    UsersViewSet,
    basename='users'
)

router_v1.register(
    r'categories',
    CategoryViewSet,
    basename='categories'
)

router_v1.register(
    r'genres',
    GenreViewSet,
    basename='genres'
)
auth_urls = ([
    path('signup/', signup, name='signup'),
    path('token/', token, name='token'),
], 'auth')

urlpatterns = [
    path('v1/auth/', include(auth_urls)),
    path('v1/', include(router_v1.urls)),
]
