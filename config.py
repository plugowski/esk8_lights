import os
import ujson


def resetable(cls):
    attributes = [f for f in dir(cls) if not callable(getattr(cls, f)) and not f.startswith('__')]
    cls._resetable_cache_ = {}
    for attr in attributes:
        cls._resetable_cache_[attr] = getattr(cls, attr)
    return cls


@resetable
class Config:
    """ Main application configuration, here you can set pins where specified things are connected
        Some configurations can be overwritten by config.json which will be set via external application
    """

    WIFI_SSID = b"Evolve Bamboo GT"
    WIFI_PASS = b"MyBambooGT"

    LED_STANDARD = const(1)
    LED_WS2812B = const(2)
    ENABLED = const(1)
    DISABLED = const(0)

    PWM_DEFAULT_FREQ = 200  # can be overwrite by custom config
    PWM_DEFAULT_VALUE = const(50)
    PWM_MIN_SCALE = const(0)
    PWM_MAX_SCALE = const(100)

    # changes per minute <delay is calculated as (60/speed) * 1000 [ms]>
    RGB_DEFAULT_SPEED = 100  # can be overwritten by custom config

    RGB_ACTIVE = ENABLED
    RGB_TYPE = LED_STANDARD

    RGB_RED_PIN = const(27)
    RGB_GREEN_PIN = const(16)
    RGB_BLUE_PIN = const(12)
    RGB_SIGNAL_PIN = const(5)

    NEOPIXEL_SIGNAL_PIN = const(5)
    NEOPIXEL_GND_PIN = const(12)
    NEOPIXEL_LED_AMOUNT = const(20)

    FRONT_LIGHT_ACTIVE = ENABLED
    FRONT_LIGHT_PIN = const(26)

    TAIL_LIGHT_ACTIVE = DISABLED
    TAIL_LIGHT_PIN = const(32)

    BATTERY_ADC_ACTIVE = DISABLED
    BATTERY_ADC_PIN = const(33)

    CUSTOM_CONFIG = 'config.json'
    RESET_PIN = const(13)

    def __init__(self):
        self.load()

    def load(self):
        try:
            f = open(self.CUSTOM_CONFIG)
            json = f.read()
            config = ujson.loads(json)
            for key, value in config.items():
                setattr(self, key, value)
            f.close()
        except OSError:
            pass

    def set_value(self, key: str, value):
        f = open(self.CUSTOM_CONFIG, 'w+')
        file_content = f.read()

        if not file_content:
            json = {}
        else:
            json = ujson.load(file_content)

        json[key] = value
        f.write(ujson.dumps(json))
        f.close()
        self.load()

    def get_value(self, key: str):
        return None if not hasattr(self, key) else getattr(self, key)

    def reset(self):
        """ Remove custom config file, and reset object to original state!
        """
        os.remove(self.CUSTOM_CONFIG)

        attributes = [f for f in dir(self) if not callable(getattr(self, f)) and not f.startswith('_')]
        for key in [key for key in attributes if key not in self._resetable_cache_]:
            delattr(self, key)
        for key, value in self._resetable_cache_.items():
            setattr(self, key, value)
