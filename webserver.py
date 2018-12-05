from lights_service import LightsService
from uwebsocket import *
import uasyncio as asyncio
import ujson
import asyn


class Server(WebSocketServer):

    def __init__(self, lights_service: LightsService):
        self.lights_service = lights_service
        super().__init__(3)

    def _make_client(self, conn):
        return Client(conn, self.lights_service)


class Client(WebSocketClient):

    def __init__(self, conn, lights_service: LightsService):
        self.lights_service = lights_service
        asyncio.get_event_loop().call_soon(self.lights_service.status_worker(conn, 0.1))
        super().__init__(conn)

    def process(self):
        try:
            msg = self.connection.read()

            if not msg:
                return

            msg = ujson.loads(msg.decode("utf-8"))
            command = msg.pop('command')
            loop = asyncio.get_event_loop()

            if command is not None:

                if command in ['front', 'tail', 'blink_tail', 'color', 'jump', 'fade', 'police', 'cancel']:
                    loop.call_soon(self.lights_service.action_handler(command, **msg))
                    self.connection.write(command + ' : ' + ujson.dumps(msg))
                elif command == 'status':
                    self.connection.write(ujson.dumps(self.lights_service.read_status()))
                else:
                    raise ValueError('Invalid command! ' + str(command))

            else:
                raise ValueError('Missing command!')

        except ValueError as error:
            self.connection.write(ujson.dumps({'error': str(error)}))

        except ClientClosedError:
            self.connection.close()
