import tornado.ioloop
import tornado.web
import tornado.websocket

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True
    
    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        self.write_message(message)

    def on_close(self):
        print("WebSocket closed")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/ws", WebSocketHandler)
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()