import os
import re
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.templatetags.static import static
from apiclient.discovery import build
import django_filters
import imdb
import omdb
import requests


class Movie(models.Model):
    title = models.CharField(max_length=200)
    year = models.IntegerField(null=True, blank=True)
    genre = models.CharField(max_length=100, blank=True)
    imdb_rating = models.CharField(max_length=3, blank=True)
    imdb_id = models.CharField(max_length=15, blank=True)
    youtube_video_id = models.CharField(max_length=20, blank=True)
    runtime = models.IntegerField(null=True, blank=True)
    plot = models.TextField(blank=True)
    director = models.CharField(blank=True, max_length=150)
    writers = models.TextField(blank=True)
    actors = models.TextField(blank=True)
    poster = models.ImageField(upload_to='posters', blank=True, max_length=200)
    slug = models.SlugField(max_length=100)

    class Meta:
        ordering = ['title']

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('movie-detail', kwargs={'pk': self.id})

    def get_movie_metadata_from_omdb(self):
        """
        Gets the movie metadata from the OMDb API (http://www.omdbapi.com/)
        """
        movie = omdb.title(self.title, tomatoes=True)
        if movie:
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

    def get_movie_metadata_from_imdb(self):
        """
        Gets the movie metadata from the IMDb (http://www.imdb.com)
        """
        api = imdb.IMDb()
        movies = api.search_movie(self.title, results=1)
        if movies:
            movie = api.get_movie(movies[0].movieID)
            self.year = movie.get('year')
            self.genre = ", ".join(movie.get('genres', []))
            self.imdb_rating = movie.get("rating", "")
            self.imdb_id = "tt" + movie.movieID
            director = movie.get("director")
            if director:
                self.director = director[0].get("name")
            writers = movie.get("writers")
            if writers:
                writers = [writer.get("name") for writer in writers]
                self.writers = ", ".join(writers)
            actors = movie.get("actors")[:10]
            if actors:
                actors = [actor.get("name") for actor in actors]
                self.actors = ", ".join(actors)
            runtimes = movie.get("runtimes")
            if runtimes:
                # get only digits from string (example UK:112min -> 112)
                self.runtime = int(re.findall('\d+', runtimes[0])[0])
            self.plot = movie.get('plot outline', "")
            poster_url = movie.get('cover url')
            if poster_url:
                poster_data = requests.get(poster_url)
                file_extension = os.path.splitext(poster_url)[1]
                self.poster.save(
                    slugify(self.title) + file_extension,
                    ContentFile(poster_data.content),
                )
            self.save()

    def get_youtube_trailer_video_id(self):
        """
        Uses the Youtube API to try to find a trailer for the movie and
        returns the youtube video ID
        API Documentation:
        https://developers.google.com/youtube/v3/docs/
        https://developers.google.com/api-client-library/python/apis/youtube/v3
        """
        youtube = build("youtube", "v3", developerKey="AIzaSyD8d-NQ8wjfW23ZjQPU2nAwZ0PTMF-gom8")
        response = youtube.search().list(
            q=u"{0} trailer".format(self.title),
            type="video",
            videoDuration="short",
            part="id,snippet"
        ).execute()
        results = response.get("items")
        if results:
            top_item = results[0]
            self.youtube_video_id = top_item["id"]["videoId"]
            self.save()

    def poster_url(self):
        """
        Returns the poster URL or the 'not found' poster
        in case the movie doesn't have one.
        """
        if self.poster:
            return self.poster.url
        else:
            return static("images/default_poster.png")

    def imdb_link(self):
        """
        Returns the link to the IMDB movie page based on the IDMB ID from the database
        """
        return "http://www.imdb.com/title/{0}/reference".format(self.imdb_id)


def get_by_genre(qs, genres):
    """
    Splits the comma separated genre list and filters
    the queryset so it contains all the genres from the list.
    """
    if genres:
        genres = genres.split(",")
        for genre in genres:
            qs = qs.filter(genre__icontains=genre)
    return qs


class MovieFilter(django_filters.FilterSet):
    """
    Filter for movie objects in the API that allows filtering by
    title, genre or year.
    """
    title = django_filters.CharFilter(name="title", lookup_type="icontains")
    genre = django_filters.CharFilter(name="genre", action=get_by_genre)

    class Meta:
        model = Movie
        fields = ['title', 'genre', 'year']
