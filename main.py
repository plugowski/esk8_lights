from config import Config
import network
from helpers import factory_reset
from machine import Pin
from microWebSrv import MicroWebSrv
from websocket_service import WebsocketService

config = Config()

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=config.WIFI_SSID, authmode=network.AUTH_WPA_WPA2_PSK, password=config.WIFI_PASS)

mws = MicroWebSrv()
mws.WebSocketThreaded = False
mws.AcceptWebSocketCallback = getattr(WebsocketService(config), 'accept_callback')
mws.Start()

Pin(config.RESET_PIN, mode=Pin.IN, pull=Pin.PULL_UP, handler=factory_reset, trigger=Pin.IRQ_LOLEVEL)