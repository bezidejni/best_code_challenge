import os
from django.conf import settings
from .models import Movie


def import_movies_from_csv(path='movies.csv'):
    if not os.path.isabs(path):
        path = os.path.join(settings.BASE_DIR, path)
    new_movies_imported = 0
    for line in open(path):
        line = line.strip()
        movie_id, movie_title = line.split(",", 1)
        movie_title = normalize_movie_name(movie_title)
        movie, created = Movie.objects.get_or_create(id=int(movie_id), title=movie_title)
        if created:
            new_movies_imported += 1
    return new_movies_imported


def normalize_movie_name(title):
    title = title.strip()
    if ", " in title:
        title = title.split(", ")
        title = title[1] + " " + title[0]
    return title
