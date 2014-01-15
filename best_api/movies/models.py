from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=200)
    year = models.IntegerField()
    genre = models.CharField(max_length=40)
    poster = models.ImageField(upload_to='posters', blank=True)
