import time
from machine import I2C, Pin
from components.lcd1602 import LCD
from components.utils import smart_wrap

class Screen:
    """
    A high-level class to handle an LCD1602 display using I2C communication.
    """

    def __init__(self, pin_sda: int, pin_scl: int, freq_ghz=0.4, rows=4, cols=20):
        freq = int(freq_ghz * 1e6)  # Convert MHz to Hz
        i2c = I2C(0, sda=Pin(pin_sda), scl=Pin(pin_scl), freq=freq)
        self.lcd = LCD(i2c)
        self.rows = rows
        self.cols = cols

    def message(self, string, clear=True, center=False, autosplit=True):
        """
        Display a message on the LCD.
        - string can contain '\n'
        - if center=True, text is centered both horizontally and vertically,
        with any extra blank line at the bottom.
        """
        if clear:
            self.lcd.clear()

        # 1) Break into lines (manual '\n' or autosplit)
        if '\n' in string:
            lines = string.split('\n')
        elif autosplit:
            wrapped = smart_wrap(string, row_len=self.cols, max_rows=self.rows)
            lines = wrapped.split('\n')
        else:
            lines = [string]

        # Trim to max rows
        if len(lines) > self.rows:
            lines = lines[:self.rows]

        # Prepare an all-blank row
        blank = ' ' * self.cols

        if center:
            # 2) Horizontal center each line
            for i in range(len(lines)):
                line = lines[i]
                if len(line) < self.cols:
                    pad_left = (self.cols - len(line)) // 2
                    pad_right = self.cols - len(line) - pad_left
                    lines[i] = (' ' * pad_left) + line + (' ' * pad_right)
                else:
                    lines[i] = line[:self.cols]

            # 3) Vertical centering
            top_pad = (self.rows - len(lines)) // 2
            padded = [blank] * top_pad + lines
            # fill bottom
            while len(padded) < self.rows:
                padded.append(blank)
            lines = padded

        else:
            # Left-justify (fill or truncate)
            for i in range(len(lines)):
                line = lines[i]
                if len(line) < self.cols:
                    lines[i] = line + (' ' * (self.cols - len(line)))
                else:
                    lines[i] = line[:self.cols]

        # 4) Send to LCD
        # Most Micropython HD44780 drivers treat '\n' as "move to next line"
        self.lcd.message('\n'.join(lines))

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
    from components.pins import PIN_SCREEN_SDA, PIN_SCREEN_SCL
    # Example usage of the Screen class
    # SDA Pin 20, SCL Pin 21, frequency 400kHz
    screen = Screen(PIN_SCREEN_SDA, PIN_SCREEN_SCL)

    # Test all lines
    msg = '\n'.join([f"Line {i+1}:" for i in range(screen.rows)])
    screen.message(msg)
    time.sleep(2)  # Wait for 2 seconds

    # Test centering and autosplitting
    screen.message(
        "This message is too long to fit on one line.", center=True, autosplit=True
    )
    time.sleep(2)  # Wait for 2 seconds

    # Test vertical centering
    screen.message(
        "This message fits on two lines.", center=True, autosplit=True
    )
    time.sleep(2)  # Wait for 2 seconds

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
        screen.message(f"Time: {current_time} ms\nSince start")
        time.sleep_ms(250)
