from lights_service import LightsService
from battery import Battery
from lights import Lights
import uasyncio as asyncio
import webserver
import network


ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=b"Evolve Bamboo GT", authmode=network.AUTH_WPA_WPA2_PSK, password=b"MyBambooGT")
lights = Lights(14, 16, 12, 26, 27)
battery = Battery(33, max_value=8.2)
app_socket = webserver.Server(LightsService(lights, battery))


try:

    app_socket.start()
    loop = asyncio.get_event_loop()
    loop.call_soon(app_socket.process_all())
    loop.run_forever()

except KeyboardInterrupt:

    app_socket.stop()

    if ap.isconnected():
        ap.disconnect()
