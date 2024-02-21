from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Reviews(models.Model):
    text = models.TextField(verbose_name='Текст', max_length=256)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='Автор',
    )
    score = models.IntegerField(verbose_name='Оценка', validators=[MinValueValidator(1), MaxValueValidator(10)])
    pub_date = models.DateField(verbose_name='Дата публикации', auto_now_add=True)



class Comments(models.Model):
    text = models.TextField(verbose_name='Текст', max_length=256)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comment',
        verbose_name='Автор',
    )
    pub_date = models.DateField(verbose_name='Дата публикации', auto_now_add=True)


class Title(models.Model):
    name = models.CharField(verbose_name='Имя произведения', max_length=20)
    # year =
    rating = models.FloatField(verbose_name='Рейтинг', validators=[MinValueValidator(1), MaxValueValidator(10)])
    description = models.TextField(verbose_name='Описание', max_length=256)
    # genre =
    # category =
