import tornado.ioloop
import tornado.web
import tornado.websocket
from api import devices

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    clients = {}

    def check_origin(self, origin):
        return True
    
    def open(self):
        print("WebSocket opened")
        client_name = self.get_argument('client_name', 'anonymous')  # Get the client name
        self.client_name = client_name  # Store the client name
        if client_name in self.clients:  # If a client with the same name already exists
            self.clients[client_name].close()  # Close the old client's connection
        self.clients[client_name] = self  # Store the WebSocketHandler instance

    def on_message(self, message):
        print(message)
        self.write_message(u"You mentioned: " + message)
        devices.write_measurement(message)


    def on_close(self):
        print("WebSocket closed")
        if self in self.clients.values():  # Only remove the client if it's still in the clients dictionary
            del self.clients[self.client_name]  # Remove the WebSocketHandler instance

    @classmethod
    def send_to_clients(cls, message):
        print(cls.clients)
        for client in cls.clients.values():
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