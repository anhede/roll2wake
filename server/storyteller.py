import os
import json
from openai import OpenAI
from typing import List, Optional, Tuple
from models import StoryBeat, Choice
from themes import get_random_themes
from models import MODE_DISADVANTAGE, MODE_NORMAL, MODE_ADVANTAGE

# System prompt for the Choose-Your-Own-Adventure game engine
STORYTELLER_SYSTEM_PROMPT = (
    "You are a Choose-Your-Own-Adventure game engine. "
    "Your style is very short and concise. You focus only on what's important."
    "You are not afraid of mature themes and content. Blood, gore, and violence is encouraged."
    "When the player is faced by enemies, they can always choose to fight lethally."
    "In successful lethal combat, describe the death of the enemy in detail."
    "When describing action, use vivid and gore-filled language. Describe blood flowing, shots piercing flesh, and the visceral reactions of characters."
    "If the player fails an important task, or achieves a major victory, end the story with a satisfying conclusion."
    "Such a conclusion should not be abrupt, but rather a natural end to the story arc."
    "If the player has items, include them in the story beat text."
    "If the player is hurt, include their injuries in the story beat text.\n\n"
    "Always provide choices for any beat of the story, unless the story is ending.\n\n"
    "Generate interactive story content in JSON format with the following structure:\n\n"
    '{"beat": "story text here", "choices": ["1,choice text,difficulty,roll_mode", "2,choice text,difficulty,roll_mode", ...], "endstory": false}\n\n'
    "FORMAT REQUIREMENTS:\n"
    "• beat: A single story paragraph, ends with the state of the player and any items they may possess if any\n"
    "• choices: Array of strings, each formatted as: 'index,choice_text,difficulty,roll_mode'\n"
    "  - index: number 1-5\n"
    "  - choice_text: descriptive action text\n"
    "  - difficulty: integer 2-8 (2=easy, 8=very hard)\n"
    "  - roll_mode: -1 (disadvantage), 0 (normal), 1 (advantage)\n"
    "• endstory: boolean - set to true when the player has failed or won at an important task and the story should end\n\n"
    "EXAMPLE:\n"
    '{"beat": "You stand at a crossroads in the dark forest.\\nThe path splits in three directions.", "choices": ["1,Take the left path,3,0", "2,Go right towards the light,5,1", "3,Stay and rest,2,-1"], "endstory": false}\n\n'
    "ENDING RULES:\n"
    "• Set endstory to true when the player has achieved a major victory or suffered a critical failure\n"
    "• When endstory is true, provide a satisfying conclusion in the beat text\n"
    "• When endstory is true, choices array should be empty or omitted\n"
    "• Major victories: completing the main quest, defeating the final boss, achieving the primary goal\n"
    "• Critical failures: dying, losing the main objective, being captured permanently\n\n"
    "RULES:\n"
    "• Output ONLY valid JSON\n"
    "• Include 2-5 choices per beat (unless ending the story)\n"
    "• Make choices reflect the themes and story context\n"
    "• Make sure that the difficulty reflects the choice. \n"
    "• Ensure all difficulty values are integers 2-8\n"
    "• Ensure all roll_mode values are -1, 0, or 1"
)


class Story:
    def __init__(self):
        self.story_beats: List[StoryBeat] = []
        self.choices: List[Tuple[Choice, str]] = []

    def add_story_beat(self, story_beat: StoryBeat):
        self.story_beats.append(story_beat)

    def add_choice(self, choice: Choice, roll_result: str):
        self.choices.append((choice, roll_result))

    def get_story_history(self) -> str:
        """Get the history of the story so far. Includes the story beats and the choices made."""
        history = ""
        beats = self.story_beats.copy()
        choices = self.choices.copy()
        while beats or choices:
            if beats:
                history += f"Story beat: {beats.pop(0).beat_text}\n"
            if choices:
                choice_tuple = choices.pop(0)
                history += f"Choice: Tried {choice_tuple[0].label}. Result: {choice_tuple[1]}\n"
            history += "\n"
        return history


