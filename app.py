import asyncio
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone, tzinfo

import psycopg2
from tornado.web import Application, RequestHandler
from tornado.websocket import WebSocketHandler


class MainHandler(RequestHandler):
    def get(self):
        self.write('')

class BaseHandler(RequestHandler):
    @property
    def db(self):
        return self.application.db

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers",
                        "x-requested-with, Content-Type, "\
                        "Access-Control-Allow-Origin")
        self.set_header('Access-Control-Allow-Methods',
                        'POST, GET, PUT, DELETE, OPTIONS')

    def options(self, *args):
        self.set_status(204)
        self.finish()

    def get_password(self):
        raw_password = self.get_argument('password', '')
        if raw_password == '':
            return None
        else:
            return hashlib.sha256(raw_password.encode('utf-8')).hexdigest()

    def get_system(self, id, password=None, recursive=True):
        with self.db.cursor() as cursor:
            sql = 'SELECT name, client, password, active_flight_id'\
                ' FROM systems WHERE id = %s'
            cursor.execute(sql, [id])
            result = cursor.fetchone()
            if result is None:
                return None

            name, client, system_password, active_flight_id = result

            if active_flight_id is None:
                active_flight = None
            elif recursive:
                active_flight = self.get_flight(active_flight_id,
                                                recursive=False)
            else:
                active_flight = active_flight_id

            return {'id': id,
                    'name': name,
                    'client': client,
                    'admin': password == system_password,
                    'activeFlight': active_flight
                    }

    def get_flight(self, id, recursive=True):
        with self.db.cursor() as cursor:
            sql = 'SELECT system_id, name, start_time, launch_time, end_time, '\
                'data FROM flights WHERE id = %s'
            cursor.execute(sql, [id])
            result = cursor.fetchone()
            if result is None:
                return None

            system_id, name, start_time, launch_time, end_time, data = result

            if recursive:
                system = self.get_system(system_id, self.get_password(),
                                         recursive=False)
            else:
                system = system_id

            return {'id': id,
                    'system': system,
                    'name': name,
                    'startTime': start_time and start_time.isoformat() + 'Z',
                    'launchTime': launch_time and launch_time.isoformat() + 'Z',
                    'endTime': end_time and end_time.isoformat() + 'Z',
                    'data': data
                    }


class SystemListHandler(BaseHandler):
    def get(self):
        with self.db.cursor() as cursor:
            sql = "SELECT id, name, client, active_flight_id FROM systems"
            cursor.execute(sql, [])
            result = cursor.fetchall()

            systems = []

            for id, name, client, active_flight_id in result:
                if active_flight_id is None:
                    active_flight = None
                else:
                    active_flight = self.get_flight(active_flight_id)

                systems.append({'id': id,
                                'name': name,
                                'client': client,
                                'activeFlight': active_flight
                                })

            self.write(json.dumps({'systems': systems}))

class SystemHandler(BaseHandler):
    def get(self, id):
        system = self.get_system(id, self.get_password())

        if system is None:
            self.send_error(404)
        else:
            self.write(json.dumps(system))

    def put(self, id):

        system = self.get_system(id, self.get_password())

        if system is None:
            with self.db.cursor() as cursor:
                name = self.get_argument('name')
                client = self.get_argument('client', '')
                raw_password = self.get_argument('password')
                password = hashlib.sha256(raw_password.encode('utf-8'))\
                                  .hexdigest()

                sql = 'INSERT INTO systems (id, name, client, password)'\
                    'VALUES (%s, %s, %s, %s)'
                cursor.execute(sql, (id, name, client, password))
                self.db.commit()

        else:
            if not system['admin']:
                self.send_error(403)
                return

            name = self.get_argument('name', system['name'])
            client = self.get_argument('client', system['client'])

            with self.db.cursor() as cursor:
                sql = 'UPDATE systems SET name = %s, client = %s WHERE id = %s'
                cursor.execute(sql, (name, client, id))

                self.db.commit()

        system = self.get_system(id, self.get_password())
        self.write(json.dumps(system))


    def delete(self, id):

        with self.db.cursor() as cursor:
            sql = 'DELETE from systems WHERE id = %s'
            cursor.execute(sql, [id])
            self.db.commit()

        self.write({'status': 'ok'})


