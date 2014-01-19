var mevies = angular.module('mevies', ['ui.bootstrap']);

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
		},
		getNextPage: function(url) {
			return $http({
				method: 'GET',
				url: url
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

mevies.controller('MeviesCtrl', ['$scope', '$timeout', '$q', 'Movies', function ($scope, $timeout, $q, Movies) {

	$scope.currentPage = 1;
	$scope.gettingMovies = true;
	$scope.listView = false;
	$scope.tagFilters = [];
	$scope.pages = [];
	$scope.predicate = 'year'
	$scope.reverse = true;

	$scope.getMovies = function(requestData) {
		Movies.getList(requestData)
			.success(function(data) {
				$scope.gettingMovies = false;
				$scope.movies = data;
				angular.forEach($scope.movies.results, function(movie, index){
					movie.tags = movie.genre.split(',');
				});
				$scope.nextPageUrl = data.next;
				$scope.pages = $scope.paginate($scope.movies.results, 24);
				$scope.currentPageView = $scope.pages[$scope.currentPage - 1];
				$scope.totalNumOfMovies = data.count;
			});
	}

	var requestData = {page_size: 240, ordering: '-year'};
	$scope.getMovies(requestData);

	$scope.addTagFilter = function(tag) {
		if ($scope.tagFilters.indexOf(tag.toLowerCase()) == -1) $scope.tagFilters.push(tag.toLowerCase());
	}

	$scope.removeTagFilter = function(index) {
		$scope.tagFilters.splice(index, 1);
	}

	$scope.search = function() {
		// When the search text field is changed this function is fired. We don't want to fire off
		// an ajax request with every change. Rather, let's be a little smart about this and fire
		// off a request if there hasn't been a change within 1.5 seconds.

		// TODO Don't make canceler global.
		if (typeof canceler !== 'undefined') { canceler.resolve(); }

		canceler = $q.defer();

		$timeout.cancel($scope.stopSearch);
		var requestData = {
			title: $scope.searchMovies,
			ordering: (($scope.reverse) ? '-' : '') + $scope.predicate,
			page_size: 240,
			page: 1
		};

		$scope.stopSearch = $timeout(function() {
			$scope.pages = [];
			$scope.currentPage = 1;
			$scope.currentPageView = $scope.pages[$scope.currentPage - 1];
			$scope.gettingMovies = true;
			Movies.getList(requestData, canceler.promise).
				success(function(data) {
					$scope.gettingMovies = false;
					$scope.movies = data;
					angular.forEach($scope.movies.results, function(movie, index){
						movie.tags = movie.genre.split(',');
					});
					$scope.nextPageUrl = data.next;
					$scope.pages.push.apply($scope.pages, $scope.paginate($scope.movies.results, 24));
					$scope.currentPageView = $scope.pages[$scope.currentPage - 1];
				});
		}, 1500);
	};

	$scope.clearSearch = function() {
		$scope.searchMovies = '';
		$scope.pages = [];
		$scope.currentPage = 1;
		$scope.currentPageView = $scope.pages[$scope.currentPage - 1];
		$scope.gettingMovies = true;
		var requestData = {page_size: 240, ordering: '-year'};
		$scope.getMovies(requestData);
	}

	$scope.paginate = function(data, pageSize) {
		var newArr = [];
		var pages = [];

		// Copy the contents of data into newArr, breaking the reference.
		for (var i in data) { newArr.push(data[i]); }

		while (newArr.length > 0) {
			pages.push(newArr.splice(0, pageSize));
		}

		return pages;
	};

	$scope.$watch('currentPage', function(val) {
			$scope.currentPageView = $scope.pages[$scope.currentPage - 1];

			if ($scope.pages.length - $scope.currentPage <= 5) {
				if ($scope.gettingMovies || $scope.nextPageUrl === null) { return; }

				$scope.gettingMovies = true;

				if ($scope.nextPageUrl) {
					Movies.getNextPage($scope.nextPageUrl).
						success(function(data) {
							$scope.gettingMovies = false;
							$scope.movies = data;
							angular.forEach($scope.movies.results, function(movie, index){
								movie.tags = movie.genre.split(',');
							});
							$scope.nextPageUrl = data.next;
							$scope.pages.push.apply($scope.pages, $scope.paginate($scope.movies.results, 24));
							$scope.currentPageView = $scope.pages[$scope.currentPage - 1];
						});
				}
			}
	});

}]);