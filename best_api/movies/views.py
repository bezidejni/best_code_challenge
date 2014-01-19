from rest_framework import filters, viewsets
from django.views.generic import DetailView, ListView
from .models import Movie, MovieFilter
from .serializers import MovieSerializer


class MovieList(ListView):
    context_object_name = "movies"
    paginate_by = 10
    queryset = Movie.objects.all()
    template_name = "movie_list.html"


class MovieDetail(DetailView):
    model = Movie
    template_name = "movie_detail.html"


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    filter_backends = [filters.DjangoFilterBackend, filters.OrderingFilter]
    filter_class = MovieFilter
    ordering_fields = ('title', 'year')
    paginate_by_param = 'page_size'
    paginate_by = 10
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
