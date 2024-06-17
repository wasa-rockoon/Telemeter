import tornado.ioloop
import tornado.web
import tornado.websocket
from api import devices

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    clients = []  # Add this line

    def check_origin(self, origin):
        return True
    
    def open(self):
        print("WebSocket opened")
        self.clients.append(self)  # Add this line

    def on_message(self, message):
        print(message)
        self.write_message(u"You mentioned: " + message)
        # devices.write_measurement(message)

    def on_close(self):
        print("WebSocket closed")
        self.clients.remove(self)  # Add this line

    @classmethod
    def send_to_clients(cls, message):  # Add this method
        print(cls.clients)
        for client in cls.clients:
            client.write_message(message)

class ApiHandler(tornado.web.RequestHandler):  # Add this class
    def get(self):
        # Do whatever you need to do for the API call
        WebSocketHandler.send_to_clients("API call received")

def make_app():
    return tornado.web.Application([
        (r"/", WebSocketHandler),
        (r"/api", ApiHandler),  # Add this line
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.autoreload.start()  # ここでautoreloadを開始
    tornado.ioloop.IOLoop.current().start()