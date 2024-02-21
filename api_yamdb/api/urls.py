from django.urls import include, path
from rest_framework.routers import SimpleRouter
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


urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
