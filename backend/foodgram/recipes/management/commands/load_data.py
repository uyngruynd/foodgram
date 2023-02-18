import logging
from csv import DictReader

from django.core.management import BaseCommand

from recipes.models import Ingredient

files_to_download = {
    Ingredient: '../../data/ingredients.csv',
}
logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    """Загрузка данных из csv в таблицы моделей проекта."""
    help = 'Загрузка данных из .csv в модели проекта.'

    def handle(self, *args, **options):
        for model, file in files_to_download.items():
            logging.info(
                f'Загрузка данных из файла {file} в модель {model}...')

            for row in DictReader(open(f'{file}')):
                try:
                    obj = model(**row)
                    obj.save()
                except Exception as err:
                    logging.info(
                        f'Не загружена строка c данными {row.values()} '
                        f'по причине - {err}')
        logging.info('Загрузка данных завершена!')
