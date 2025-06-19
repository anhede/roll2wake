import time
import random
from components.screen import Screen
from components.pushbutton import PushButton
from components.neopixelcircle import NeopixelCircle

INITIAL_VELOCITY = 50  # Initial velocity for the roll in milliseconds
STOP_VELOCITY = 200  # Velocity at which the roll stops in milliseconds
BASE_FRICTION = 10

COLOR_BLANK = (0, 0, 0)  # Black for blank state
COLOR_FAIL = (0, 0, 255)  # Blue for failure
COLOR_DICE = (255, 255, 255)  # White for dice
COLOR_SUCCESS = (0, 255, 0)  # Green for success
COLOR_GREAT_SUCCESS = COLOR_BLANK  # Optionally show the 8th in a special color


def dnd_roll(
    difficulty: int,  # 1-8
    advantage: int,  # 0 for normal, 1 for advantage, -1 for disadvantage
    screen: Screen,
    pushb: PushButton,
    neopix: NeopixelCircle,
):
    """
    Perform a D&D style roll with advantage or disadvantage.
    """
    # Prompt the user to roll, showing the current difficulty and advantage state
    random.seed(time.ticks_ms())  # Seed the random number generator
    __prompt_roll(screen, difficulty, advantage)

    n_rolls = 2 if advantage != 0 else 1
    die_indices = []
    for _ in range(n_rolls):
        die_indices.append(0)
        __color_die_roll(neopix, difficulty, die_indices)
        # Wait for the button press to start the roll
        while not pushb.is_held():
            time.sleep_ms(50)  # Polling delay

        # Wait for the button to be released
        velocity = int(
            INITIAL_VELOCITY * random.uniform(0.8, 1.4)
        )  # Randomize initial velocity
        while pushb.is_held():
            __color_die_roll(neopix, difficulty, die_indices)
            die_indices[-1] = (die_indices[-1] + 1) % 8
            time.sleep_ms(velocity)

        # Perform the roll
        friction = int(BASE_FRICTION * random.uniform(0.6, 1.2))
        while velocity < STOP_VELOCITY:
            die_indices[-1] = (die_indices[-1] + 1) % 8
            __color_die_roll(neopix, difficulty, die_indices)
            time.sleep_ms(velocity)
            velocity += friction

    # Calculate the final roll value
    if advantage == 1:  # Advantage
        final_roll = max(die_indices) + 1  # Convert index to die value (1-8)
    elif advantage == -1:  # Disadvantage
        final_roll = min(die_indices) + 1  # Convert index to die value (1-8)
    else:  # Normal roll
        final_roll = die_indices[0] + 1  # Convert index to die value

    # Check if the roll is a success or great success
    success = final_roll >= difficulty
    great_success = final_roll == 8

    # Display the result on the screen
    __show_final_roll(screen, neopix, success, great_success, final_roll, difficulty)


def __prompt_roll(screen: Screen, difficulty: int, advantage: int):
    """
    Display the roll prompt on the screen.
    """
    screen.clear()
    if advantage == 0:
        screen.message(f"Roll at least {difficulty}", center=True)
    elif advantage == 1:
        screen.message(f"Roll at least {difficulty}\nAdvantage", center=True)
    else:
        screen.message(f"Roll at least {difficulty}\nDisadvantage", center=True)


def __color_die_roll(
    neopix: NeopixelCircle, difficulty: int, die_indices: list[int] | None = None
):
    """
    Color the NeoPixel circle based on the current roll state.
    Shows difficulty as reds, die indices as whites.
    """
    colors = []
    for i in range(8):
        # Base color for the die
        if i in range(difficulty - 1):
            colors.append(COLOR_FAIL)
        elif i == 7:
            colors.append(COLOR_GREAT_SUCCESS)  # Yellow for critical success
        else:
            colors.append(COLOR_BLANK)

        # Overdraw the die being rolled in white
        if die_indices is not None and i in die_indices:
            n_die = die_indices.count(i)
            base_color = colors[i]
            # mix base and die color, 3/4 for double die, 1/4 for single die
            m_factor = 3 / 4 if n_die > 1 else 1 / 4
            m_factor_i = 1 - m_factor
            colors[i] = tuple(
                int(base_color[j] * m_factor_i + COLOR_DICE[j] * m_factor)
                for j in range(3)
            )

    neopix.set_colors(colors)


def __show_final_roll(
    screen: Screen,
    neopix: NeopixelCircle,
    success: bool,
    great_success: bool,
    final_roll: int,
    difficulty: int,
):
    """
    Show the final roll result on the screen and NeoPixel circle.
    """
    # Update the screen with the result
    if success:
        if great_success:
            screen_message = f"Great Success!\nRolled {final_roll} on {difficulty}"
        else:
            screen_message = f"Success!\nRolled {final_roll} on {difficulty}"
    else:
        screen_message = f"Failure!\nRolled {final_roll} on {difficulty}"
    screen.message(screen_message, center=True)

    # Neopixel colors based on the result
    if great_success:
        colors = [COLOR_GREAT_SUCCESS] * 8
    elif success:
        colors = [COLOR_SUCCESS] * 8
    else:
        colors = [COLOR_FAIL] * 8

    colors[final_roll - 1] = COLOR_DICE  # Highlight the rolled die # type: ignore

    # Flash the result
    total_time_ms = 3000
    if great_success:
        # Rainbow cycle for great success
        colors = [
            (255, 0, 0),  # Red
            (255, 127, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0),  # Green
            (0, 255, 255),  # Cyan
            (0, 0, 255),  # Blue
            (75, 0, 130),  # Indigo
            (143, 0, 255),  # Violet
        ]
        spin_time_ms = 50
        n_flashes = total_time_ms // spin_time_ms
        for i in range(n_flashes):
            # Cycle through the colors
            colors = colors[-1:] + colors[:-1]
            neopix.set_colors(colors)
            time.sleep_ms(spin_time_ms)
    else:
        # Flash the result on the screen and NeoPixel circle
        flash_time_ms = 500
        n_flashes = total_time_ms // flash_time_ms
        for i in range(n_flashes):
            last_flash = i == n_flashes - 1
            if not last_flash and i % 2 == 0:
                # Blank
                neopix.fill(COLOR_BLANK)
            else:
                # Flash
                neopix.set_colors(colors)
            time.sleep_ms(flash_time_ms)


if __name__ == "__main__":
    # Example usage of the dnd_roll function
    screen = Screen(pin_sda=20, pin_scl=21)  # Adjust pins as needed
    pushb = PushButton(pin=15)  # Adjust pin as needed
    neopix = NeopixelCircle(
        pin=16, brightness=0.1
    )  # Adjust pin and brightness as needed

    while True:
        # Simulate a roll with random difficulty and advantage
        difficulty = random.randint(2, 8)
        advantage = random.choice([-1, 0, 0, 0, 1])  # type: ignore
        dnd_roll(difficulty, advantage, screen, pushb, neopix)  # type: ignore
