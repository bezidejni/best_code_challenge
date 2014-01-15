import os
from django.core.files.base import ContentFile
from django.db import models
from django.template.defaultfilters import slugify
import omdb
import requests


class Movie(models.Model):
    title = models.CharField(max_length=200)
    year = models.IntegerField(null=True, blank=True)
    genre = models.CharField(max_length=40)
    imdb_rating = models.CharField(max_length=3, blank=True)
    imdb_id = models.CharField(max_length=15, blank=True)
    runtime = models.IntegerField(null=True, blank=True)
    plot = models.TextField(blank=True)
    poster = models.ImageField(upload_to='posters', blank=True)

    def __unicode__(self):
        return self.title

    def get_movie_metadata(self):
        movie = omdb.title(self.title, tomatoes=True)
        self.year = movie.year
        self.genre = movie.genre
        self.imdb_rating = movie.imdb_rating
        self.imdb_id = movie.imdb_id
        self.runtime = movie.runtime.split(" ")[0]
        self.plot = movie.plot
        poster_data = requests.get(movie.poster)
        file_extension = os.path.splitext(movie.poster)[1]
        self.poster.save(
            "{0}.{1}".format(slugify(self.title), file_extension),
            ContentFile(poster_data.content)
        )
        self.save()
