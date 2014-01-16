import os
from django.conf import settings
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
    poster = models.ImageField(upload_to='posters', blank=True, max_length=200)

    def __unicode__(self):
        return self.title

    def get_movie_metadata(self):
        """
        Gets the movie metadata from the OMDb API (http://www.omdbapi.com/)
        """
        movie = omdb.title(self.title, tomatoes=True)
        if movie:
            print movie
            self.year = movie.year[:4]
            self.genre = movie.genre
            self.imdb_rating = movie.imdb_rating
            self.imdb_id = movie.imdb_id
            if movie.runtime != "N/A":
                self.runtime = movie.runtime.split(" ")[0]
            self.plot = movie.plot
            if "http" in movie.poster:
                poster_data = requests.get(movie.poster)
                file_extension = os.path.splitext(movie.poster)[1]
                self.poster.save(
                    slugify(self.title) + file_extension,
                    ContentFile(poster_data.content),
                )
            self.save()

    def poster_url(self):
        if not self.poster:
            return None
        return self.poster.url

    def imdb_link(self):
        """
        Returns the link to the IMDB movie page based on the IDMB ID from the database
        """
        return "http://www.imdb.com/title/{0}/reference".format(self.imdb_id)
