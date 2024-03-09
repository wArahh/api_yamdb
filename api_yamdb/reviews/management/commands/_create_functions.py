import os
import sqlite3

from django.conf import settings

from reviews.models import User, Category


def create_title_genre(datas, model=None):
    url = os.path.join(settings.BASE_DIR, 'db.sqlite3')
    con = sqlite3.connect(url)
    cur = con.cursor()
    data_list = [
        tuple(data.values())
        for data in datas
    ]
    cur.executemany(
        'INSERT INTO reviews_title_genre VALUES(?, ?, ?);', data_list
    )
    con.commit()
    con.close()


def universal_bulk_create(datas, model):
    model.objects.bulk_create(
        model(**data)
        for data in datas
    )


def create_titles(datas, model):
    for data in datas:
        data = dict(data)
        cat_id = data.pop('category')
        category = Category.objects.get(id=cat_id)
        data['category'] = category
        model.objects.create(**data)


def create_reviews_comments(datas, model):
    for data in datas:
        data = dict(data)
        author_id = data.pop('author')
        author = User.objects.get(id=author_id)
        data['author'] = author
        model.objects.create(**data)
