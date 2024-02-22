from django.urls import include, path
from rest_framework.routers import SimpleRouter, DefaultRouter
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

router = DefaultRouter()
router.register(r"v1/categories", CategoryViewSet, basename="categories")
router.register(r"v1/genres", GenreViewSet, basename="genres")

urlpatterns = [
    path('', include(router.urls)),
    path('v1/', include(router_v1.urls)),
]
