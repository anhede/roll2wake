import os
import random
from storyteller import Storyteller
import time


def main():
    api_key = os.getenv("API_KEY")
    if not api_key:
        print("API_KEY is not set.")
        return
    storyteller = Storyteller(api_key=api_key)
    beat = storyteller.generate_new_story()
    while True:
        print("\n" + beat.beat_text)
        
        # Check if this is an ending
        if beat.is_ending and beat.ending is not None:
            ending_type = beat.ending.ending_type.name
            print(f"\n=== STORY ENDING: {ending_type} ===")
            print(f"Reason: {beat.ending.reason}")
            print("The story has concluded!")
            break
        
        print("\nChoices:")
        for choice in beat.choices:
            print(
                f"  {choice.choice_id}. {choice.label} (DC {choice.difficulty}, {choice.mode.name})"
            )
        try:
            user_input = input(
                "\nChoose an option by number (or 'q' to quit): "
            ).strip()
            if user_input.lower() == "q":
                print("Thanks for playing!")
                break
            choice_id = int(user_input)
            selected = next(c for c in beat.choices if c.choice_id == choice_id)
        except Exception:
            print("Invalid choice. Try again.")
            continue
        roll = roll_dice()
        print(f"You rolled a {roll} (DC {selected.difficulty})...")
        if roll >= selected.difficulty:
            result = "Solid Success."
        else:
            result = "Failure."
        beat = storyteller.continue_story(choice_id=choice_id, success_result=result)
        
        # Check if the story ended (no choices and not an explicit ending)
        if not beat.choices and not beat.is_ending:
            print("\n" + beat.beat_text)
            print("No more choices. The story ends here!")
            break


def roll_dice() -> int:
    dice = random.randint(1, 8)
    velocity = random.random() * 24 + 6
    friction = random.random() * 4 + 8
    while velocity < 200:
        dice = (dice + 1) % 8
        print(dice + 1, end="\r")
        velocity += friction
        time.sleep(velocity / 1000)
    print()
    return dice + 1


if __name__ == "__main__":
    main()
