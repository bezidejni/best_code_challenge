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

mevies.filter('tagsFilter', function() {
	return function(movies, tags) {
		if (!angular.isUndefined(movies) && !angular.isUndefined(tags) && tags.length > 0) {

			var filteredMovies = [];
			angular.forEach(movies, function(movie, key){
				var matches = 0;
				angular.forEach(tags, function(tag, index){
					if (movie.genre.toLowerCase().indexOf(tag) !== -1) matches++;
				});
				if (matches === tags.length) filteredMovies.push(movie);
			});

			return filteredMovies;
		}
		else return movies;
	}
});

mevies.controller('MeviesCtrl', ['$scope', 'Movies', function ($scope, Movies) {

	$scope.listView = false;
	$scope.tagFilters = [];

	var requestData = {page_size: 50};
	Movies.getList(requestData)
		.success(function(data) {
			$scope.movies = data.results;
			angular.forEach($scope.movies, function(movie, index){
				movie.tags = movie.genre.split(',');
			});
		});

	$scope.addTagFilter = function(tag) {
		if ($scope.tagFilters.indexOf(tag.toLowerCase()) == -1) $scope.tagFilters.push(tag.toLowerCase());
	}

	$scope.removeTagFilter = function(index) {
		console.log(index);
		$scope.tagFilters.splice(index, 1);
	}

}]);