import os, sys, json, math
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver
from camera import WebCam

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
}

webcam = WebCam(10)

class WSHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True
    
    def open(self):
        print("Websocket Connected from "+self.request.remote_ip);
        
    def on_message(self, message):
        self.write_message(webcam.data)
                
    def on_close(self):
        print("Websocket Closed")
        
class CapturedFilesHandler(tornado.web.RequestHandler):
    def get(self, page):
        page = int(page)
        flist = os.listdir('static/captured')
        print(flist)
        files = [f.split('.')[0] for f in flist if os.path.isfile(os.path.join('static/captured', f)) and f.split('.')[1] == 'mp4']
        files = list(reversed(sorted(files)))
        si = (page - 1) * 10 if page > 0 else 0
        fi = si + 10
        self.write( json.dumps({ 'total_pages': math.ceil(len(files) / 10),
                                'total_files': len(files),
                                'filenames' : files[si:fi] }) )
        
def make_app():
    return tornado.web.Application([ (r'/webcam', WSHandler),
                                     (r'/CaptureFiles/([1-9]\d*)/', CapturedFilesHandler),
                                     (r'/(.*)', tornado.web.StaticFileHandler, {'path': settings['static_path'], 'default_filename': 'index.html'}),
                                    ])
    
def start(port):
    app = make_app()
    app.listen(port)
    print("WebCam Service Start...")
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    webcam.start()
    port = 8100
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    start(port)
    webcam.shutdown()
    webcam.join()
