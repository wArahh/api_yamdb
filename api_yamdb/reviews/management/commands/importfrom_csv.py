import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from . import _create_functions
from reviews.models import User, Genre, Category, Title, Review, Comments

csv_names_model_function = (
    ('users', User, False),
    ('genre', Genre, False),
    ('category', Category, False),
    ('titles', Title, _create_functions.create_titles),
    ('genre_title', None, _create_functions.create_title_genre),
    ('review', Review, _create_functions.create_reviews_comments),
    ('comments', Comments, _create_functions.create_reviews_comments)
)


def run_populating():
    for csv_name, model, func in csv_names_model_function:
        url_to_csv_file = os.path.join(
            settings.BASE_DIR, f'static/data/{csv_name}.csv'
        )
        print(f'Подготовка модели {csv_name}...', end=' ')
        with open(url_to_csv_file, 'r', encoding="utf8") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            if not func:
                _create_functions.universal_bulk_create(
                    datas=csv_reader, model=model
                )
            else:
                func(datas=csv_reader, model=model)
        print('(ok)')


class Command(BaseCommand):
    help = 'This command populates the database'

    def handle(self, *args, **options):
        try:
            print('START!')
            run_populating()
            print('FINISH!')
        except Exception as error:
            raise Exception(error)
