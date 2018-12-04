from machine import ADC, Pin


class Battery:
    """ Read battery status from input source
    """
    def __init__(self, adc: int, min_value: float = 6.4, max_value: float = 8.4):
        self.adc = ADC(Pin(adc))
        self.adc.atten(ADC.ATTN_11DB)
        self.min = min_value
        self.max = max_value

    def status(self) -> dict:
        voltage = self.adc.read() / 4095 * self.max
        percentage = 0 if voltage < self.min else round((voltage - self.min) / (self.max - self.min) * 100, 2)

        return {
            'voltage': voltage,
            'percentage': percentage
        }
