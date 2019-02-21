from config import Config
import rgb_strip
import ujson


class WebsocketService:

    def __init__(self, config: Config):

        self.config = config

        if self.config.RGB_TYPE == self.config.LED_STANDARD:
            self.rgb_strip = rgb_strip.RGBAnalog(self.config)
        elif self.config.RGB_TYPE == self.config.LED_WS2812B:
            self.rgb_strip = rgb_strip.RGBDigital(self.config)

    def accept_callback(self, web_socket, http_client):
        # on connection send actual status to websocket client
        web_socket.SendText(self._action_handler('status'))

        # set proper callbacks
        web_socket.RecvTextCallback = getattr(self, '_text_callback')
        web_socket.ClosedCallback = getattr(self, '_closed_callback')

    def _text_callback(self, web_socket, msg):
        try:
            request = ujson.loads(msg)
            if 'command' not in request.keys():
                raise ValueError('Request should contain command in JSON')
            web_socket.SendText(self._action_handler(request.pop('command'), **request))
        except ValueError as e:
            web_socket.SendText(self._jsonify(str(e), False))

    def _closed_callback(self, web_socket):
        # todo: connection close callback
        print("WS CLOSED")

    def _action_handler(self, action: str, *args, **kwargs):
        """ Run specified action after cancelled previous
        """
        if action == 'status':
            return 'WS Connected!'

        if action == 'config':
            if 'value' in kwargs.keys():
                self.config.set_value(kwargs['key'], kwargs['value'])
                return self._jsonify('%s has been updated to %s' % (kwargs['key'], kwargs['value']))
            else:
                return self._jsonify(self.config.get_value(kwargs['key']))

        return ujson.dumps(kwargs)

    @staticmethod
    def _jsonify(data, status: bool = True):
        return ujson.dumps({
            'status': 'success' if status else 'error',
            'payload': data
        })
