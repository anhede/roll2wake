import time
from machine import ADC, Pin

class Potentiometer:
    """
    A class to read values from a potentiometer connected to an ADC pin,
    with hysteresis in the discrete read to avoid jitter at bin edges.
    """
    def __init__(self, pin: int):
        self.adc_pin = ADC(pin)
        self._last_bin = None    # remember last discrete value

    def read_u16(self):
        return self.adc_pin.read_u16()

    def read_voltage(self, reference_voltage=3.3):
        value = self.read_u16()
        return value * reference_voltage / 65535

    def read_normalized(self):
        return self.read_u16() / 65535

    def read_discrete(self, steps=8):
        """
        Reads the normalized pot value and returns a bin in [0, steps-1],
        but only moves to a new bin once the reading crosses the midpoint
        between the old and new bin (hysteresis = half a bin width).
        """
        v = self.read_normalized()
        raw = min(int(v * steps), steps - 1)

        # first call: just set and return
        if self._last_bin is None:
            self._last_bin = raw
            return raw

        # midpoint between bins in normalized units
        upper_mid = (self._last_bin + 0.5) / steps
        lower_mid = (self._last_bin - 0.5) / steps

        # only bump up if we've crossed halfway into the next bin
        if raw > self._last_bin and v > upper_mid:
            self._last_bin = raw
        # only bump down if we've crossed halfway into the previous bin
        elif raw < self._last_bin and v < lower_mid:
            self._last_bin = raw

        return self._last_bin

if __name__ == "__main__":
    pot = Potentiometer(28)
    led = Pin("LED", Pin.OUT)
    led.on()

    while True:
        u16 = pot.read_u16()
        voltage = pot.read_voltage()
        normalized = pot.read_normalized()
        discrete = pot.read_discrete()

        print(f"{u16:5d} - {voltage:5.2f}V - {normalized:5.2f} - {discrete:2d}", end="\r")
        time.sleep(0.2)
