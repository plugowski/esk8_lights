import _thread
from config import Config
from machine import PWM, Pin, Neopixel


class RGB(object):

    color_map = [
        [1, 0, 0],  # red
        [1, 1, 0],  # yellow
        [0, 1, 0],  # green
        [0, 1, 1],  # cyan
        [0, 0, 1],  # blue
        [1, 0, 1],  # purple
    ]

    def __init__(self, config: Config):
        self.config = config
        self.speed = self.config.RGB_DEFAULT_SPEED

    def brightness(self, intensity: int) -> None:
        """ Set brightness of led strip
        """

    def color(self, color: tuple) -> None:
        """ Just set single color with intensity, color is a tuple of colors (red, green, blue)
        """
        pass

    def sequence(self, mode: int, speed: float) -> None:
        """ Change colors in sequence, two modes #1 - six colors or #2 basic three colors (RGB)
        """
        pass

    def fade(self, speed: int):
        pass

    def rainbow(self, speed: int):
        pass

    def snake(self, length: int, speed: int):
        pass

    def flow(self):
        pass

    def police(self):
        pass

    def turnoff(self):
        pass

    def _wait_and_exit(self, time: int) -> bool:
        return _thread.wait(time) == _thread.EXIT


class RGBAnalog(RGB):

    def __init__(self, config: Config):

        super().__init__(config)

        self.leds = [
            PWM(
                Pin(self.config.RGB_RED_PIN, Pin.OUT, value=0),
                freq=self.config.PWM_DEFAULT_FREQ,
                duty=self.config.PWM_MIN_SCALE,
                timer=0
            ),
            PWM(
                Pin(self.config.RGB_GREEN_PIN, Pin.OUT, value=0),
                freq=self.config.PWM_DEFAULT_FREQ,
                duty=self.config.PWM_MIN_SCALE,
                timer=0
            ),
            PWM(
                Pin(self.config.RGB_BLUE_PIN, Pin.OUT, value=0),
                freq=self.config.PWM_DEFAULT_FREQ,
                duty=self.config.PWM_MIN_SCALE,
                timer=0
            )
        ]
        self.intensity = self.config.PWM_DEFAULT_VALUE

    def brightness(self, intensity: int):
        self.intensity = intensity

    def police(self) -> None:

        while True:
            self.leds[0].freq(10)
            self.leds[0].duty(round(self.intensity / self.config.PWM_MAX_SCALE * 100, 2))
            if self._wait_and_exit(30): return
            self.leds[0].duty(0)
            if self._wait_and_exit(20): return

            self.leds[2].freq(10)
            self.leds[2].duty(round(self.intensity / self.config.PWM_MAX_SCALE * 100, 2))
            if self._wait_and_exit(30): return
            self.leds[2].duty(0)
            if self._wait_and_exit(20): return

    def color(self, hex_color: str):
        color = list(int(hex_color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
        for pin, value in enumerate(color):
            dty = (float(value)/255) * (self.intensity / self.INTENSITY_MAX_SCALE) * 100
            self.rgb_matrix[pin].duty(round(dty, 2))

    def sequence(self, mode: int = 2, speed: float = 0.1) -> None:
        while True:
            for step, color in enumerate(self.COLORS):
                if mode == 2 and (step + 1) % 2 == 0:
                    continue

                self._set_color(map(lambda x: x * 255, color))

                if _thread.wait(speed * 1000) == _thread.EXIT:
                    return

    def rgb_color(self, hex_color: str, intensity: int = DEFAULT_INTENSITY) -> None:
        """ Set RGB color for lights, based on HEX string
        """
        rgb = list(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        self._set_intensity(intensity)
        self._set_color(rgb)

    def rgb_jump(self, mode: int = 2, speed: float = 0.1, intensity: int = DEFAULT_INTENSITY) -> None:
        """ Change colors in sequence, two modes #1 - six colors or #2 basic three colors (RGB)
        """
        while True:
            for step, color in enumerate(self.COLORS):
                if mode == 2 and (step + 1) % 2 == 0:
                    continue

                self._set_intensity(intensity)
                self._set_color(map(lambda x: x * 255, color))
                time.sleep(speed, 10)

    def rgb_fade(self, period: float, intensity: int = DEFAULT_INTENSITY) -> None:
        """ Fade RGB colors. Period is a cycle lenght in seconds.
        """
        colors = len(self.COLORS)
        period_ms = period * 1000
        steps = int(period_ms / (colors * 10))

        while True:
            for i in range(steps * colors):
                current_color = self.COLORS[int(i / steps)]
                next_color = self.COLORS[int(i / steps + 1) if i / steps + 1 < colors else 0]
                rgb = [0, 0, 0]
                for j in range(3):
                    if current_color[j] == next_color[j]:
                        rgb[j] = current_color[j] * steps
                    elif current_color[j] > next_color[j]:
                        rgb[j] = steps - (i % steps)
                    else:
                        rgb[j] = i % steps

                self._set_intensity(intensity)
                self._set_color(map(lambda x: x / steps * 255, rgb))
                time.sleep(0.01, 10)


    def rgb_reset(self) -> None:
        """ Reset RGB PWMs to neutral state
        """
        for pin in self.rgb_matrix:
            pin.freq(self.DEFAULT_FREQ)
            pin.duty(self.STATE_OFF)

    def rgb_cancel(self) -> None:
        """ Cancel all working coros and reset RGB lights
        """
        time.Cancellable.cancel_all()
        self.rgb_reset()

    def _set_intensity(self, intensity: int) -> int:
        self.rgb_intensity = intensity
        return intensity

    def _set_color(self, color: iter) -> None:
        """ Set specified color for RGB Pins, expected list with values of each color in range 0-255
        """
        for pin, value in enumerate(color):
            dty = (float(value)/255) * (self.rgb_intensity / self.INTENSITY_MAX_SCALE) * 100
            self.rgb_matrix[pin].duty(round(dty, 2))

    def _calculate_color_value(self, pin: PWM) -> int:
        """ Return color value in range 0-255 based on duty value
        """
        divider = self.rgb_intensity / self.INTENSITY_MAX_SCALE
        return 0 if divider == 0 else int(255 * (pin.duty() / divider / 100))


class RGBDigital(RGB):

    def __init__(self, config: Config):
        super().__init__(config)
        self.np = Neopixel(Pin(self.config.RGB_SIGNAL_PIN, Pin.OUT, value=0), self.config.NEOPIXEL_LED_AMOUNT)

    def brightness(self, intensity: int):
        self.np.brightness(int(255 * intensity / 100))

    def police(self):
        half_strip = Config.NEOPIXEL_LED_AMOUNT / 2

        while True:

            for x in range(3):
                self.np.set(1, 0x0000ff, num=half_strip)
                if self._wait_and_exit(30): return
                self.np.set(1, 0x000000, num=half_strip)
                if self._wait_and_exit(20): return

            for x in range(3):
                self.np.set(half_strip + 1, 0x0000ff, num=half_strip)
                if self._wait_and_exit(30): return
                self.np.set(half_strip + 1, 0x000000, num=half_strip)
                if self._wait_and_exit(20): return

            if self._wait_and_exit(super().speed): return
