import time
from components.neopixelcircle import NeopixelCircle
from components.screen import Screen
from components.potentiometer import Potentiometer
from components.pushbutton import PushButton
from components.utils import smart_wrap

# White for the selected choice
COLOR_SELECTION = (255, 255, 255)
# Blue for unselected choices
COLOR_UNSELECTED = (0, 0, 255)
# No color for off state
COLOR_OFF = (0, 0, 0)
# Time in milliseconds to wait before autoscrolling a line
AUTOSCROLL_DELAY = 2000


def choice_menu(
    prompts: list[str],
    neopix: NeopixelCircle,
    screen: Screen,
    pot: Potentiometer,
    pushb: PushButton,
) -> int:
    """
    Displays a radial choice menu on the NeoPixel circle and screen.
    Returns the index of the selected choice.
    Limit of 8 choices.
    """
    n_prompts = len(prompts)
    if n_prompts > 8:
        raise ValueError("Maximum of 8 choices allowed.")

    # Get the closest potentiometer step value to 8 divisible by len(prompts)
    # This breaks up small n_steps into multiple cycles
    # E.g. 4 -> 8, 3 -> 9
    pot_steps = round(8 / n_prompts) * n_prompts

    last_choice = 0
    last_choice_time = time.ticks_ms()
    last_prompt = None
    choice = 0
    while not pushb.is_pressed():
        # Get current choice
        choice = __get_choice(pot, pot_steps, n_prompts)
        prompt = smart_wrap(prompts[choice], screen.cols, 50)
        prompt = __update_autoscroll(screen, prompt, last_choice_time)
        if not last_prompt:
            last_prompt = prompt

        # If new choice this iteration
        if choice != last_choice:
            last_choice = choice
            last_choice_time = time.ticks_ms()
            last_prompt = prompt
            __update_neopixel(neopix, prompts, choice)
            __update_screen(screen, prompt)

        if prompt != last_prompt:
            last_prompt = prompt
            __update_screen(screen, prompt)

        time.sleep_ms(50)

    return choice  # Return the index of the selected choice


def __get_choice(pot: Potentiometer, pot_steps: int, n_prompts: int) -> int:
    """
    Get the current choice based on the potentiometer position.
    Returns an index from 0 to n_prompts - 1.
    """
    return pot.read_discrete(pot_steps) % n_prompts  # Ensure it wraps around correctly


def __update_screen(screen: Screen, prompt: str):
    """
    Update the screen with the current choice.
    """
    screen.message(prompt)


def __update_neopixel(neopix: NeopixelCircle, prompts: list[str], choice: int):
    """
    Update the NeoPixel circle with the current choice.
    """
    valid_choices = __centered_list(len(prompts))
    colors = [COLOR_OFF] * 8  # Start with all LEDs off

    # Color valid choices
    for i in valid_choices:
        colors[i] = COLOR_UNSELECTED  # type: ignore

    # Highlight the selected choice
    colors[valid_choices[choice]] = COLOR_SELECTION  # type: ignore

    # Set the colors on the NeoPixel circle
    neopix.set_colors(colors)


def __update_autoscroll(
    screen: Screen,
    prompt: str,
    choice_time: int,
) -> str:
    """
    Update the screen to scroll through the choice text if the choice hasn't changed for a while.
    """
    lines_to_scroll = max(0, len(prompt.split("\n")) - screen.rows)
    if lines_to_scroll <= 0:
        return prompt
    current_line = (
        time.ticks_ms() - choice_time
    ) // AUTOSCROLL_DELAY  # Scroll every second
    current_line = current_line % (lines_to_scroll + 1)  # Wrap around
    lines = prompt.split("\n")
    selected_lines = lines[current_line : current_line + screen.rows]
    return "\n".join(selected_lines)


def __centered_list(n, center=2):
    half = n // 2
    if n % 2 == 0:
        return list(range(center - half, center + half))
    else:
        return list(range(center - half, center + half + 1))


if __name__ == "__main__":
    import time
    from components.pins import (
        PIN_NEOPIXEL,
        PIN_SCREEN_SDA,
        PIN_SCREEN_SCL,
        PIN_POT,
        PIN_BUTTON,
    )

    # Example usage with mock components
    neopix = NeopixelCircle(pin=PIN_NEOPIXEL, brightness=1)
    screen = Screen(PIN_SCREEN_SDA, PIN_SCREEN_SCL)
    pot = Potentiometer(PIN_POT)
    pushb = PushButton(PIN_BUTTON)

    prompts = [
        "Attack",
        "Run away",
        "Drink love potion",
        "Alt F4",
        "A very long choice that should wrap around to the next line. Probably more than 50 characters long and needs scrolling.",
    ]

    selected_index = choice_menu(prompts, neopix, screen, pot, pushb)
    screen.message(f"Selected: \n{prompts[selected_index]}")
    neopix.clear()
