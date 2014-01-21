
var mevies = angular.module('mevies', ['ui.bootstrap', 'ngSanitize']);

// app configuration
mevies.config(function($provide, $windowProvider, $httpProvider) {
	var apiBaseUrl = 'http://movies.jukic.me/api/';

	$httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

	$provide.value('API_BASE_URL', apiBaseUrl);
	$provide.value('CSRF_TOKEN', $windowProvider.$get().csrfToken);
});

// service for getting movies
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

	$scope.pages = [];
	$scope.currentPage = 1;
	$scope.gettingMovies = true;
	$scope.tagFilters = [];

	// ordering parameters
	$scope.predicate = 'year'
	$scope.reverse = true;


	// SCOPE FUNCTIONS

	// a function to get movie details
	$scope.getMovie = function(movieId) {
		Movies.getMovie(movieId)
			.success(function(data) {
				$scope.movie = data;
				$scope.movieTrailer = $sce.trustAsHtml('<iframe id="player" width="560" height="315" frameborder="0" allowfullscreen="" src="https://www.youtube.com/embed/' + $scope.movie.youtube_video_id + '?rel=0&amp;autohide=1&amp;showinfo=0&amp;modestbranding=1&amp;iv_load_policy=3"></iframe>');
				$scope.movieLoaded = true;
			});
	}

	// a function to get the initial list of movies
	$scope.getMovies = function(requestData, promise) {
		Movies.getList(requestData, promise)
			.success(function(data) {
				$scope.gettingMovies = false;
				$scope.movies = data;
				angular.forEach($scope.movies.results, function(movie, index){
					if(movie.genre !== '') movie.tags = movie.genre.replace(/ /g,'').split(',');
				});
				$scope.nextPageUrl = data.next;
				$scope.pages = $scope.paginate($scope.movies.results, 24);
				$scope.currentPageView = $scope.pages[$scope.currentPage - 1];
				$scope.totalNumOfMovies = data.count;
			});
	}

	// a function to get a filtered list of movies
	$scope.getFilteredList = function(requestData, promise) {
		Movies.getList(requestData, promise)
			.success(function(data) {
				$scope.gettingMovies = false;
				$scope.movies = data;
				angular.forEach($scope.movies.results, function(movie, index){
					if(movie.genre !== '') movie.tags = movie.genre.replace(/ /g,'').split(',');
				});
				$scope.nextPageUrl = data.next;
				$scope.pages = $scope.paginate($scope.movies.results, 24);
				$scope.currentPage = 1;
				$scope.currentPageView = $scope.pages[$scope.currentPage - 1];
			});
	}

	// check if the page is a movie detail page
	// and if it is, fetch the movie
	var path = window.location.pathname.split('/');
	if (path[1] === 'movie') {
		$scope.getMovie(path[2].split('-')[0]);
	}
	// if not get a list of movies
	else {
		var requestData = {
			page_size: 240, 
			ordering: (($scope.reverse) ? '-' : '') + $scope.predicate
		};
		$scope.getMovies(requestData);
	}

	// add genre to filter list
	$scope.addTagFilter = function(tag) {
		if ($scope.tagFilters.indexOf(tag.toLowerCase()) == -1) {
			$scope.tagFilters.push(tag.toLowerCase());

			// TODO Don't make canceler global.
			if (typeof canceler !== 'undefined') { canceler.resolve(); }
			canceler = $q.defer();
			$scope.gettingMovies = true;

			var requestData = {
				ordering: (($scope.reverse) ? '-' : '') + $scope.predicate,
				page_size: 240,
				page: 1,
				genre: $scope.tagFilters.join(',')
			};
			requestData[$scope.searchBy.toLowerCase()] = $scope.searchMovies;

			$scope.getFilteredList(requestData, canceler);
		}
	}

	// remove genre from filter list
	$scope.removeTagFilter = function(index) {
		$scope.tagFilters.splice(index, 1);

		// TODO Don't make canceler global.
		if (typeof canceler !== 'undefined') { canceler.resolve(); }
		canceler = $q.defer();
		$scope.gettingMovies = true;

		var requestData = {
			ordering: (($scope.reverse) ? '-' : '') + $scope.predicate,
			page_size: 240,
			page: 1,
			genre: $scope.tagFilters.join(',')
		};
		requestData[$scope.searchBy.toLowerCase()] = $scope.searchMovies;

		$scope.getFilteredList(requestData, canceler);
	}

	// search movies using the API
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
			ordering: (($scope.reverse) ? '-' : '') + $scope.predicate,
			page_size: 240,
			page: 1,
			genre: $scope.tagFilters.join(',')
		};
		requestData[$scope.searchBy.toLowerCase()] = $scope.searchMovies;

		$scope.stopSearch = $timeout(function() {
			Movies.getList(requestData, canceler.promise).
				success(function(data) {
					$scope.gettingMovies = false;
					$scope.movies = data;
					angular.forEach($scope.movies.results, function(movie, index){
						if(movie.genre !== '') movie.tags = movie.genre.replace(/ /g,'').split(',');
					});
					$scope.nextPageUrl = data.next;
					$scope.pages.push.apply($scope.pages, $scope.paginate($scope.movies.results, 24));
					$scope.currentPageView = $scope.pages[$scope.currentPage - 1];
				});
		}, 1500);
	};

	// clear search when X is clicked
	$scope.clearSearch = function() {
		$scope.searchMovies = '';
		$scope.pages = [];
		$scope.currentPage = 1;
		$scope.currentPageView = $scope.pages[$scope.currentPage - 1];
		$scope.gettingMovies = true;
		var requestData = {
			ordering: (($scope.reverse) ? '-' : '') + $scope.predicate,
			page_size: 240,
			page: 1,
			genre: $scope.tagFilters.join(',')
		};
		$scope.getFilteredList(requestData);
	}

	// sort function
	$scope.sort = function() {
        $scope.pages = [];
        $scope.currentPage = 1;
        $scope.currentPageView = $scope.pages[$scope.currentPage - 1];

        // TODO Don't make canceler global.
        if (typeof canceler !== 'undefined') { canceler.resolve(); }
        canceler = $q.defer();

        $scope.gettingMovies = true;

        var requestData = {
			ordering: (($scope.reverse) ? '-' : '') + $scope.predicate,
			page_size: 240,
			page: 1,
			genre: $scope.tagFilters.join(',')
		};
		requestData[$scope.searchBy.toLowerCase()] = $scope.searchMovies;

        $scope.getFilteredList(requestData, canceler.promise);
    };

    // pagination function
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


	// WATCH EXPRESSIONS

	// watch for value change in currentPage model
	$scope.$watch('currentPage', function(val) {
			$scope.currentPageView = $scope.pages[$scope.currentPage - 1];

			if ($scope.pages.length - $scope.currentPage <= 5) {
				if ($scope.gettingMovies || $scope.nextPageUrl === null) { return; }

				if ($scope.nextPageUrl) {
					Movies.getNextPage($scope.nextPageUrl).
						success(function(data) {
							$scope.movies = data;
							angular.forEach($scope.movies.results, function(movie, index){
								if(movie.genre !== '') movie.tags = movie.genre.replace(/ /g,'').split(',');
							});
							$scope.nextPageUrl = data.next;
							$scope.pages.push.apply($scope.pages, $scope.paginate($scope.movies.results, 24));
							$scope.currentPageView = $scope.pages[$scope.currentPage - 1];
						});
				}
			}
	});
}]);