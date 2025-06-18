from components.neopixelcircle import NeopixelCircle
from components.screen import Screen
from components.potentiometer import Potentiometer
from components.pushbutton import PushButton

# Blue for the selected choice
COLOR_SELECTION = (0, 0, 255)
# Gray for unselected choices
COLOR_UNSELECTED = (64, 0, 0)
# No color for off state
COLOR_OFF = (0, 0, 0) 

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

    last_choice = None
    while not pushb.is_pressed():

        # Get current choice
        choice = get_choice(pot, pot_steps, n_prompts)

        # If new choice this iteration
        if choice != last_choice:
            last_choice = choice
            update_screen(screen, prompts, choice)
            update_neopixel(neopix, prompts, choice)

        time.sleep_ms(50)

    return choice  # Return the index of the selected choice

def get_choice(pot: Potentiometer, pot_steps: int, n_prompts: int) -> int:
    """
    Get the current choice based on the potentiometer position.
    Returns an index from 0 to n_prompts - 1.
    """
    return pot.read_discrete(pot_steps) % n_prompts  # Ensure it wraps around correctly

def update_screen(screen: Screen, prompts: list[str], choice: int):
    """
    Update the screen with the current choice.
    """
    screen.message(f"{choice+1}/{len(prompts)}: {prompts[choice]}")

def update_neopixel(neopix: NeopixelCircle, prompts: list[str], choice: int):
    """
    Update the NeoPixel circle with the current choice.
    """
    valid_choices = __centered_list(len(prompts))
    colors = [COLOR_OFF] * 8  # Start with all LEDs off

    # Color valid choices
    for i in valid_choices:
        colors[i] = COLOR_UNSELECTED # type: ignore

    # Highlight the selected choice
    colors[valid_choices[choice]] = COLOR_SELECTION  # type: ignore

    # Set the colors on the NeoPixel circle
    neopix.set_colors(colors)

def __centered_list(n, center=2):
    half = n // 2
    if n % 2 == 0:
        return list(range(center - half, center + half))
    else:
        return list(range(center - half, center + half + 1))

if __name__ == "__main__":
    import time

    # Example usage with mock components
    neopix = NeopixelCircle(pin=16, brightness=1)
    screen = Screen(20, 21)
    pot = Potentiometer(28)
    pushb = PushButton(15)

    prompts = ["Attack", "Run away", "Drink love\npotion", "Alt F4"]
    
    selected_index = choice_menu(prompts, neopix, screen, pot, pushb)
    screen.message(f"Selected: \n{prompts[selected_index]}")
    neopix.clear()