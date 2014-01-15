from django.core.management.base import BaseCommand, CommandError
from movies.utils import import_movies_from_csv


class Command(BaseCommand):
    args = '<csv_file>'
    help = 'Imports movie data from csv file'

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("Wrong number of arguments, the command expects only the csv file path")

        path = args[0]
        new_movies = import_movies_from_csv(path)
        self.stdout.write("{0} new movies imported".format(new_movies))
