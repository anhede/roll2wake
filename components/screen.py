import time
from components.lcd1602 import LCD

class Screen:
    """
    A high-level class to handle an LCD1602 display using I2C communication.
    """

    def __init__(self, pin_sda: int, pin_scl: int, freq_ghz=0.4):
        freq = int(freq_ghz * 1e6)  # Convert MHz to Hz
        i2c = I2C(0, sda=Pin(pin_sda), scl=Pin(pin_scl), freq=freq)
        self.lcd = LCD(i2c)

    def message(self, string):
        """
        Display a message on the LCD.
        The string can contain '\n' for new lines.
        """
        self.lcd.message(string)

    def clear(self):
        """
        Clear the LCD display.
        """
        self.lcd.clear()

if __name__ == "__main__":
    from machine import I2C, Pin

    # Example usage of the Screen class
    # SDA Pin 20, SCL Pin 21, frequency 400kHz
    screen = Screen(20, 21)

    start = time.ticks_ms()
    while True:
        # Display time since start
        current_time = time.ticks_ms() - start
        screen.clear()
        screen.message(f"Time: {current_time } ms\n"
                        f"Since start")
        time.sleep_ms(250)