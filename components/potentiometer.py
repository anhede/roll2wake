import time
from machine import ADC, Pin


class Potentiometer:
    """
    A class to read values from a potentiometer connected to an ADC pin.
    """

    def __init__(self, pin: int):
        self.adc_pin = ADC(pin)

    def read_u16(self):
        """
        Reads the ADC value from the potentiometer pin as a 16-bit unsigned integer.
        """
        return self.adc_pin.read_u16()

    def read_voltage(self, reference_voltage=3.3):
        """
        Reads the voltage from the potentiometer pin and converts it to a float voltage.
        """
        value = self.read_u16()
        voltage = value * reference_voltage / 65535
        return voltage

    def read_normalized(self):
        """
        Reads the normalized value from the potentiometer pin.
        Normalized value is between 0.0 and 1.0.
        """
        value = self.read_u16()
        return value / 65535

    def read_discrete(self, steps=8):
        """
            Reads the discrete value from the potentiometer pin.
            Discrete value is between 0 and steps-1.
            """
        value_norm = self.read_normalized()
        bin_index = int(value_norm * steps)
        return min(bin_index, steps - 1)

if __name__ == "__main__":
    pot = Potentiometer(28)  # Assuming GP28 is used for the potentiometer
    led = Pin("LED", Pin.OUT)
    led.on()

    while True:
        u16 = pot.read_u16()
        voltage = pot.read_voltage()
        normalized = pot.read_normalized()
        discrete = pot.read_discrete()

        print(f"{u16:5d} - {voltage:5.2f}V - {normalized:5.2f} - {discrete:2d}", end="\r")

        time.sleep(0.2)
