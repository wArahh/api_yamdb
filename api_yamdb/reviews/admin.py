from .models import Category, Genre, Title

admin.site.empty_value_display = "Не задано"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
    )
    list_editable = ("name", "slug")
    search_fields = ("name", "slug")
    list_filter = ("name", "slug")
    list_display_links = ("name",)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
    )
    list_editable = ("name", "slug")
    search_fields = ("name", "slug")
    list_filter = ("name", "slug")
    list_display_links = ("name",)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "year",
        "rating",
        "description",
        "genre",
        "category",
    )
    list_editable = (
        "name",
        "year",
        "description",
        "genre",
        "category",
    )
    search_fields = ("name", "year")
    list_filter = ("name",)
    list_display_links = ("name",)
