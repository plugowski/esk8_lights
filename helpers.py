from config import Config
from machine import reset as machine_reset
import utime


def factory_reset(irq):
    """ Interrupt trigger for reset button, when hold more than 10s all configs will be restored to default
    """
    start = irq.value()
    utime.sleep(10)
    if irq.value() == start:
        Config().reset()
        machine_reset()
    else:
        irq.init(handler=factory_reset)
