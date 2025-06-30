import time

from components.screen import Screen
from components.pushbutton import PushButton
from components.potentiometer import Potentiometer
from components.neopixelcircle import NeopixelCircle
from components.utils import smart_wrap

from client.client import Client
from client.wifi_client import WifiClient
from routines.scroll_read import scroll_read
from routines.choicemenu import choice_menu
from routines.dndroll import dnd_roll
from server.models import (
    StoryBeat,
    Choice,
    MODE_ADVANTAGE,
    MODE_DISADVANTAGE,
    MODES_SYMBOLS,
)


def interactive_story(
    client: Client,
    screen: Screen,
    pot: Potentiometer,
    neopix: NeopixelCircle,
    button: PushButton,
):
    """
    Displays an interactive story on the screen and controls the neopixel circle.
    """

    message_wait_story(screen)
    beat = client.get_new_story()
    screen.set_cursor(False)
    while True:
        formatted_text = beat.beat_text.replace("\n", " ").strip()
        formatted_text = smart_wrap(
            formatted_text,
            row_len=screen.cols,
            max_rows=100,
        )
        scroll_read(screen, pot, button, formatted_text)
        if beat.is_ending:
            scroll_read(
                screen, pot, button, "The story has ended. Thank you for playing!"
            )
            return
        prompts = []
        for choice in beat.choices:
            prompts.append(
                f"{choice.choice_id}: {choice.label} ({choice.difficulty}{MODES_SYMBOLS[choice.mode]})"
            )
        choice_id = (
            choice_menu(
                prompts,
                neopix,
                screen,
                pot,
                button,
            )
            + 1
        )  # +1 to match choice_id starting from 1
        choice = beat.choices[choice_id - 1]
        success = dnd_roll(choice.difficulty, choice.mode, screen, button, neopix)
        message_wait_story(screen)
        neopix.clear()
        beat = client.update_story(choice_id, success)
        screen.set_cursor(False)


def message_wait_story(screen: Screen):
    screen.set_cursor(True)
    message = "Generating".center(screen.cols)
    screen.message(message, center=True, autosplit=False)
    # Set after last letter
    last_letter_index = len(message.rstrip())
    screen.set_cursor_position(screen.rows // 2 - 1, last_letter_index)


if __name__ == "__main__":
    from components.pins import (
        PIN_SCREEN_SDA,
        PIN_SCREEN_SCL,
        PIN_POT,
        PIN_BUTTON,
        PIN_NEOPIXEL,
    )

    wifi_client = WifiClient()
    client = Client("http://192.168.1.234:5000")
    screen = Screen(PIN_SCREEN_SDA, PIN_SCREEN_SCL)
    pot = Potentiometer(PIN_POT)
    button = PushButton(PIN_BUTTON)
    neopix = NeopixelCircle(PIN_NEOPIXEL, brightness=0.1)
    interactive_story(client, screen, pot, neopix, button)
