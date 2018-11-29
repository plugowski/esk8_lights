from lights import Lights
import uasyncio as asyncio
import webserver
import network

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=b"EBGT", authmode=network.AUTH_OPEN)  # ap.config(essid=b"Evolve Bamboo GT", authmode=network.AUTH_WPA_WPA2_PSK, password=b"MyBambooGT")
lights = Lights(14, 16, 12, back=27)
app_socket = webserver.Server(lights)


def run():
    global app_socket
    try:
        app_socket.start()

        loop = asyncio.get_event_loop()
        loop.call_soon(app_socket.process_all())

        loop.run_forever()
        app_socket.stop()

    except KeyboardInterrupt:

        app_socket.stop()

        if ap.isconnected():
            ap.disconnect()


run()
