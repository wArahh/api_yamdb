from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import *

from .views import *

router_v1 = SimpleRouter()
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
    r'titles',
    TitleViewSet,
    basename='title'
)
router_v1.register(
    r'auth',
    SignUpViewSet,
    basename='signup'
)
router_v1.register(
    r"categories",
    CategoryViewSet,
    basename="categories"
)
router_v1.register(
    r"genres",
    GenreViewSet,
    basename="genres"
)
router_v1.register(
    r'users',
    UsersViewSet,
    basename='users'
)
urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
