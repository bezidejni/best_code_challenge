from rest_framework import filters, viewsets
from django.views.generic import DetailView, TemplateView
from .models import Movie, MovieFilter
from .serializers import MovieSerializer


class HomepageView(TemplateView):
    template_name = "movie_list.html"


class MovieDetail(DetailView):
    model = Movie
    template_name = "movie_detail.html"

    def get(self, request, *args, **kwargs):
        # Saves the ID of the "seen" movie in the session
        movies_seen = request.session.get('movies_seen', set())
        movies_seen.add(kwargs['pk'])
        request.session['movies_seen'] = movies_seen
        return super(MovieDetail, self).get(request, *args, **kwargs)


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    filter_backends = [filters.DjangoFilterBackend, filters.OrderingFilter]
    filter_class = MovieFilter
    ordering_fields = ('title', 'year')
    paginate_by_param = 'page_size'
    paginate_by = 10
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
