import os, sys
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
        
def make_app():
    return tornado.web.Application([ (r'/webcam', WSHandler),
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