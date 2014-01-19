var mevies = angular.module('mevies', []);

mevies.config(function($provide, $windowProvider, $httpProvider) {
    var apiBaseUrl = 'http://movies.jukic.me/api/';

    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

    $provide.value('API_BASE_URL', apiBaseUrl);
    $provide.value('CSRF_TOKEN', $windowProvider.$get().csrfToken);
});

mevies.factory('Movies', ['$http', 'API_BASE_URL', function ($http, API_BASE_URL) {
	return {
		getList: function(params) {
			return $http({
				method: 'GET',
				url: API_BASE_URL + 'movies/',
				params: params
			});
		}
	};
}]);

mevies.controller('MeviesCtrl', ['$scope', 'Movies', function ($scope, Movies) {

	$scope.listView = false;

	var data = {"count": 1682, "next": "http://movies.jukic.me/api/movies/?search=toy+story&page=2&format=json", "previous": null, "results": [{"id": 750, "title": "Amistad", "year": 1997, "genre": "Drama, History, Mystery", "imdb_rating": "7.2", "imdb_id": "tt0118607", "runtime": 155, "plot": "About a 1839 mutiny aboard a slave ship that is traveling towards the northeastern coast of America. Much of the story involves a court-room drama about the free man who led the revolt.", "poster": "http://movies.jukic.me/media/posters/amistad.jpg"}, {"id": 21, "title": "Muppet Treasure Island", "year": 1996, "genre": "Action, Adventure, Comedy", "imdb_rating": "6.8", "imdb_id": "tt0117110", "runtime": 99, "plot": "The Muppets' twist on the classic tale.", "poster": "http://movies.jukic.me/media/posters/muppet-treasure-island.jpg"}, {"id": 26, "title": "The Brothers McMullen", "year": 1995, "genre": "Comedy, Drama, Romance", "imdb_rating": "6.6", "imdb_id": "tt0112585", "runtime": 98, "plot": "Three Irish Catholic brothers from Long Island struggle to deal with love, marriage, and infidelity.", "poster": "http://movies.jukic.me/media/posters/the-brothers-mcmullen.jpg"}, {"id": 30, "title": "Belle de jour", "year": 1967, "genre": "Drama", "imdb_rating": "7.8", "imdb_id": "tt0061395", "runtime": 101, "plot": "A frigid young housewife decides to spend her midweek afternoons as a prostitute.", "poster": "http://movies.jukic.me/media/posters/belle-de-jour.jpg"}, {"id": 32, "title": "Crumb", "year": 1994, "genre": "Documentary, Biography", "imdb_rating": "8.0", "imdb_id": "tt0109508", "runtime": 119, "plot": "An intimate portrait of the controversial cartoonist and his traumatized family.", "poster": "http://movies.jukic.me/media/posters/crumb.jpg"}, {"id": 14, "title": "Il Postino", "year": 2011, "genre": "Drama, Music, Musical", "imdb_rating": "N/A", "imdb_id": "tt2122659", "runtime": 132, "plot": "N/A", "poster": "http://movies.jukic.me/media/posters/il-postino.jpg"}, {"id": 84, "title": "Robert A. Heinlein's The Puppet Masters", "year": null, "genre": "", "imdb_rating": "", "imdb_id": "", "runtime": null, "plot": "", "poster": null}, {"id": 50, "title": "Star Wars", "year": 1983, "genre": "Action, Adventure, Sci-Fi", "imdb_rating": "7.2", "imdb_id": "tt0251413", "runtime": null, "plot": "N/A", "poster": null}, {"id": 45, "title": "Eat Drink Man Woman", "year": 1994, "genre": "Comedy, Romance, Drama", "imdb_rating": "7.8", "imdb_id": "tt0111797", "runtime": 124, "plot": "A senior chef lives with his three grown daughters; the middle one finds her future plans affected by unexpected events and the life changes of the other household members.", "poster": "http://movies.jukic.me/media/posters/eat-drink-man-woman.jpg"}, {"id": 49, "title": "I.Q.", "year": 1994, "genre": "Comedy, Romance", "imdb_rating": "6.2", "imdb_id": "tt0110099", "runtime": 100, "plot": "Albert Einstein helps a young man who's in love with Einstein's niece to catch her attention by pretending temporarily to be a great physicist.", "poster": "http://movies.jukic.me/media/posters/iq.jpg"}]};
	
	angular.forEach($scope.movies, function(movie, index){
		movie.tags = movie.genre.split(',');
	});

	Movies.getList()
		.success(function(data) {
			$scope.movies = data.results;
		});

}]);