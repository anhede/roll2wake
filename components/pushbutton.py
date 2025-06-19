import time
from machine import Pin


class PushButton:
    """
    A class to handle a momentary pushbutton with minimum click interval.
    Assumes active low logic, i.e. wired to ground when pressed.
    """

    def __init__(self, pin: int, min_click_ms=100):
        # choose pull based on active level
        self._pin = Pin(pin, Pin.IN, pull=Pin.PULL_UP)
        self._min_click_ms = min_click_ms
        self._last_click_time = time.ticks_ms() - min_click_ms  # allow immediate press
        self._last_held = False

    def is_pressed(self):
        """
        Returns True if the button has just been pressed.
        """
        now = time.ticks_ms()

        # check for release
        if self._last_held:
            if not self.__raw_is_pressed():
                # button released
                self._last_held = False
            else:
                # still held, no click
                return False

        # check hangtime
        if time.ticks_diff(now, self._last_click_time) < self._min_click_ms:
            return False
        
        # check for valid click
        if self.__raw_is_pressed():
            self._last_click_time = now
            self._last_held = True
            return True
        return False
    
    def is_held(self):
        """
        Returns True if the button is currently pressed (active low).
        This is a more advanced check that allows for continuous press detection.
        """
        if self.__raw_is_pressed():
            self._last_held = True
            return True
        else:
            self._last_held = False
            return False
    
    def __raw_is_pressed(self):
        """
        Returns True if the button is currently pressed (active low).
        Dumb method that does no advanced checking.
        """
        if self._pin.value() == 0:
            self._last_held = True
            return True
        return False


if __name__ == "__main__":
    hangtime_ms = 100  # milliseconds
    button = PushButton(15, min_click_ms=hangtime_ms)
    led = Pin("LED", Pin.OUT)
    led.off()

    while True:
        if button.is_pressed():
            led.toggle()
            print("Button pressed! LED is now", "ON" if led.value() else "OFF")
        time.sleep_ms(50)
