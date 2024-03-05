from datetime import datetime
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api_yamdb.settings import MIN_SCORE, MAX_SCORE

User = get_user_model()


def current_year():
    return datetime.now().year


class NamedSlug(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=150,
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=50,
        unique=True,
    )

    class Meta:
        abstract = True
        ordering = ('slug',)

    def __str__(self):
        return self.name


class AuthoredText(models.Model):
    text = models.TextField(
        verbose_name='Текст',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='textauthor'
    )
    pub_date = models.DateField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        abstract = True
        ordering = ('pub_date',)


class Category(NamedSlug):
    class Meta(NamedSlug.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(NamedSlug):
    class Meta(NamedSlug.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=150,
    )
    year = models.IntegerField(
        verbose_name='Год',
        validators=[MaxValueValidator(current_year())]
    )
    description = models.TextField(
        verbose_name='Описание',
        max_length=256,
        null=True,
        blank=True,
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Категория',
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        default_related_name = 'titles'

    def __str__(self):
        return self.name[:15]


class Review(AuthoredText):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    score = models.IntegerField(
        verbose_name='Оценка',
        validators=[MinValueValidator(MIN_SCORE),
                    MaxValueValidator(MAX_SCORE)],
    )

    class Meta(AuthoredText.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'
        constraints = (models.UniqueConstraint(
            fields=('title', 'author'),
            name='unique_review'
        ),)

    def __str__(self):
        return self.title


class Comments(AuthoredText):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв',
        related_name='review'
    )

    class Meta(AuthoredText.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.name[:15]
