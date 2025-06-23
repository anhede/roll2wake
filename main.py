import time

from components.buzzer import Buzzer
from components.screen import Screen
from components.pushbutton import PushButton
from components.potentiometer import Potentiometer
from components.neopixelcircle import NeopixelCircle
from components.utils import time_string, smart_wrap
from components.distsensor import Distsensor

from client.client import Client
from client.wifi_client import WifiClient

DEEP_SLEEP_MS = 10000
SLEEP_MS = 5000


class AlarmState:
    def __init__(self, choice=0, hour=8, minute=0, is_on=False):
        self.__choice = 0  # 0: On/Off, 1: Hour, 2: Minute
        self.__hour = hour
        self.__minute = minute
        self.__is_on = is_on
        self.__just_changed = True
        self.__last_change_ms = time.ticks_ms()

    def choice(self, choice: int | None = None):
        # Set
        if choice is not None and choice != self.__choice:
            self.just_changed(True)
            self.__choice = choice
            return None

        # Get
        return self.__choice

    def hour(self, hour: int | None = None):
        # Set
        if hour is not None and hour != self.__hour:
            self.just_changed(True)
            self.__hour = hour
            return None

        # Get
        return self.__hour

    def minute(self, minute: int | None = None):
        # Set
        if minute is not None and minute != self.__minute:
            self.just_changed(True)
            self.__minute = minute
            return None

        # Get
        return self.__minute

    def is_on(self, is_on: bool | None = None):
        # Set
        if is_on is not None and is_on != self.__is_on:
            self.just_changed(True)
            self.__is_on = is_on
            return None

        # Get
        return self.__is_on

    def just_changed(self, just_changed: bool | None = None):
        # Set
        if just_changed is not None:
            self.__just_changed = just_changed
            self.__last_change_ms = time.ticks_ms()
            return None

        # Get
        if self.__just_changed:
            self.__just_changed = False
            return True
        return False

    def ms_since_last_change(self):
        """
        Returns the milliseconds since the last change.
        """
        return time.ticks_diff(time.ticks_ms(), self.__last_change_ms)


def main():
    """
    Main function to initialize components and run the interactive story routine.
    """
    # Initialize components
    screen = Screen(20, 21)
    pot = Potentiometer(28)
    button = PushButton(15)
    neopix = NeopixelCircle(16, brightness=0.1)
    distsensor = Distsensor(trigger_pin=7, echo_pin=6)

    buzzer = Buzzer(14)

    # Initialize client
    wifi_client = WifiClient()
    client = Client("http://192.168.1.234:5000")

    # State loop
    state = AlarmState()
    screen.set_cursor(True)
    msg = ""
    sleep = False
    deep_sleep = False
    last_dist_was_close_ms = 0
    while True:
        if not button.is_held():
            choice = pot.read_discrete(6) % 3
            state.choice(choice)

        if state.choice() == 0:
            if button.is_pressed():
                state.is_on(not state.is_on())

        elif state.choice() == 1:
            if button.is_held():
                hour = pot.read_discrete(24)
                state.hour(hour)

        elif state.choice() == 2:
            if button.is_held():
                minute = pot.read_discrete(60)
                state.minute(minute)

        # Display updated settings
        if state.just_changed():
            sleep = False
            deep_sleep = False
            screen.set_backlight(True)
            msg_alarm = f"Alarm {' On' if state.is_on() else 'Off'}".center(screen.cols)
            msg_time = f"Time: {state.hour():02}:{state.minute():02}".center(
                screen.cols
            )
            msg = "\n".join([msg_alarm, msg_time])
            screen.message(msg)

            # Update cursor
            row = 0
            steps_back = 0
            if state.choice() == 0:
                row = 0
                steps_back = 0
            elif state.choice() == 1:
                row = 1
                steps_back = 3
            elif state.choice() == 2:
                row = 1
                steps_back = 0
            cursor_col = len(msg.split("\n")[row].rstrip()) - steps_back - 1
            screen.set_cursor_position(row, cursor_col)

        if not sleep and state.ms_since_last_change() > SLEEP_MS:
            sleep = True
            msg_time = time_string(include_seconds=False, prefix_day_of_week=True)
            msg_alarm = (
                f"Wake at {state.hour():02}:{state.minute():02}"
                if state.is_on()
                else ""
            )
            msg = "\n".join([msg_time, msg_alarm])
            screen.message(msg, center=True)

        if (
            not deep_sleep
            and state.ms_since_last_change() > DEEP_SLEEP_MS
            and time.ticks_diff(time.ticks_ms(), last_dist_was_close_ms)
            > DEEP_SLEEP_MS - SLEEP_MS
        ):
            deep_sleep = True
            screen.set_backlight(False)

        if distsensor.is_close():
            print(f"close at {distsensor.distance_cm():.2f} cm")
            last_dist_was_close_ms = time.ticks_ms()
            screen.set_backlight(True)
            deep_sleep = False

        time.sleep_ms(50)


if __name__ == "__main__":
    main()
