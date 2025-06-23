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
        self._is_pressed_lock = False

    def is_pressed(self):
        """
        Returns True if the button has just been pressed.
        """
        now = time.ticks_ms()

        # check for release
        if self._is_pressed_lock:
            if not self.__raw_is_pressed():
                # button released
                self._is_pressed_lock = False
            else:
                # still held, no click
                return False

        # check hangtime
        if time.ticks_diff(now, self._last_click_time) < self._min_click_ms:
            return False
        
        # check for valid click
        if self.__raw_is_pressed():
            self._last_click_time = now
            self._is_pressed_lock = True
            return True
        return False
    
    def is_held(self):
        """
        Returns True if the button is currently pressed (active low).
        This is a more advanced check that allows for continuous press detection.
        """
        if self.__raw_is_pressed():
            return True
        else:
            return False
    
    def __raw_is_pressed(self):
        """
        Returns True if the button is currently pressed (active low).
        Dumb method that does no advanced checking.
        """
        if self._pin.value() == 0:
            return True
        return False


if __name__ == "__main__":
    hangtime_ms = 100  # milliseconds
    button = PushButton(15, min_click_ms=hangtime_ms)
    led = Pin("LED", Pin.OUT)
    led.off()

    while True:
        is_pressed = button.is_pressed()
        is_held = button.is_held()
        print(f"pressed: {is_pressed}, held: {is_held}      ", end="\r")
        time.sleep_ms(20)
