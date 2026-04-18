import json
import logging

from datetime import datetime

from lib.send_packet import send_packet
from lib.write_measurement import write_measurement

import tornado.ioloop
import tornado.web
import tornado.websocket

from lib.predict import get_values

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

error_log = ""


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
        logger.info("WebSocket opened")
        client_name = self.get_argument(
            "client_name", "anonymous"
        )  # Get the client name
        self.client_name = client_name  # Store the client name
        if client_name in self.clients:  # If a client with the same name already exists
            self.clients[client_name].close()  # Close the old client's connection
        self.clients[client_name] = self  # Store the WebSocketHandler instance

    def on_message(self, message):
        global error_log

        try:
            error_log = ""
            record = write_measurement(message)
        except ValueError:
            self.write_message("Invalid data.")
            error_log = str(datetime.now()) + ": " + "Invalid data."
            logger.warning("WebSocket received invalid data")
        except Exception as e:
            error_log = str(datetime.now()) + ": " + str(e)
            logger.exception("Unexpected error while handling WebSocket message")

    def on_close(self):
        logger.info("WebSocket closed")
        if (
            self in self.clients.values()
        ):  # Only remove the client if it's still in the clients dictionary
            del self.clients[self.client_name]  # Remove the WebSocketHandler instance

    @classmethod
    def send_to_clients(cls, bufs):
        logger.info("Sending packets to %d clients", len(cls.clients))
        for client in cls.clients.values():
            for buf in bufs:
                client.write_message(buf, binary=True)


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
        global error_log
        try:
            bufs = send_packet(self.request.body)
            WebSocketHandler.send_to_clients(bufs)
        except json.JSONDecodeError:
            self.set_status(400)  # Bad Request
            self.write({"error": "Invalid JSON."})
            error_log = str(datetime.now()) + ": " + "Invalid JSON."
            logger.warning("API received invalid JSON")
            return
        except ValueError:
            self.set_status(400)
            self.write({"error": "Invalid data."})
            error_log = str(datetime.now()) + ": " + "Invalid data."
            logger.warning("API received invalid data")
            return
        except Exception as e:
            self.set_status(400)
            self.write({"error": "An unexpected error occurred."})
            error_log = str(datetime.now()) + ": " + str(e)
            logger.exception("Unexpected error in API POST handler")

    def get(self):
        url = get_values()
        if error_log:
            self.write({"error": error_log})
        else:
            self.write(url)

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
