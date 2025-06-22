import time
from machine import I2C, Pin
from components.lcd1602 import LCD
from components.utils import smart_wrap

class Screen:
    """
    A high-level class to handle an LCD1602 display using I2C communication.
    """

    def __init__(self, pin_sda: int, pin_scl: int, freq_ghz=0.4, rows=2, cols=16):
        freq = int(freq_ghz * 1e6)  # Convert MHz to Hz
        i2c = I2C(0, sda=Pin(pin_sda), scl=Pin(pin_scl), freq=freq)
        self.lcd = LCD(i2c)
        self.rows = rows
        self.cols = cols

    def message(self, string: str, clear=True, center=False, autosplit=True):
        """
        Display a message on the LCD.
        The string can contain '\n' for new lines.
        """
        if clear:
            self.lcd.clear()

        # Format the string for display
        formatted_string = string
        if "\n" in string:  # Manual line breaks
            lines = string.split("\n")
            if center:
                # Center each line
                lines = [line.center(self.cols) for line in lines]
            formatted_string = "\n".join(lines)

        elif autosplit:  # Auto split long strings
            formatted_string = smart_wrap(
                string, row_len=self.cols, max_rows=self.rows, center=center
            )

        self.lcd.message(formatted_string)

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

    def set_cursor(self, on : bool):
        """
        Set the cursor visibility.
        :param on: True to show the cursor, False to hide it.
        """
        if on:
            self.lcd.enableCursor()
        else:
            self.lcd.disableCursor()

    def set_cursor_position(self, row: int, col: int):
        """
        Set the cursor position on the LCD.
        :param row: Row number (0 or 1).
        :param col: Column number (0 to cols-1).
        """
        self.lcd.setCursor(row, col)

if __name__ == "__main__":
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

    # Test centering and autosplitting
    screen.message(
        "This message is too long to fit on one line.", center=True, autosplit=True
    )
    time.sleep(2)  # Wait for 2 seconds

    start = time.ticks_ms()
    while True:
        # Display time since start
        current_time = time.ticks_ms() - start
        screen.message(f"Time: {current_time} ms\nSince start")
        time.sleep_ms(250)
