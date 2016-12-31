'use strict';

var webcamApp = angular.module('webcamApp', ['ngResource', 'ui.router'])
.filter('file_dtstamp', function(){
	return function(filename){
		var dtstring = (filename.split('.')[0]).split('_')[1];
		var dtstamp = new Date(dtstring.slice(0, 4),
								parseInt(dtstring.slice(4, 6)) -1,
								dtstring.slice(6, 8),
								dtstring.slice(8, 10),
								dtstring.slice(10, 12),
								dtstring.slice(12, 14) );
		return dtstamp;
	}
})
.factory('WebCamService', function(){
	var _WS = new PersistentWebSocket(window.location.hostname+':8100/webcam');
	return _WS;
})
.controller('WebCamCtrl', function($scope, $rootScope, WebCamService){
	var self = this;
	self.data = undefined;
	WebCamService.addEventListener('onMessageReceiveRaw', function(evt, data){
		self.data = "data:image/jpg;base64,"+data;
		$scope.$apply();
	});
	
	self.capture = function(){
//		var url = self.data.replace(/^data:image\/[^;]/, 'data:application/octet-stream');
//		window.open(url, 'LiveCamCapture.jpg');
		
		var downloadLink = document.createElement("a");
		downloadLink.href = self.data;
		downloadLink.download = "LiveCamCapture.jpg";
//		document.body.appendChild(downloadLink);
		downloadLink.click();
//		document.body.removeChild(downloadLink);
	};
	
	$scope.$on("$destroy", function(){
		WebCamService.removeAllEventListeners();
	});
	
})
.directive('pagination', ['$state', function($state){
	return {
		restrict: 'E',
		scope: {
			totalPages: '=',
			currentPage: '=',
			pageRange: '='
		},
		controller: function($scope){
			$scope.parseInt = parseInt;
			var self = this;
			$scope.pageList = [];
			$scope.$watch(function(){
				if ($scope.totalPages && $scope.currentPage) return $scope.currentPage;
				else return undefined;
			}, function(newVal){
				var si = parseInt(newVal) - $scope.pageRange;
				var fi = parseInt(newVal) + $scope.pageRange;
				$scope.pageList = [];
				for (var i=si; i <= fi; i++){
					if (i > 0 && i <= $scope.totalPages) $scope.pageList.push(i);
				};
				
			});
		},
		controllerAs: '$pagination',
		templateUrl: '/views/pagination.html'
	}
}])
.config(['$stateProvider', '$urlRouterProvider', 
        function($stateProvider, $urlRouterProvider){
    		
    		$stateProvider
    			.state('home', {
    				url: '/',
    				templateUrl: 'views/main.html',
    			})
    			.state('captures', {
    				url: '/captures/:page/',
    				params: {
    					page: '1'
    				},
    				controller: function($scope, $http, $stateParams){
    					$scope.parseInt = parseInt
    					$scope.captures = [];
    					$scope.page = $stateParams.page;
    					
    					$scope.getCaptures = function(){
    						$http.get('/CaptureFiles/'+$stateParams.page+'/')
    						   .then(function(response){
    							   $scope.captures = response.data.filenames;
    							   $scope.total_pages = response.data.total_pages;
    							   console.log($scope.total_pages);
    						   });
    					}
    					
    					$scope.getCaptures();
    				},
    				templateUrl: 'views/captures.html',
    			})
    			.state('captures.view', {
    				url: ':filename',
    				controller: function($scope, $stateParams){
    					$scope.filename = $stateParams.filename;
    					$scope.videopath = '/captured/' +$stateParams.filename +'.mp4';
    					$scope.imagepath = '/captured/' +$stateParams.filename +'.jpg';
    				},
    				templateUrl: 'views/captures_view.html'
    			})
    			
    	$urlRouterProvider.otherwise('/');
}])