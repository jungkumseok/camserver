# Camserver - Lightweight Live WebCam Stream Server

This is a lightweight Python3 application used to provide live stream from USB webcams.
It is built using OpenCV and Tornado.

The implementation is quite basic; it captures images from the USB webcam through the `cv2.VideoCapture` API, then converts the jpeg image into a base64 encoded bytestring. This bytestring is then served through Tornado's websocket. Finally, from the front-end application (the included front-end application uses AngularJS), we fetch the bytestring and update the `src` of an `img` element at regular intervals. Thus this is a basic implementation of MJPEG.

By default, the application binds to port 8100 and captures images at 10 fps.

During execution, the application will compare the newly acquired image with the previous image to see if there is a significant difference ( Delta > threshold ) between the two frames. If there is a significant difference, it will start a `cv2.VideoWriter` stream and continue recording images until it determines the stream has "stabilized" (no more changes in the images); this is controlled by the `WebCam.diff_buffer`, which is a list of Delta's for the past N frames. If `WebCam.diff_buffer` is a list of length 20, the application will determine that the stream is "stable" if all of the 20 Deltas are below the threshold. Additionally, the application will discard a recorded stream if there are less than 5 frames with significant changes, in order to ignore minor movements or noises in the image. The recorded videos are saved as mp4 and served in the static folder for direct viewing from the browser.

##Dependencies

* Python 3
* OpenCV with Python bindings (Python `cv2` module; I'm using OpenCV 3.0.0)
* Tornado

## How to use

### 1. git clone the project
### 2. Start the Tornado application

```
python3 start.py
```

Optionally, you can pass in a different port number as the command line argument
```
python3 start.py 8000
```
If you're using a different port, you will need to change the port number in the front-end application too.
Example:
```
//app.js

webcamApp.factory('WebCamService', function(){
	var _WS = new PersistentWebSocket(window.location.hostname+':8000/webcam');
	return _WS;
})
```

### 3. Open a browser
and enter in the address bar "localhost:8100"

## License

MIT License