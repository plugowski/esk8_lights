from machine import Pin, PWM
import asyn


class Lights:

    DEFAULT_FREQ = 200
    DEFAULT_INTENSITY = 512

    STATE_OFF = 0
    STATE_ON = 1023

    COLORS = [
        [1, 0, 0],  # red
        [1, 1, 0],  # yellow
        [0, 1, 0],  # green
        [0, 1, 1],  # cyan
        [0, 0, 1],  # blue
        [1, 0, 1],  # purple
    ]

    rgb_matrix = []
    tail_light = None
    front_light = None

    def __init__(self, red: int, green: int, blue: int, front: int = None, back: int = None):
        self.rgb_matrix = [
            PWM(Pin(red, Pin.OUT, value=0), freq=self.DEFAULT_FREQ, duty=self.STATE_OFF),
            PWM(Pin(green, Pin.OUT, value=0), freq=self.DEFAULT_FREQ, duty=self.STATE_OFF),
            PWM(Pin(blue, Pin.OUT, value=0), freq=self.DEFAULT_FREQ, duty=self.STATE_OFF)
        ]
        self.front_light = None if front is None else PWM(Pin(front, Pin.OUT, value=0), freq=self.DEFAULT_FREQ, duty=self.STATE_OFF)
        # self.front_light = None if front is None else Pin(front, Pin.OUT, value=0)
        self.tail_light = None if back is None else PWM(Pin(back, Pin.OUT, value=0), freq=self.DEFAULT_FREQ, duty=self.STATE_OFF)

    def tail(self, intensity: int):
        if self.tail_light is not None:
            self.tail_light.duty(intensity)

    def front(self, intensity: int):
        if self.front_light is not None:
            self.front_light.duty(intensity)

    @asyn.cancellable
    async def rgb_color(self, hex_color: str, intensity: int = DEFAULT_INTENSITY) -> None:
        """ Set RGB color for lights, based on HEX string
        """
        rgb = list(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        self._set_color(rgb, intensity)

    @asyn.cancellable
    async def rgb_jump(self, mode: int = 2, speed: float = 0.1, intensity: int = DEFAULT_INTENSITY) -> None:
        """ Change colors in sequence, two modes #1 - six colors or #2 basic three colors (RGB)
        """
        while True:
            for step, color in enumerate(self.COLORS):
                if mode == 2 and (step + 1) % 2 == 0:
                    continue

                self._set_color(map(lambda x: x * 255, color), intensity)
                await asyn.sleep(speed, 10)

    @asyn.cancellable
    async def rgb_fade(self, period: float, intensity: int = DEFAULT_INTENSITY) -> None:
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

                self._set_color(map(lambda x: x / steps * 255, rgb), intensity)
                await asyn.sleep(0.01, 10)

    @asyn.cancellable
    async def rgb_police(self, intensity: int = DEFAULT_INTENSITY) -> None:
        """ Flash RGB like police lights (red and blue)
        """
        while True:
            await self._blink(self.rgb_matrix[0], intensity)
            await self._blink(self.rgb_matrix[2], intensity)

    def rgb_reset(self) -> None:
        """ Reset RGB PWMs to neutral state
        """
        for pin in self.rgb_matrix:
            pin.freq(self.DEFAULT_FREQ)
            pin.duty(self.STATE_OFF)

    async def rgb_cancel(self):
        """ Cancel all working coros and reset RGB lights
        """
        await asyn.Cancellable.cancel_all()
        self.rgb_reset()

    def _set_color(self, color: iter, intensity: int = DEFAULT_INTENSITY) -> None:
        """ Set specified color for RGB Pins, expected list with values of each color in range 0-255
        """
        for pin, value in enumerate(color):
            self.rgb_matrix[pin].duty(int(float(value)/255 * intensity))

    @staticmethod
    async def _blink(led: PWM, intensity: int = DEFAULT_INTENSITY) -> None:
        """ Blink led 3 times and wait
        """
        led.freq(10)
        led.duty(intensity)
        await asyn.sleep(0.3, 10)
        led.duty(0)
        await asyn.sleep(0.2, 10)

    def status(self) -> dict:
        """ Return actual lights status...
        """
        return {
            'rgb': {
                'mode': '',
                'r': self.rgb_matrix[0].duty(),
                'g': self.rgb_matrix[1].duty(),
                'b': self.rgb_matrix[2].duty()
            },
            'front': self.front_light.duty(),
            'tail': self.tail_light.duty(),
        }

