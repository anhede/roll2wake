import time

from components.buzzer import Buzzer
from components.screen import Screen
from components.pushbutton import PushButton
from components.potentiometer import Potentiometer
from components.neopixelcircle import NeopixelCircle
from components.utils import time_string, smart_wrap, get_iso_timestamp
from components.distsensor import Distsensor

from client.client import Client
from client.wifi_client import WifiClient

from routines.alarm import alarm
from routines.interactive_story import interactive_story
from server.stats import STAT_INTERACTION, STAT_WAKEUP, Statistics

DEEP_SLEEP_MS = 5000
SLEEP_MS = 3000
ALARM_STATE_CHANGE_FREEZE_MS = 2000  # Prevents the alarm from going off immediately after setting it
QUICK_ALARM_TOGGLE_SCREEN_MS = 200  # Time to enable screen after quick alarm toggle


class AlarmState:
    def __init__(self, choice=0, hour=8, minute=0, is_on=False):
        self.__choice = 0  # 0: On/Off, 1: Hour, 2: Minute
        self.__hour = hour
        self.__minute = minute
        self.__is_on = is_on
        self.__just_changed = True
        self.__last_change_ms = -100000
        self.__last_fired_ms = time.ticks_ms() - 120 * 1000  # Set to 2 minutes ago to allow immediate firing

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
    
    def silent_is_on(self, is_on: bool | None = None):
        """
        Set or get the alarm state without triggering a change.
        """
        if is_on is not None:
            self.__is_on = is_on
            return None
        return self.__is_on

    def just_changed(self, just_changed: bool | None = None):
        # Set
        if just_changed is not None:
            time_since_last_change = time.ticks_diff(time.ticks_ms(), self.__last_change_ms)
            if time_since_last_change > 1000 * 60:  # More than a minute since last change
                publish_interaction()
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

    def just_fired(self):
        """
        Tell the alarm that it just fired.
        """
        self.__last_fired_ms = time.ticks_ms()

    def armed(self):
        """
        Is the alarm ready to go off?
        """
        if time.ticks_diff(time.ticks_ms(), self.__last_fired_ms) < 120 * 1000:
            return False
        return True

