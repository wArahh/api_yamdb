from rest_framework import mixins, viewsets, filters
from .permissions import IsAdminOrReadOnly
from rest_framework.pagination import PageNumberPagination


class CategoryGenreMixin(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
