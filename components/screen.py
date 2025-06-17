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

    def message(self, string, clear = True):
        """
        Display a message on the LCD.
        The string can contain '\n' for new lines.
        """
        if clear:
            self.lcd.clear()
        self.lcd.message(string)

    def clear(self):
        """
        Clear the LCD display.
        """
        self.lcd.clear()

    def set_backlight(self, on: bool):
        """
        Set the backlight of the LCD.
        :param on: True to turn on, False to turn off.
        """
        if on:
            self.lcd.enableBacklight()
        else:
            self.lcd.disableBacklight()

if __name__ == "__main__":
    from machine import I2C, Pin

    # Example usage of the Screen class
    # SDA Pin 20, SCL Pin 21, frequency 400kHz
    screen = Screen(20, 21)

    screen.message("Goodbye World!")
    time.sleep(2)  # Wait for 2 seconds

    screen.set_backlight(False)  # Turn off the backlight
    time.sleep(2)  # Wait for 2 seconds

    screen.set_backlight(True)  # Turn on the backlight
    screen.message("Hello World!")
    time.sleep(2)  # Wait for 2 seconds

    start = time.ticks_ms()
    while True:
        # Display time since start
        current_time = time.ticks_ms() - start
        screen.message(f"Time: {current_time } ms\n"
                        f"Since start")
        time.sleep_ms(250)