def main():
    """
    Main function to initialize components and run the interactive story routine.
    """
    time.sleep(3)  # Allow time for the system to stabilize
    import components.pins as pins
    screen = Screen(pins.PIN_SCREEN_SDA, pins.PIN_SCREEN_SCL)
    pot = Potentiometer(pins.PIN_POT)
    button = PushButton(pins.PIN_BUTTON)
    neopix = NeopixelCircle(pins.PIN_NEOPIXEL, brightness=0.1)
    distsensor = Distsensor(trigger_pin=pins.PIN_DIST_TRIG, echo_pin=pins.PIN_DIST_ECHO)

    buzzer = Buzzer(pins.PIN_BUZZER)

    # Initialize client
    screen.message("Connecting to WiFi...", center=True)
    _ = WifiClient()
    screen.message("Connecting to server...", center=True)
    global client
    client = Client("http://192.168.1.110:5000")
    screen.message("Connections established", center=True)
    time.sleep(1)

    # State loop
    state = AlarmState()
    screen.set_cursor(True)
    sleep = False
    deep_sleep = False
    last_dist_was_close_ms = 0
    last_time_string = ""
    while True:
        update_alarm_state(pot, button, state, sleep)

        # Display updated settings
        if state.just_changed():
            sleep = False
            deep_sleep = False
            display_alarm_state(screen, state)
            last_time_string = "" # Forget the last time string to force update

        if not sleep and state.ms_since_last_change() > SLEEP_MS:
            sleep = True
            last_time_string = display_sleep_state(screen, state, last_time_string)

        if not deep_sleep and sleep:
            last_time_string = display_sleep_state(screen, state, last_time_string)

        if (
            not deep_sleep
            and state.ms_since_last_change() > DEEP_SLEEP_MS
            and time.ticks_diff(time.ticks_ms(), last_dist_was_close_ms)
            > DEEP_SLEEP_MS - SLEEP_MS
        ):
            deep_sleep = True
            screen.set_backlight(False)

        if distsensor.is_close() and deep_sleep:
            while distsensor.is_close():
                last_dist_was_close_ms = time.ticks_ms()
                screen.set_backlight(True)
                deep_sleep = False
                time.sleep_ms(50)

        if sleep and button.is_pressed():
            # If the button is pressed while in sleep mode, 
            # toggle the alarm state
            start_time = time.ticks_ms()
            press_duration = 0
            while button.is_held() and press_duration < 1000:
                # Wait for the button to be released
                time.sleep_ms(50)
                press_duration = time.ticks_diff(time.ticks_ms(), start_time)
            if press_duration < 1000:
                state.silent_is_on(not state.silent_is_on())
                screen.set_backlight(True)
                deep_sleep = False
                last_time_string = display_sleep_state(screen, state, last_time_string)
                publish_interaction()
            else:
                # Immediately start the interactive story if the button is held
                sleep = False
                deep_sleep = False
                screen.set_backlight(True)
                time_to_hold = int(3)
                while button.is_held() and time_to_hold > 0:
                    screen.message(f"Starting story in {time_to_hold}...", center=True)
                    time.sleep(1)
                    time_to_hold -= 1
                if time_to_hold == 0:
                    try:
                        interactive_story(client, screen, pot, neopix, button)
                    except Exception as e:
                        print(f"Error in interactive story: {e}")
                        screen.message("Error occurred", center=True)
                        time.sleep(2)
                else:
                    last_time_string = display_sleep_state(screen, state, last_time_string)

        # Check if it's time to wake up
        if should_wake_up(state):
            sleep = False
            deep_sleep = False
            screen.set_backlight(True)
            state.is_on(False)  # Turn off the alarm after firing
            state.just_fired()
            alarm(screen, button, buzzer)
            try:
                client.publish_statistics(
                    Statistics(
                        STAT_WAKEUP,
                        0.0,
                        get_iso_timestamp(),
                    )
                )
                interactive_story(client, screen, pot, neopix, button)
            except Exception as e:
                print(f"Error in interactive story: {e}")
                screen.message("Error occurred", center=True)
                time.sleep(2)
            screen.set_cursor(True)

        #print(f"Sleep: {sleep}, Deep Sleep: {deep_sleep}, Armed: {state.armed()}, Choice: {state.choice()}     ", end="\r")
        time.sleep_ms(50)

def publish_interaction():
    client.publish_statistics(
                Statistics(
                    STAT_INTERACTION,
                    0.0,
                    get_iso_timestamp(),
                )
            )

def should_wake_up(state: AlarmState) -> bool:
    """
    Check if the current time matches the alarm time and the alarm is on.
    """
    if not state.armed():
        return False
    current_hour = time.localtime()[3]  # Hour
    current_minute = time.localtime()[4]  # Minute
    if (state.is_on()
        and state.ms_since_last_change() > ALARM_STATE_CHANGE_FREEZE_MS
        and state.hour() == current_hour
        and state.minute() == current_minute):
        state.just_fired()
        return True
    return False

def display_sleep_state(screen: Screen, state, last_time_string):
    screen.set_cursor(False)
    msg_time = time_string(include_seconds=False, prefix_day_of_week=True)
    msg_alarm = (
        f"Wake at {state.hour():02}:{state.minute():02}" if state.is_on() else ""
    )
    msg = "\n".join([msg_time, msg_alarm])
    if msg != last_time_string:
        screen.message(msg, center=True)
    return msg


def display_alarm_state(screen: Screen, state):
    screen.set_backlight(True)
    screen.set_cursor(True)
    msg_alarm = f"Alarm {' On' if state.is_on() else 'Off'}".center(screen.cols)
    msg_time = f"Time: {state.hour():02}:{state.minute():02}".center(screen.cols)
    msg = "\n".join([msg_alarm, msg_time])
    screen.message(msg, center=True)

    # Update cursor
    # two rows -> 0th line, four rows -> 1st line
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
    centering_adjust = screen.rows // 2 - 1
    cursor_col = len(msg.split("\n")[row].rstrip()) - steps_back - 1
    screen.set_cursor_position(row + centering_adjust, cursor_col)


def update_alarm_state(pot, button, state, sleep):
    if not button.is_held():
        choice = pot.read_discrete(6) % 3
        state.choice(choice)

    if sleep:
        return

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


if __name__ == "__main__":
    main()
