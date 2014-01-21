var mevies = angular.module('mevies', ['ui.bootstrap', 'ngSanitize']);

mevies.config(function($provide, $windowProvider, $httpProvider) {
	var apiBaseUrl = 'http://movies.jukic.me/api/';

	$httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

	$provide.value('API_BASE_URL', apiBaseUrl);
	$provide.value('CSRF_TOKEN', $windowProvider.$get().csrfToken);
});

mevies.factory('Movies', ['$http', 'API_BASE_URL', function ($http, API_BASE_URL) {
	return {
		getList: function(params, promise) {
			return $http({
				method: 'GET',
				url: API_BASE_URL + 'movies/',
                timeout: promise,
				params: params
			});
		},
		getNextPage: function(url) {
			return $http({
				method: 'GET',
				url: url
			});
		},
		getMovie: function(movie_id) {
			return $http({
				method: 'GET',
				url: API_BASE_URL + 'movies/' + movie_id + '/'
			});
		}
	};
}]);

mevies.controller('MeviesCtrl', ['$scope', '$timeout', '$q', '$sce', 'Movies', function ($scope, $timeout, $q, $sce, Movies) {

	$scope.currentPage = 1;
	$scope.gettingMovies = true;
	$scope.listView = false;
	$scope.tagFilters = [];
	$scope.pages = [];
	$scope.predicate = 'year'
	$scope.reverse = true;


	$scope.getMovie = function(movieId) {
		Movies.getMovie(movieId)
			.success(function(data) {
				$scope.movie = data;
				$scope.movieTrailer = $sce.trustAsHtml('<iframe id="player" width="560" height="315" frameborder="0" allowfullscreen="" src="https://www.youtube.com/embed/' + $scope.movie.youtube_video_id + '}?rel=0&amp;controls=0&amp;showinfo=0&amp;modestbranding=1&amp;iv_load_policy=3"></iframe>');
				$scope.movieLoaded = true;
			});
	}

	$scope.getMovies = function(requestData, promise) {
		Movies.getList(requestData, promise)
			.success(function(data) {
				$scope.gettingMovies = false;
				$scope.movies = data;
				angular.forEach($scope.movies.results, function(movie, index){
					if(movie.genre !== '') movie.tags = movie.genre.split(',');
				});
				$scope.nextPageUrl = data.next;
				$scope.pages = $scope.paginate($scope.movies.results, 24);
				$scope.currentPageView = $scope.pages[$scope.currentPage - 1];
				$scope.totalNumOfMovies = data.count;
			});
	}

	$scope.getFilteredList = function(requestData, promise) {
		Movies.getList(requestData, promise)
			.success(function(data) {
				$scope.gettingMovies = false;
				$scope.movies = data;
				angular.forEach($scope.movies.results, function(movie, index){
					if(movie.genre !== '') movie.tags = movie.genre.split(',');
				});
				$scope.nextPageUrl = data.next;
				$scope.pages = $scope.paginate($scope.movies.results, 24);
				$scope.currentPage = 1;
				$scope.currentPageView = $scope.pages[$scope.currentPage - 1];
			});
	}

	var path = window.location.pathname.split('/');
	if (path[1] === 'movie') {
		$scope.getMovie(path[2].split('-')[0]);
	}
	else {
		var requestData = {page_size: 240, ordering: (($scope.reverse) ? '-' : '') + $scope.predicate};
		$scope.getMovies(requestData);
	}

	$scope.addTagFilter = function(tag) {
		if ($scope.tagFilters.indexOf(tag.toLowerCase()) == -1) {
			$scope.tagFilters.push(tag.toLowerCase());

			// TODO Don't make canceler global.
			if (typeof canceler !== 'undefined') { canceler.resolve(); }
			canceler = $q.defer();
			$scope.gettingMovies = true;

			var requestData = {
				title: $scope.searchMovies,
				ordering: (($scope.reverse) ? '-' : '') + $scope.predicate,
				page_size: 240,
				page: 1,
				genre: $scope.tagFilters.join(',')
			};

			$scope.getFilteredList(requestData, canceler);
		}
	}

	$scope.removeTagFilter = function(index) {
		$scope.tagFilters.splice(index, 1);

		// TODO Don't make canceler global.
		if (typeof canceler !== 'undefined') { canceler.resolve(); }
		canceler = $q.defer();
		$scope.gettingMovies = true;

		var requestData = {
			title: $scope.searchMovies,
			ordering: (($scope.reverse) ? '-' : '') + $scope.predicate,
			page_size: 240,
			page: 1,
			genre: $scope.tagFilters.join(',')
		};

		$scope.getFilteredList(requestData, canceler);
	}

	$scope.search = function() {
		// When the search text field is changed this function is fired. We don't want to fire off
		// an ajax request with every change. Rather, let's be a little smart about this and fire
		// off a request if there hasn't been a change within 1.5 seconds.

		// TODO Don't make canceler global.
		if (typeof canceler !== 'undefined') { canceler.resolve(); }
		canceler = $q.defer();

		$scope.pages = [];
		$scope.currentPage = 1;
		$scope.currentPageView = $scope.pages[$scope.currentPage - 1];

		$timeout.cancel($scope.stopSearch);
		$scope.gettingMovies = true;

		var requestData = {
			title: $scope.searchMovies,
			ordering: (($scope.reverse) ? '-' : '') + $scope.predicate,
			page_size: 240,
			page: 1,
			genre: $scope.tagFilters.join(',')
		};

		$scope.stopSearch = $timeout(function() {
			Movies.getList(requestData, canceler.promise).
				success(function(data) {
					$scope.gettingMovies = false;
					$scope.movies = data;
					angular.forEach($scope.movies.results, function(movie, index){
						if(movie.genre !== '') movie.tags = movie.genre.split(',');
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
		var requestData = {page_size: 240, ordering: (($scope.reverse) ? '-' : '') + $scope.predicate};
		$scope.getMovies(requestData);
	}

	$scope.sort = function() {
        $scope.pages = [];
        $scope.currentPage = 1;
        $scope.currentPageView = $scope.pages[$scope.currentPage - 1];

        // TODO Don't make canceler global.
        if (typeof canceler !== 'undefined') { canceler.resolve(); }
        canceler = $q.defer();

        $scope.gettingMovies = true;

        var requestData = {
			title: $scope.searchMovies,
			ordering: (($scope.reverse) ? '-' : '') + $scope.predicate,
			page_size: 240,
			page: 1,
			genre: $scope.tagFilters.join(',')
		};

        $scope.getMovies(requestData, canceler.promise);
    };

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

				if ($scope.nextPageUrl) {
					Movies.getNextPage($scope.nextPageUrl).
						success(function(data) {
							$scope.movies = data;
							angular.forEach($scope.movies.results, function(movie, index){
								if(movie.genre !== '') movie.tags = movie.genre.split(',');
							});
							$scope.nextPageUrl = data.next;
							$scope.pages.push.apply($scope.pages, $scope.paginate($scope.movies.results, 24));
							$scope.currentPageView = $scope.pages[$scope.currentPage - 1];
						});
				}
			}
	});

}]);