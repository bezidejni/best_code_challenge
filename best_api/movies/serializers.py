from rest_framework import serializers
from .models import Movie


class AbsoluteURLFileField(serializers.FileField):
    """
    FileField serializer that shows the absolute URL instead of showing
    relative file path.
    """
    def to_native(self, value):
        request = self.context.get('request', None)
        if value:
            return request.build_absolute_uri(value.url)
        else:
            return None


class MovieSerializer(serializers.HyperlinkedModelSerializer):
    poster = AbsoluteURLFileField()

    class Meta:
        model = Movie
        fields = ('id', 'title', 'year', 'genre', 'imdb_rating', 'imdb_id',
                  'runtime', 'plot', 'poster', 'youtube_video_id')
