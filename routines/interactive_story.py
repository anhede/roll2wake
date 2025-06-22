from components.screen import Screen
from components.pushbutton import PushButton
from components.potentiometer import Potentiometer
from components.neopixelcircle import NeopixelCircle

from client.client import Client
from routines.scroll_read import scroll_read
from routines.choicemenu import choice_menu
from routines.dndroll import dnd_roll, SUCCESS_LEVELS
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

    # beat = client.get_new_story()
    beat = StoryBeat(
        beat_text="Welcome to the interactive story! Choose your path.",
        choices=[
            Choice(1, "Slay the dragon", 7),
            Choice(2, "Pray to the Gods", 5, MODE_DISADVANTAGE),
            Choice(3, "Flee", 3, MODE_ADVANTAGE),
        ],
    )
    while not beat.is_ending:
        scroll_read(
            screen,
            pot,
            button,
            beat.beat_text,
        )

        prompts = []
        for choice in beat.choices:
            prompts.append(
                f"{choice.choice_id}: {choice.label} ({choice.difficulty} {MODES_SYMBOLS[choice.mode]})"
            )
        choice_id = choice_menu(
            prompts,
            neopix,
            screen,
            pot,
            button,
        )
        choice = beat.choices[choice_id - 1]
        success = dnd_roll(choice.difficulty, choice.mode, screen, button, neopix)
        beat = client.update_story(choice_id, success)

    print(beat.full_format)  # Ending
