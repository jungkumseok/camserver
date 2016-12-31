import os, cv2, time, base64, datetime
import threading
from scipy.linalg import norm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def timefunc(func, print_result=True):
    def dfunc(*args, **kwargs):
        start = time.clock()
        result = func(*args, **kwargs)
        stop = time.clock()
        if print_result:
            print(str((stop - start)*1000)+" ms")
        return result
    return dfunc

def normalize(arr):
    rng = arr.max()-arr.min()
    amin = arr.min()
    return (arr-amin)*255/rng

class WebCam(threading.Thread):
    def __init__(self, framerate=15):
        threading.Thread.__init__(self)
        self.framerate = framerate
        si = -1
        self.camera = cv2.VideoCapture(si)        
        while not self.camera.isOpened():
            si = si + 1
            self.camera = cv2.VideoCapture(si)        
        self.raw_image = None
        self.gray_image = None
        self.image = None
        
        self.status = 'inactive'
        
        self.stableSnapshot = {
                               'raw': None,
                               'gray': None,
                               'jpg': None
                               }
        self.isRecording = False
        self.saveRecord = False
        self.current_record_file = None
        self.diff_buffer = [False for i in range(0, 20)]
        
    def start_recording(self):
        self.saveRecord = False
        self.isRecording = True
        fourcc = cv2.VideoWriter_fourcc(*'X264')
        self.current_record_file = 'static/captured/CAM_'+datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.recorder = cv2.VideoWriter(self.current_record_file+".mp4", fourcc, 20.0, (640, 480) )
        cv2.imwrite(self.current_record_file+'.jpg', self.raw_image)
        print("Starting Capture")
    
    def stop_recording(self):
        self.recorder.release()
        if not self.saveRecord:
            os.remove(os.path.join(BASE_DIR, self.current_record_file+".mp4"))
            os.remove(os.path.join(BASE_DIR, self.current_record_file+".jpg"))
            print("  removing capture - insignificant movement")
        self.isRecording = False
        self.current_record_file = None
        print("...Stopping Capture")
        
#     @timefunc
    def compare_frames(self, f1, f2):
        obj_cnt = 0
        if not f1 == None and not f2 == None:
            frameDelta = cv2.absdiff(f1, f2)
            thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
            
            thresh = cv2.dilate(thresh, None, iterations=2)
            _, cnts, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for c in cnts:
                if cv2.contourArea(c) < 250:
                    continue
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(self.raw_image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.rectangle(thresh, (x, y), (x + w, y + h), (0, 0, 255), 2)
                obj_cnt += 1
            cv2.putText(self.raw_image, ("Recording" if self.isRecording else "Idle"), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, ((0 if self.isRecording else 255), (0 if self.isRecording else 255), 255), 2)
            cv2.putText(self.raw_image, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S.%f %p"),
                (10, self.raw_image.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
#             cv2.imshow('diff', self.raw_image)
#             cv2.waitKey(1)
        return obj_cnt
    
#     @timefunc
    def update_frame(self):
        prev_snapshot = { 'raw': self.raw_image,
                          'gray': self.gray_image,
                          'jpg': self.image }
        success, self.raw_image = self.camera.read()
        self.gray_image = cv2.cvtColor(self.raw_image, cv2.COLOR_BGR2GRAY)
        self.gray_image = cv2.GaussianBlur(self.gray_image, (21, 21), 0)
        fdiff = self.compare_frames(prev_snapshot['gray'], self.gray_image)
        
        ret, self.image = cv2.imencode('.jpg', self.raw_image)
        
        if self.status == 'inactive':
            self.status = 'active'
            self.stableSnapshot['raw'] = self.raw_image
            self.stableSnapshot['gray'] = self.gray_image
            self.stableSnapshot['jpg'] = self.image

#         f1_size = self.image.nbytes if self.image != None else 0
#         ret, self.image = cv2.imencode('.jpg', self.raw_image)
#         f2_size = self.image.nbytes
#         fdiff = abs(f2_size - f1_size)
        
        self.diff_buffer.pop(0)
        if fdiff > 1:
            self.diff_buffer.append(True)
            if not self.isRecording:
                print("Movement detected! "+str(fdiff))
                self.start_recording()
        else:
            self.diff_buffer.append(False)
        if self.isRecording:
            self.recorder.write(self.raw_image)
        if not any(self.diff_buffer):
            if self.isRecording:
                print("Stabilized")
                self.stop_recording()
                self.stableSnapshot['raw'] = self.raw_image
                self.stableSnapshot['gray'] = self.gray_image
                self.stableSnapshot['jpg'] = self.image
        else:
            seq = list(filter(lambda x: x == True, self.diff_buffer))
#             print(len(seq))
            if len(seq) > 4:
                self.saveRecord = True
#             print(''.join([str(int(item)) for item in self.diff_buffer]))
    
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
        self.camera.release()
    
    def run(self):
        self.start_stream()
