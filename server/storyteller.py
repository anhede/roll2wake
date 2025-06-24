import os
import json
from openai import OpenAI
from typing import List, Optional, Tuple
from models import StoryBeat, Choice
from themes import get_random_themes
from models import MODE_DISADVANTAGE, MODE_NORMAL, MODE_ADVANTAGE

# Maximum number of attempts to get a valid response from OpenAI
# This is to handle potential API errors or invalid responses
# Happens sometimes due to bad model responses, 
# a single failed attempt may happen in about 1 in 20 requests using gpt-4o-mini
# Having six failed attempts in a row is thus extremely unlikely (1 in 64,200,000)
MAX_ATTEMPTS = 6

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
        self.client = OpenAI(api_key=api_key)
        self.model = model
        print(f"Initializing Storyteller with model {self.model}")

    def _request_story_beat(self, user_content: str) -> StoryBeat | None:
        """
        Send messages to OpenAI, parse JSON response, convert to StoryBeat, and record history.
        """
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": STORYTELLER_SYSTEM_PROMPT},
                        {"role": "user", "content": user_content}
                    ],
                    response_format={"type": "json_object"},
                )
                content = response.choices[0].message.content
                if content is None:
                    raise ValueError("No content received from OpenAI API")

                data = json.loads(content)

                # Parse choices
                choices: List[Choice] = []
                for choice_str in data.get("choices", []):
                    parts = choice_str.split(",", 3)
                    if len(parts) < 4:
                        continue
                    cid, label, diff, mode = parts
                    mode_map = {"1": MODE_ADVANTAGE, "-1": MODE_DISADVANTAGE, "0": MODE_NORMAL}
                    choices.append(
                        Choice(
                            choice_id=int(cid),
                            label=label,
                            difficulty=int(diff),
                            mode=mode_map.get(mode, MODE_NORMAL),
                        )
                    )

                # Build beat
                story_beat = StoryBeat(
                    beat_text=data.get("beat", ""),
                    choices=choices,
                    is_ending=data.get("endstory", False)
                )

                # Record
                self.story.add_story_beat(story_beat)
                return story_beat

            except Exception as e:
                print(f"Attempt {attempt} failed: {e}")
                if attempt == MAX_ATTEMPTS:
                    raise

    def generate_new_story(self) -> StoryBeat:
        """Generate a new story beat with up to 8 choices."""
        themes = " ".join(get_random_themes())
        self.story = Story()
        print(f"Generating new story with themes: {themes}")
        prompt = f"Themes: {themes}\n\nGenerate a single beat and up to 8 choices following the format above."
        beat = self._request_story_beat(prompt)
        if not beat:
            raise ValueError("Failed to generate a new story beat")
        return beat

    def continue_story(self, choice_id: int, success_result: str) -> StoryBeat:
        """Continue the story based on a player's choice and its outcome."""
        print(f"Current Story Beats: {len(self.story.story_beats)}")
        current = self.story.story_beats[-1] if self.story.story_beats else None
        if not current:
            raise ValueError("No story beat available to continue from")
        chosen = next((c for c in current.choices if c.choice_id == choice_id), None)
        if not chosen:
            raise ValueError(f"Choice with ID {choice_id} not found")

        self.story.add_choice(chosen, success_result)
        history = self.story.get_story_history()
        prompt = f"Story history:\n{history}\nPlayer chose: {chosen.label}\nResult: {success_result}\n\nGenerate the next story beat and choices based on this outcome."
        beat = self._request_story_beat(prompt)
        if not beat:
            raise ValueError("Failed to continue the story")
        return beat

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
