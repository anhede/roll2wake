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
    while True:
        formatted_text = beat.beat_text.replace("\n", " ").strip()
        formatted_text = smart_wrap(
            formatted_text,
            row_len=screen.cols,
            max_rows=50,
        )
        scroll_read(
            screen,
            pot,
            button,
            formatted_text
        )
        if beat.is_ending:
            scroll_read(
                screen,
                pot,
                button,
                "The story has ended. Thank you for playing!"
            )
            return
        prompts = []
        for choice in beat.choices:
            prompts.append(
                f"{choice.choice_id}: {choice.label} ({choice.difficulty}{MODES_SYMBOLS[choice.mode]})"
            )
        choice_id = choice_menu(
            prompts,
            neopix,
            screen,
            pot,
            button,
        ) + 1  # +1 to match choice_id starting from 1
        choice = beat.choices[choice_id - 1]
        success = dnd_roll(choice.difficulty, choice.mode, screen, button, neopix)
        message_wait_story(screen)
        neopix.clear()
        beat = client.update_story(choice_id, success)

def message_wait_story(screen: Screen):
    screen.set_cursor(True)
    message = "Generating"
    message = message.center(screen.cols)
    screen.message(message, center=False, autosplit=False)
    # Set after last letter
    last_letter_index = len(message.rstrip())
    screen.set_cursor_position(0, last_letter_index)

if __name__ == "__main__":
    # Example usage
    wifi_client = WifiClient()
    client = Client("http://192.168.1.234:5000")
    screen = Screen(20, 21)
    pot = Potentiometer(28)
    button = PushButton(15)
    neopix = NeopixelCircle(16, brightness=0.1)
    interactive_story(client, screen, pot, neopix, button)
