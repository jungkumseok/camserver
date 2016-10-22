'use strict';

var webcamApp = angular.module('webcamApp', [])
.factory('WebCamService', function(){
	var _WS = new PersistentWebSocket(window.location.hostname+':8100/webcam');
	return _WS;
})
.controller('WebCamCtrl', function($scope, WebCamService){
	var self = this;
	self.data = undefined;
	WebCamService.addEventListener('onMessageReceiveRaw', function(evt, data){
		self.data = "data:image/jpg;base64,"+data;
		$scope.$apply();
	});
})