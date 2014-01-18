from rest_framework import viewsets
from django.views.generic import ListView
from .models import Movie
from .serializers import MovieSerializer


class MovieList(ListView):
    template_name = "index.html"
    queryset = Movie.objects.all()
    paginate_by = 10
    context_object_name = "movies"


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
