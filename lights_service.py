from battery import Battery
from lights import Lights
import uasyncio as asyncio
import asyn


class LightsService:

    def __init__(self, lights: Lights, battery: Battery):
        self.battery = battery
        self.lights = lights

    async def action_handler(self, action: str, *args, **kwargs):
        """ Run specified action after cancelled previous
        """
        if action in ['front', 'tail']:
            getattr(self.lights, action)(*args, **kwargs)
            return

        await self.lights.rgb_cancel()

        if action != 'cancel':
            asyncio.get_event_loop().create_task(asyn.Cancellable(getattr(self.lights, 'rgb_' + action), *args, **kwargs)())

    def read_status(self):
        return {**self.battery.status(), **self.lights.status()}