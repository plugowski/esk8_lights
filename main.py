from config import Config
import network
from machine import reset as machine_reset, Pin
from microWebSrv import MicroWebSrv
import utime
from websocket_service import WebsocketService

config = Config()

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=config.WIFI_SSID, authmode=network.AUTH_WPA_WPA2_PSK, password=config.WIFI_PASS)


def factory_reset(irq):
    start = irq.value()
    utime.sleep(10)
    if irq.value() == start:
        config.reset()
        machine_reset()
    else:
        irq.init(handler=factory_reset)


# reset to factory defaults
p = Pin(config.RESET_PIN, mode=Pin.IN, pull=Pin.PULL_UP, handler=factory_reset, trigger=Pin.IRQ_LOLEVEL)



mws = MicroWebSrv()
mws.WebSocketThreaded = False
mws.AcceptWebSocketCallback = getattr(WebsocketService(config), 'accept_callback')
mws.Start()