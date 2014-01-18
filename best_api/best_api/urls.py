from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework import routers
from movies import views

admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'movies', views.MovieViewSet)

urlpatterns = patterns('',

    url(r'^api', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', views.MovieList.as_view(), name="movie_list"),
)