class FlightListHandler(BaseHandler):
    def get(self, system_id):
        with self.db.cursor() as cursor:
            sql = 'SELECT id, name, start_time, launch_time, end_time'\
                ' FROM flights WHERE system_id = %s'
            cursor.execute(sql, [system_id])
            result = cursor.fetchall()

            flights = []

            for id, name, start_time, launch_time, end_time in result:
                flights.append(
                    {'id': id,
                     'name': name,
                     'system': system_id,
                     'startTime': start_time and start_time.isoformat() + 'Z',
                     'launchTime': launch_time and launch_time.isoformat() +'Z',
                     'endTime': end_time and end_time.isoformat() + 'Z',
                     })

            self.write(json.dumps({'flights': flights}))

    def post(self, system_id):
        system = self.get_system(system_id, self.get_password())

        if system is None:
            self.send_error(403)
        elif not system['admin']:
            self.send_error(403)
        else:
            with self.db.cursor() as cursor:
                name = self.get_argument('name')
                activate = self.get_argument('activate', False)

                print('new flight', name, activate)

                sql = 'INSERT INTO flights'\
                    ' (system_id, name, start_time, launch_time)'\
                    'VALUES (%s, %s, current_timestamp, current_timestamp)'\
                    'RETURNING id'
                cursor.execute(sql, (system_id, name))
                result = cursor.fetchone()

                id, = result

                if activate:
                    sql = 'UPDATE systems SET active_flight_id = %s'\
                        ' WHERE id = %s'
                    cursor.execute(sql, (id, system_id))

                self.db.commit()

            flight = self.get_flight(id)
            self.write(json.dumps(flight))



class FlightHandler(BaseHandler):
    def get(self, id):
        flight = self.get_flight(id)

        if flight is None:
            self.send_error(404)
        else:
            self.write(json.dumps(flight))

class PacketsHandler(WebSocketHandler):

    listeners = defaultdict(lambda: [])

    @property
    def db(self):
        return self.application.db

    def check_origin(self, origin):
        return True

    def open(self, flight_id):
        self.flight_id = flight_id
        self.source = self.get_argument('source')
        print('open connection', flight_id, self.source)
        start_time = self.get_argument('startTime', None)
        self.start_time = datetime.fromisoformat(start_time) \
            if start_time else None
        end_time = self.get_argument('endTime', None)
        self.end_time = datetime.fromisoformat(end_time) \
            if end_time else None

        if self.start_time:
            PacketsHandler.listeners[self.flight_id].append(self)

            with self.db.cursor() as cursor:
                if self.end_time:
                    sql = 'SELECT time, source, raw FROM packets '\
                        'WHERE flight_id = %s AND time BETWEEN %s AND %s'
                    cursor.execute(sql, [self.flight_id, self.start_time,
                                         self.end_time])
                else:
                    sql = 'SELECT time, source, raw FROM packets '\
                        'WHERE flight_id = %s AND time > %s'
                    cursor.execute(sql, [self.flight_id, self.start_time])

                result = cursor.fetchall()

                for time, source, raw in result:
                    self.send_packet(time, source, raw)


    def on_message(self, message):
        if not isinstance(message, bytes):
            return

        unix_time = int.from_bytes(message[:8], 'little')
        time = datetime.fromtimestamp(unix_time / 1000.0, timezone.utc)
        type = message[8]
        from_ = message[9]
        raw = message[8:]

        # print('message', time, type, from_)

        for listener in PacketsHandler.listeners[self.flight_id]:
            if listener is not self:
                listener.send_packet(time, self.source, raw)

        with self.db.cursor() as cursor:
            sql = 'INSERT INTO packets'\
                ' (flight_id, time, source, type, from_, raw) '\
                'VALUES (%s, %s, %s, %s, %s, %s)'
            cursor.execute(
                sql,
                (self.flight_id, time, self.source, type, from_, raw))

            self.db.commit()

    def send_packet(self, time, source, raw):
        time = time.replace(tzinfo=timezone.utc)
        if not self.start_time or time < self.start_time:
            return
        if self.end_time and self.end_time < time:
            return

        bytes_ = bytearray(int(time.timestamp() * 1000.0).to_bytes(8, 'little'))
        bytes_.extend(source.encode('utf-8'))
        bytes_.extend(bytearray(16 - len(bytes_)))
        bytes_.extend(raw)
        try:
            self.write_message(bytes(bytes_), True)
        except:
            self.on_close()

    def on_close(self):
        print('close connection', self.flight_id, self.source)
        PacketsHandler.listeners[self.flight_id].remove(self)


class App(Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler),
            (r'/api/systems/?', SystemListHandler),
            (r'/api/systems/([^/]+)/?', SystemHandler),
            (r'/api/systems/([^/]+)/flights/?', FlightListHandler),
            (r'/api/flights/([^/]+)/?', FlightHandler),
            (r'/api/flights/([^/]+)/packets/?', PacketsHandler),
        ]
        Application.__init__(self, handlers, debug=True)

        self.db = psycopg2.connect(host='postgres',
                                   port='5432',
                                   database='tlmdb',
                                   user='postgre',
                                   password='postgre')

        print(self.db)

    # def __del__(self):
    #     self.db.close()

async def main():
    app = App()
    app.listen(8888)
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
