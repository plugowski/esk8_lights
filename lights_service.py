from battery import Battery
from lights import Lights
import uasyncio as asyncio
import ujson
import asyn


class LightsService:

    cache_battery = None

    def __init__(self, lights: Lights, battery: Battery):
        self.battery = battery
        self.lights = lights

    async def action_handler(self, action: str, *args, **kwargs):
        """ Run specified action after cancelled previous
        """
        if action in ['front', 'tail', 'blink_tail']:
            getattr(self.lights, action)(*args, **kwargs)
            return

        await self.lights.rgb_cancel()

        if action != 'cancel':
            asyncio.get_event_loop().create_task(asyn.Cancellable(getattr(self.lights, 'rgb_' + action), *args, **kwargs)())

    async def status_worker(self, connection, freq: float = 2):
        """ Worker which updates current status via websocket
        """
        i = 0
        while True:

            if connection.ws is not None:
                connection.write(ujson.dumps(self.read_status(i == 0)))
                i = 0 if i > 100 else i + 1

            await asyncio.sleep(freq)

    def read_status(self, refresh_battery: bool = False):
        status = self.lights.status()

        if refresh_battery is True:
            self.cache_battery = self.battery.status()

        status.update(self.cache_battery)
        return status
