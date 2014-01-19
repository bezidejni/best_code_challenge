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

	var requestData = {page_size: 50};
	Movies.getList(requestData)
		.success(function(data) {
			$scope.movies = data.results;
			angular.forEach($scope.movies, function(movie, index){
				movie.tags = movie.genre.split(',');
			});
		});

}]);