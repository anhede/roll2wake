import requests
import random
import time
from client import Client
from models import MODE_ADVANTAGE, MODE_DISADVANTAGE, MODE_NORMAL


def roll_dice() -> int:
    """Simulate dice rolling with animation"""
    dice = random.randint(1, 8)
    velocity = random.random() * 24 + 6
    friction = random.random() * 4 + 8
    print("Rolling dice...")
    while velocity < 200:
        dice = (dice + 1) % 8
        print(dice + 1, end="\r")
        velocity += friction
        time.sleep(velocity / 1000)
    print()
    return dice + 1


def main():
    print("=== Interactive Story API Client ===")
    client = Client()

    # Start new story
    print("\nStarting new story...")
    beat = client.get_new_story()
    while True:
        print("\n" + beat.full_format())

        # Check if this is an ending
        if beat.is_ending:
            print("\n=== STORY ENDING ===")
            break

        # Get user input
        try:
            user_input = input(
                "\nChoose an option by number (or 'q' to quit): "
            ).strip()
            if user_input.lower() == "q":
                print("Thanks for playing!")
                break

            choice_id = int(user_input)
            selected = next(c for c in beat.choices if c.choice_id == choice_id)
        except (ValueError, StopIteration):
            print("Invalid choice. Try again.")
            continue

        # Roll dice and determine result
        roll = roll_dice()
        if selected.mode == MODE_ADVANTAGE:
            roll = max(roll, roll_dice())
        elif selected.mode == MODE_DISADVANTAGE:
            roll = min(roll, roll_dice())
        print(f"You rolled a {roll} ({selected.difficulty})...")

        if roll == 8:
            result = "Critical Success."
        elif roll == 1:
            result = "Critical Failure."
        elif roll >= selected.difficulty:
            result = "Solid Success."
        else:
            result = "Failure."

        # Update story
        beat = client.update_story(choice_id=choice_id, success_result=result)


if __name__ == "__main__":
    main()
