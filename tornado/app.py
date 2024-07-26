import json

from api import devices

import tornado.ioloop
import tornado.web
import tornado.websocket


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    clients = {}

    def check_origin(self, origin):
        # This method can be used to allow/disallow cross-origin requests
        # Here, it's set to always allow. You might want to restrict it to certain origins.
        return True

    def set_default_headers(self):
        # Set CORS headers here
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header(
            "Access-Control-Allow-Headers", "Content-Type, X-Requested-With"
        )
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")

    def open(self):
        print("WebSocket opened")
        client_name = self.get_argument(
            "client_name", "anonymous"
        )  # Get the client name
        self.client_name = client_name  # Store the client name
        if client_name in self.clients:  # If a client with the same name already exists
            self.clients[client_name].close()  # Close the old client's connection
        self.clients[client_name] = self  # Store the WebSocketHandler instance

    def on_message(self, message):
        print(message)
        self.write_message(u"Data Received!")
        devices.write_measurement(message)

    def on_close(self):
        print("WebSocket closed")
        if (
            self in self.clients.values()
        ):  # Only remove the client if it's still in the clients dictionary
            del self.clients[self.client_name]  # Remove the WebSocketHandler instance

    @classmethod
    def send_to_clients(cls, message):
        print(cls.clients)
        for client in cls.clients.values():
            client.write_message(message)


class ApiHandler(tornado.web.RequestHandler):  # Add this class
    def set_default_headers(self):
        # Set CORS headers here
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header(
            "Access-Control-Allow-Headers",
            "x-requested-with, Content-Type, " "Access-Control-Allow-Origin",
        )
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")

    def post(self):
        try:
            body = self.request.body
            WebSocketHandler.send_to_clients(json.loads(body))
        except json.JSONDecodeError:
            self.set_status(400)  # Bad Request
            self.write({"error": "Invalid JSON."})
            return

    def get(self):
        WebSocketHandler.send_to_clients("hello")
        self.write("10")

    def options(self):
        self.set_status(204)
        self.finish()


def make_app():
    return tornado.web.Application([(r"/", WebSocketHandler), (r"/send", ApiHandler)])


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.autoreload.start()  # ここでautoreloadを開始
    tornado.ioloop.IOLoop.current().start()
