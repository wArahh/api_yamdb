from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class Review(models.Model):
    title = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    text = models.TextField(
        verbose_name='Текст',
        max_length=256,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    score = models.IntegerField(
        verbose_name='Оценка',
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    pub_date = models.DateField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'

    def __str__(self):
        return self.author.username


class Comments(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )
    text = models.TextField(
        verbose_name='Текст',
        max_length=256,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    pub_date = models.DateField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comment'

    def __str__(self):
        return self.author.username


class Category(models.Model):
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
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
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
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=150,
    )
    year = models.IntegerField(
        verbose_name='Год',
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
        return self.name
