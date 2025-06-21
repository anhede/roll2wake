import os
import json
import random
from openai import OpenAI
from typing import List, Dict, Optional, Tuple
from models import StoryBeat, Choice, StoryEnding, EndingType
from themes import get_random_themes
from models import AdvantageMode

# System prompt for the Choose-Your-Own-Adventure game engine
STORYTELLER_SYSTEM_PROMPT = (
    "You are a Choose-Your-Own-Adventure game engine. "
    "Your style is very short and concise. You focus only on what's important."
    "You are not afraid of mature themes and content. Blood, gore, and violence are not off limits."
    "Generate interactive story content in JSON format with the following structure:\n\n"
    '{"beat": "story text here", "choices": ["1,choice text,difficulty,roll_mode", "2,choice text,difficulty,roll_mode", ...], "endstory": false}\n\n'
    "FORMAT REQUIREMENTS:\n"
    "• beat: A single story paragraph with line breaks as literal '\\n' sequences\n"
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
        self.themes = get_random_themes()
        self.story = Story()
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3

    def _should_end_story(
        self, success_result: str, turns_remaining: Optional[int]
    ) -> Tuple[bool, Optional[EndingType], str]:
        """
        Determine if the story should end and what type of ending.
        Returns (should_end, ending_type, reason)
        """
        # Check if turns are exhausted
        if turns_remaining is not None and turns_remaining <= 0:
            return True, EndingType.NEUTRAL, "Story length limit reached"

        # Check for victory conditions (multiple successes in a row)
        if "Success" in success_result or "success" in success_result.lower():
            self.consecutive_failures = 0
            # Check if we have enough story beats for a satisfying victory
            if len(self.story.story_beats) >= 5:
                return (
                    True,
                    EndingType.VICTORY,
                    "Player achieved their goal through successful choices",
                )
        else:
            # Track consecutive failures
            self.consecutive_failures += 1
            if self.consecutive_failures >= self.max_consecutive_failures:
                return (
                    True,
                    EndingType.DEFEAT,
                    f"Player failed {self.consecutive_failures} consecutive important checks",
                )

        return False, None, ""

    def _generate_story_ending(
        self, ending_type: EndingType, reason: str, story_history: str
    ) -> StoryBeat:
        """Generate a story ending based on the ending type and context."""

        ending_prompt = f"""Generate a story ending in JSON format with the following structure:
{{"beat": "final story text", "endstory": true}}

ENDING TYPE: {ending_type.name}
REASON: {reason}

STORY HISTORY:
{story_history}

Generate a satisfying conclusion that wraps up the story based on the ending type and reason. Set endstory to true and provide the final narrative in the beat field."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a Choose-Your-Own-Adventure game engine. Generate story endings in JSON format.",
                },
                {
                    "role": "user",
                    "content": ending_prompt,
                },
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        if content is None:
            raise ValueError("No content received from OpenAI API")

        data = json.loads(content)

        # Create the ending
        ending = StoryEnding(
            ending_type=ending_type, ending_text=data.get("beat", ""), reason=reason
        )

        # Create story beat with ending
        story_beat = StoryBeat(
            beat_text=data.get("beat", ""),
            choices=[],  # No choices for endings
            turns_remaining=0,
            ending=ending,
        )

        return story_beat

    def generate_new_story(self, initial_turns: int = 8) -> StoryBeat:
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

        # Check if the AI wants to end the story
        endstory = data.get("endstory", False)
        if endstory:
            # Create a story ending based on the AI's decision
            ending_type = (
                EndingType.NEUTRAL
            )  # Default to neutral for AI-initiated endings
            reason = "AI determined the story should end"

            # Create the ending
            ending = StoryEnding(
                ending_type=ending_type, ending_text=data.get("beat", ""), reason=reason
            )

            # Create story beat with ending and no choices
            story_beat = StoryBeat(
                beat_text=data.get("beat", ""),
                choices=[],  # No choices for endings
                turns_remaining=0,
                ending=ending,
            )

            # Add to story history
            self.story.add_story_beat(story_beat)
            return story_beat

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
                    1: AdvantageMode.ADVANTAGE,
                    -1: AdvantageMode.DISADVANTAGE,
                    0: AdvantageMode.NORMAL,
                }
                mode = mode_map.get(roll_mode, AdvantageMode.NORMAL)

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
            turns_remaining=initial_turns,
        )

        # Add to story history
        self.story.add_story_beat(story_beat)

        return story_beat

    def continue_story(self, choice_id: int, success_result: str) -> StoryBeat:
        """Continue the story based on a player's choice and its outcome."""
        # Find the choice that was made
        current_beat = self.story.story_beats[-1] if self.story.story_beats else None
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

        # Calculate remaining turns
        turns_remaining = (
            current_beat.turns_remaining - 1 if current_beat.turns_remaining else None
        )

        # Check if the story should end
        should_end, ending_type, reason = self._should_end_story(
            success_result, turns_remaining
        )
        if should_end:
            # Generate story ending
            story_ending = self._generate_story_ending(
                ending_type, reason, story_history
            )
            return story_ending

        # Generate new story beat
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

        # Check if the AI wants to end the story
        endstory = data.get("endstory", False)
        if endstory:
            # Determine ending type based on the success result
            if "Success" in success_result or "success" in success_result.lower():
                ending_type = EndingType.VICTORY
                reason = "Player achieved a major victory"
            else:
                ending_type = EndingType.DEFEAT
                reason = "Player suffered a critical failure"

            # Create the ending
            ending = StoryEnding(
                ending_type=ending_type, ending_text=data.get("beat", ""), reason=reason
            )

            # Create story beat with ending and no choices
            story_beat = StoryBeat(
                beat_text=data.get("beat", ""),
                choices=[],  # No choices for endings
                turns_remaining=0,
                ending=ending,
            )

            # Add to story history
            self.story.add_story_beat(story_beat)
            return story_beat

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
                    1: AdvantageMode.ADVANTAGE,
                    -1: AdvantageMode.DISADVANTAGE,
                    0: AdvantageMode.NORMAL,
                }
                mode = mode_map.get(roll_mode, AdvantageMode.NORMAL)

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
            turns_remaining=turns_remaining,
        )

        # Add to story history
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
