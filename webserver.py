import asyn
import ujson
from uwebsocket import *
from lights import Lights
import uasyncio as asyncio


class Server(WebSocketServer):

    def __init__(self, lights: Lights):
        self.lights = lights
        super().__init__(2)

    def _make_client(self, conn):
        return Client(conn, self.lights)


class Client(WebSocketClient):

    def __init__(self, conn, lights: Lights):
        self.lights = lights
        super().__init__(conn)

    def process(self):
        try:
            msg = self.connection.read()

            if not msg:
                return

            msg = ujson.loads(msg.decode("utf-8"))
            command = msg.get('command')
            loop = asyncio.get_event_loop()

            if command is not None:
                if command == 'police':
                    loop.create_task(asyn.Cancellable(self.lights.rgb_police, group=1)())
                elif command == 'jump':
                    loop.create_task(asyn.Cancellable(self.lights.rgb_jump, 1, 1.0, 128, group=1)())
                elif command == 'fade':
                    loop.create_task(asyn.Cancellable(self.lights.rgb_fade, 2, group=1)())
                elif command == 'stop':
                    loop.call_soon(self.lights.rgb_cancel())
                else:
                    loop.call_soon(self.lights.rgb_color(msg.get('value', '#000000')))

                self.connection.write(ujson.dumps(msg))
            else:
                raise ValueError('Missing command type!')

        except ValueError as error:
            self.connection.write(ujson.dumps({'error': str(error)}))

        except ClientClosedError:
            disconnected = ujson.dumps(['aaaa'])
            self.connection.write(disconnected)
            self.connection.close()
