import time
from components.screen import Screen
from components.pushbutton import PushButton
from components.buzzer import Buzzer
from components.utils import time_string

class AlarmNoise:
    def __init__(self, start_time_ms: int, buzzer: Buzzer):
        self.start_time_ms = start_time_ms
        self.buzzer = buzzer

    def update(self) -> None:
        """
        Plays a short specific noise pattern for the alarm.
        """
        pass

class OnOffAlarmNoise(AlarmNoise):
    """
    Default, on-off noise pattern for the alarm.
    """
    ON_INTERVAL_MS = 100
    OFF_INTERVAL_MS = 900

    def update(self) -> None:
        should_beep = time.ticks_diff(time.ticks_ms(), self.start_time_ms) % (self.ON_INTERVAL_MS + self.OFF_INTERVAL_MS) < self.ON_INTERVAL_MS
        if should_beep:
            self.buzzer.on()
        else:
            self.buzzer.off()

class AscendingAlarmNoise(AlarmNoise):
    """
    A noise pattern that slowly increases the beep frequency.
    """
    # (number of beeps in this stage, interval between beeps in ms)
    INTERVAL_LIST = [
        (5, 3000),  # 5 beeps, one every 3000 ms
        (5, 2000),  # then 5 beeps, one every 2000 ms
        (-1, 1000), # then indefinitely, one every 1000 ms
    ]
    BEEP_DURATION_MS = 100  # how long each beep stays on

    def __init__(self, start_time_ms: int, buzzer: Buzzer):
        super().__init__(start_time_ms, buzzer)
        self._interval_index = 0
        self._beep_count = 0
        self._beep_start_time = start_time_ms

    def update(self) -> None:
        """
        Called repeatedly — turns the buzzer on for BEEP_DURATION_MS at each
        interval, steps through INTERVAL_LIST, and then holds at the last stage.
        """
        now = time.ticks_ms()
        count, interval = self.INTERVAL_LIST[self._interval_index]
        elapsed = time.ticks_diff(now, self._beep_start_time)

        # 1) Turn buzzer on for the first BEEP_DURATION_MS of the interval
        if elapsed < self.BEEP_DURATION_MS:
            self.buzzer.on()
        else:
            self.buzzer.off()

        # 2) If we've reached or passed the full interval, advance to next beep
        if elapsed >= interval:
            # consume exactly one interval (avoiding drift)
            self._beep_start_time = time.ticks_add(self._beep_start_time, interval)
            self._beep_count += 1

            # 3) If this stage had a finite count and we've done them all, go next
            if count > 0 and self._beep_count >= count:
                if self._interval_index < len(self.INTERVAL_LIST) - 1:
                    self._interval_index += 1
                    self._beep_count = 0
                # else: last stage is infinite, so stay here indefinitely
 
        

def alarm(screen: Screen, pushb: PushButton, buzzer: Buzzer) -> None:
    """
    Displays the wake-up time on the screen and waits for the user to acknowledge the alarm.
    """
    msg = f"Wake up bro!\n{time_string(include_seconds=False, prefix_day_of_week=True)}"
    screen.message(msg, center=True)
    
    # Wait for the button to be pressed
    alarm_noise = AscendingAlarmNoise(time.ticks_ms(), buzzer)
    while not pushb.is_pressed():
        alarm_noise.update()
        #time.sleep_ms(10)
    
    # Clear the screen after acknowledgment
    buzzer.off()
    screen.clear()

if __name__ == "__main__":
    # Example usage
    screen = Screen(20, 21)
    pushb = PushButton(15)
    buzzer = Buzzer(14)
    
    # Simulate an alarm
    alarm(screen, pushb, buzzer)