class Storyteller:
    """
    A class to generate and progress interactive DnD-style stories using OpenAI's Chat API.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        print("Initializing Storyteller with model:", model)
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.themes = get_random_themes()
        self.story = Story()

    def generate_new_story(self) -> StoryBeat:
        """Generate a new story beat with up to 8 choices."""
        themes_list = ", ".join(self.themes)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": STORYTELLER_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": f"Themes: {themes_list}  \n\nGenerate a single beat and up to 8 choices following the format above.",
                },
            ],
            response_format={"type": "json_object"},
        )

        # Parse the response and create a StoryBeat
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("No content received from OpenAI API")

        data = json.loads(content)

        # Create choices from the response
        choices = []
        for choice_str in data.get("choices", []):
            # Parse the choice string: "index,choice-text,difficulty,roll-mode"
            parts = choice_str.split(",", 3)  # Split into max 4 parts
            if len(parts) >= 4:
                choice_id = int(parts[0])
                label = parts[1]
                difficulty = int(parts[2])
                roll_mode = int(parts[3])

                # Convert roll_mode to AdvantageMode enum
                mode_map = {
                    1: MODE_ADVANTAGE,
                    -1: MODE_DISADVANTAGE,
                    0: MODE_NORMAL,
                }
                mode = mode_map.get(roll_mode, MODE_NORMAL)

                choice = Choice(
                    choice_id=choice_id,
                    label=label,
                    difficulty=difficulty,
                    mode=mode,
                )
                choices.append(choice)

        # Create and return the StoryBeat
        story_beat = StoryBeat(
            beat_text=data.get("beat", ""),
            choices=choices
        )

        # Add to story history
        self.story.add_story_beat(story_beat)

        return story_beat

    def continue_story(self, choice_id: int, success_result: str) -> StoryBeat:
        """Continue the story based on a player's choice and its outcome."""
        # Find the choice that was made
        current_beat = self.story.story_beats[-1]
        if not current_beat:
            raise ValueError("No story beat available to continue from")

        chosen_choice = None
        for choice in current_beat.choices:
            if choice.choice_id == choice_id:
                chosen_choice = choice
                break

        if not chosen_choice:
            raise ValueError(f"Choice with ID {choice_id} not found")

        # Add the choice and result to story history
        self.story.add_choice(chosen_choice, success_result)

        # Get story history for context
        story_history = self.story.get_story_history()

        # Generate new story beat with retry logic
        story_beat = None
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                    {
                        "role": "system",
                        "content": STORYTELLER_SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": f"Story history:\n{story_history}\n\nPlayer chose: {chosen_choice.label}\nResult: {success_result}\n\nGenerate the next story beat and choices based on this outcome.",
                    },
                    ],
                    response_format={"type": "json_object"},
                )

                # Parse the response and create a StoryBeat
                content = response.choices[0].message.content
                if content is None:
                    raise ValueError("No content received from OpenAI API")

                data = json.loads(content)

                # Create choices from the response
                choices = []
                for choice_str in data.get("choices", []):
                    # Parse the choice string: "index,choice-text,difficulty,roll-mode"
                    parts = choice_str.split(",", 3)  # Split into max 4 parts
                    choice_id = int(parts[0])
                    label = parts[1]
                    difficulty = int(parts[2])
                    roll_mode = int(parts[3])

                    # Convert roll_mode to AdvantageMode enum
                    mode_map = {
                        1: MODE_ADVANTAGE,
                        -1: MODE_DISADVANTAGE,
                        0: MODE_NORMAL,
                    }
                    mode = mode_map.get(roll_mode, MODE_NORMAL)

                    choice = Choice(
                        choice_id=choice_id,
                        label=label,
                        difficulty=difficulty,
                        mode=mode,
                    )
                    choices.append(choice)

                # Create and return the StoryBeat
                story_beat = StoryBeat(
                    beat_text=data.get("beat", ""),
                    choices=choices,
                    is_ending=data.get("endstory", False)
                )
                break  # Success, exit the retry loop
            except Exception as e:
                print(f"Attempt {attempt} failed: {e}")
                if attempt == max_attempts:
                    raise
        
        # Add to story history
        if not story_beat:
            raise ValueError("Failed to generate a new story beat after multiple attempts")
        self.story.add_story_beat(story_beat)

        return story_beat


if __name__ == "__main__":
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY is not set")
    storyteller = Storyteller(api_key=api_key)

    # Generate initial story
    initial_beat = storyteller.generate_new_story()
    print("=== INITIAL STORY ===")
    print(initial_beat.beat_text)
    print("\nChoices:")
    for choice in initial_beat.choices:
        print(f"  {choice}")

    # Continue story with a choice
    print("\n=== CONTINUING STORY ===")
    next_beat = storyteller.continue_story(choice_id=1, success_result="Solid Success.")
    print(next_beat.beat_text)
    print("\nNew Choices:")
    for choice in next_beat.choices:
        print(f"  {choice}")

    print("\n=== STORY HISTORY ===")
    print(storyteller.story.get_story_history())
