import time
from machine import Pin

HANGTIME_MS = 200

class Buzzer:
    """
    A class to handle an active 3 V DC buzzer.
    Assumes that driving the pin HIGH turns the buzzer on.
    Enforces a minimum interval between beeps to prevent continuous drive.
    """

    def __init__(self, pin: int):
        self._buzzer = Pin(pin, Pin.OUT)
        self._buzzer.value(0)  # ensure buzzer is off
        self._min_beep_ms = HANGTIME_MS
        self._last_beep_time = time.ticks_ms() - self._min_beep_ms

    def on(self):
        """Turn the buzzer on (continuous tone)."""
        self._buzzer.value(1)

    def off(self):
        """Turn the buzzer off."""
        self._buzzer.value(0)

    def beep(self, duration_ms: int) -> bool:
        """
        Beep the buzzer for the specified duration (in ms), if at least 
        `min_beep_ms` has elapsed since the last beep start.
        Returns true if the beep was emitted, False if skipped due to minimum
        interval.
        """
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_beep_time) < self._min_beep_ms:
            return False

        # record start time
        self._last_beep_time = now
        # sound the buzzer
        self._buzzer.value(1)
        time.sleep_ms(duration_ms)
        self._buzzer.value(0)
        return True


if __name__ == "__main__":
    from components.pins import PIN_BUZZER
    tone_ms = 50
    buzzer = Buzzer(PIN_BUZZER)

    try:
        while True:
            if buzzer.beep(tone_ms):
                print("Beep!")
            else:
                print("Skipped—too soon")
            time.sleep(1)  # wait 1 s before attempting the next beep
    except KeyboardInterrupt:
        buzzer.off()
        print("Stopped.")
