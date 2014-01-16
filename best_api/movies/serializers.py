from rest_framework import serializers
from .models import Movie


class MovieSerializer(serializers.HyperlinkedModelSerializer):
    poster = serializers.Field(source='poster_url')

    class Meta:
        model = Movie
        fields = ('id', 'title', 'year', 'genre', 'imdb_rating', 'imdb_id', 'runtime', 'plot', 'poster')
