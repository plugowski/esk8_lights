from config import Config
from machine import Pin, PWM


class Lights:

    rgb = tail_light = front_light = None

    def __init__(self, config: Config):
        if config.FRONT_LIGHT_ACTIVE:
            self.front_light = PWM(
                Pin(config.FRONT_LIGHT_PIN, Pin.OUT, value=0),
                freq=config.PWM_DEFAULT_FREQ,
                duty=config.STATE_OFF,
                timer=1
            )

        if config.TAIL_LIGHT_ACTIVE:
            self.tail_light = PWM(
                Pin(config.TAIL_LIGHT_PIN, Pin.OUT, value=0),
                freq=config.PWM_DEFAULT_FREQ,
                duty=config.STATE_OFF,
                timer=2
            )

    def tail(self, intensity: int) -> None:
        """ Manage tail light intensity
        """
        if self.tail_light is not None:
            self.tail_light.freq(self.DEFAULT_FREQ)
            self.tail_light.duty(round(intensity / self.INTENSITY_MAX_SCALE * 100, 2))

    def blink_tail(self, freq: int = 5, duty: int = 50) -> None:
        """ Make tail light blinky with specified frequency
        """
        self.tail_light.freq(freq)
        self.tail_light.duty(duty)

    def front(self, intensity: int ) -> None:
        """ Manage head light intensity
        """
        if self.front_light is not None:
            self.front_light.duty(round(intensity / self.INTENSITY_MAX_SCALE * 100, 2))

    def status(self) -> dict:
        """ Return actual lights status...
        """
        return {
            'rgb': {
                'mode': '',
                'r': self._calculate_color_value(self.rgb_matrix[0]),
                'g': self._calculate_color_value(self.rgb_matrix[1]),
                'b': self._calculate_color_value(self.rgb_matrix[2])
            },
            'front': int(self.front_light.duty() * self.INTENSITY_MAX_SCALE / 100),
            'tail': {
                'mode': '',
                'value': int(self.tail_light.duty() * self.INTENSITY_MAX_SCALE / 100),
            }
        }

