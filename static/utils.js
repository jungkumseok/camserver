'use strict';

function PersistentWebSocket(endpoint, refresh_rate, retry_rate){
	var self = this;
	console.log("Persistent WebSocket Object Created...");
	
	if (!refresh_rate) refresh_rate = 100;
	if (!retry_rate) retry_rate = 5000;
	self.refresh_rate = refresh_rate;
	self.retry_rate = retry_rate;

	self.endpoint = endpoint;
	self.ws_timer = null;
	self.retry_timer = null;
	self.socket = null;
	
	self.ENDPOINT_ALIVE = false;

	self.onMessageReceive = [];
	self.onMessageReceiveRaw = [];
	
	self.initialize();
}
PersistentWebSocket.prototype.initialize =function(){
	var self = this;
	if (self.socket) self.socket = null;
	self.socket = new WebSocket("ws://"+self.endpoint);
	self.socket.onopen = function(){
		console.debug("WebSocket to "+self.endpoint+" opened");
		self.ENDPOINT_ALIVE = true;
		self.ws_timer = setInterval(function(){
			if (self.socket.readyState == 1){
				self.socket.send( JSON.stringify({ operation: 'get' }));	
			}
			else {
				clearInterval(self.ws_timer);
			}
		}, self.refresh_rate);
	};
	self.socket.onclose = function(){
		self.ENDPOINT_ALIVE = false;
		console.debug("WebSocket to "+self.endpoint+" closed");
		clearInterval(self.ws_timer);
		setTimeout(function(){
			console.debug("Trying to open Websocket to "+self.endpoint+" again");
			self.initialize();
		}, self.retry_rate);
	};
	self.socket.onerror = function(){
		self.ENDPOINT_ALIVE = false;
		console.error("ERROR on WebSocket to "+self.endpoint);
	};
	self.socket.onmessage = function(event){
		for (var i=0; i < self.onMessageReceive.length; i++){
			self.onMessageReceive[i](event, JSON.parse(event.data));
		}
		for (var i=0; i < self.onMessageReceiveRaw.length; i++){
			self.onMessageReceiveRaw[i](event, event.data);
		}
	};
};
PersistentWebSocket.prototype.isAlive = function(){
	return this.ENDPOINT_ALIVE;
}
PersistentWebSocket.prototype.addEventListener = function(eventName, handlerFunc){
	console.log("Binding to Event "+eventName);
	if (this[eventName].indexOf(handlerFunc) < 0) this[eventName].push(handlerFunc);
	else throw "No Such Event : "+eventName;
}
PersistentWebSocket.prototype.removeAllEventListeners = function(eventName){
	this[event] = [];
}
PersistentWebSocket.prototype.send = function(data){
	if (this.socket.readyState === 1){
		this.socket.send( JSON.stringify( data ) );
	}
	else {
		throw "Socket Not Ready";
	}
};