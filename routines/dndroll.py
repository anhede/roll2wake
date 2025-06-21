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
COLOR_SOLID_SUCCESS = (0, 255, 0)  # Green for success
COLOR_CLOSE_CALL = (255, 255, 0)  # Yellow for close call
COLOR_GREAT_SUCCESS = COLOR_BLANK  # Optionally show the 8th in a special color

# -2 Disaster, -1 Failure, 0 Close Call, 1 Solid, 2 Triumph
SuccessLevel = int
DISASTER = 0
FAILURE = 1
CLOSE_CALL = 2
SOLID_SUCCESS = 3
TRIUMPH = 4
SUCCESS_LEVELS = ["Disaster", "Failure", "Close Call", "Solid Success", "Triumph"]

def dnd_roll(
    difficulty: int,  # 2-8
    advantage: int,  # 0 for normal, 1 for advantage, -1 for disadvantage
    screen: Screen,
    pushb: PushButton,
    neopix: NeopixelCircle,
) -> SuccessLevel:
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

    # Determine success level based on the final roll
    if final_roll == 1:
        success_level = DISASTER
    elif final_roll == 8:
        success_level = TRIUMPH
    elif final_roll == difficulty:
        success_level = CLOSE_CALL
    elif final_roll > difficulty:
        success_level = SOLID_SUCCESS
    elif final_roll < difficulty:
        success_level = FAILURE
    else:
        raise ValueError("Unexpected roll value")

    # Display the result on the screen
    __show_final_roll(screen, neopix, success_level, final_roll, difficulty)

    return success_level


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
    success_level: int,
    final_roll: int,
    difficulty: int,
):
    """
    Show the final roll result on the screen and NeoPixel circle.
    """
    # Update the screen with the result
    screen_message = f"{SUCCESS_LEVELS[success_level]}!\nRolled {final_roll} on {difficulty}"
    screen.message(screen_message, center=True)

    # Flash the result
    total_time_ms = 3000
    if success_level == TRIUMPH or success_level == DISASTER:
        # Rainbow cycle for great success
        if success_level == TRIUMPH:
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
        else: # Disaster, Red to black
            colors = [
                (255, 0, 0),  # Red
                (128, 0, 0),  # Dark Red
                (64, 0, 0),  # Very Dark Red
                (32, 0, 0),  # Almost Black
                (16, 0, 0),  # Near Black
                (8, 0, 0),   # Very Near Black
                (4, 0, 0),   # Almost Black
                (2, 0, 0)    # Black
            ]
        spin_time_ms = 50
        n_flashes = total_time_ms // spin_time_ms
        for i in range(n_flashes):
            # Cycle through the colors
            colors = colors[-1:] + colors[:-1]
            neopix.set_colors(colors)
            time.sleep_ms(spin_time_ms)
    else:
        # Neopixel colors based on the result
        if success_level == SOLID_SUCCESS:
            colors = [COLOR_SOLID_SUCCESS] * 8
        elif success_level == CLOSE_CALL:
            colors = [COLOR_CLOSE_CALL] * 8
        else:
            colors = [COLOR_FAIL] * 8

        colors[final_roll - 1] = COLOR_DICE  # Highlight the rolled die # type: ignore
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
