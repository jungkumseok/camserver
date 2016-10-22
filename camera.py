import cv2, time, base64
import threading

class WebCam(threading.Thread):
    def __init__(self, framerate=15):
        threading.Thread.__init__(self)
        self.framerate = framerate
        self.camera = cv2.VideoCapture(-1)
        self.raw_image = None
        self.image = None
        
    def update_frame(self):
        success, self.raw_image = self.camera.read()
        ret, self.image = cv2.imencode('.jpg', self.raw_image)
    
    @property
    def data(self):
        return base64.b64encode(self.image.tostring())
    
    def start_stream(self):
        last_updated = time.time()
        while True:
            curtime = time.time()
            if (curtime - last_updated) > (1 / self.framerate):
                last_updated = curtime
                self.update_frame()
    
    def run(self):
        self.start_stream()