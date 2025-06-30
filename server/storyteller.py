import os
import json
from openai import OpenAI
from typing import List, Optional, Tuple
from models import StoryBeat, Choice
from themes import get_random_themes
from models import MODE_DISADVANTAGE, MODE_NORMAL, MODE_ADVANTAGE
from llm import LLM
from prompts import STORYTELLER_SYSTEM_PROMPT, get_new_story_prompt
from utils import get_api_keys
import re
from typing import Any

# Maximum number of attempts to get a valid response from OpenAI
# This is to handle potential API errors or invalid responses
# Happens sometimes due to bad model responses, 
# a single failed attempt may happen in about 1 in 20 requests using gpt-4o-mini
# Having six failed attempts in a row is thus extremely unlikely (1 in 64,200,000)
MAX_ATTEMPTS = 6
LOW_VERBOSE, MEDIUM_VERBOSE, HIGH_VERBOSE = range(3)
VERBOSITY = HIGH_VERBOSE
LINE_STR = "-" * 80

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
                history += f"Story beat: {beats.pop(0).llm_format()}\n"
            if choices:
                choice_tuple = choices.pop(0)
                history += f"Choice: Tried {choice_tuple[0].label}. Result: {choice_tuple[1]}\n"
            history += "\n"
        if VERBOSITY >= HIGH_VERBOSE:
            print(f"Story history to be passed to LLM:\n{LINE_STR}\n{history}\n{LINE_STR}")
        return history


class Storyteller:
    """
    A class to generate and progress interactive DnD-style stories using OpenAI's Chat API.
    """

    def __init__(self, llm: LLM):
        self.llm = llm
        print(f"Initializing Storyteller with model {self.llm}")

    @staticmethod
    def parse_llm_json_response(raw: str) -> dict[str, Any]:
        """
        Robustly parse JSON from LLM response, handling common formatting issues.
        """
        # Remove any leading/trailing whitespace
        raw = raw.strip()
        
        # Remove markdown code blocks if present
        # Handle ```json, ```JSON, or just ```
        raw = re.sub(r'^```(?:json|JSON)?\s*\n', '', raw)
        raw = re.sub(r'\n```\s*$', '', raw)
        
        # If it still doesn't start with { or [, try to find JSON in the response
        if not raw.startswith(('{', '[')):
            # Look for JSON object in the response
            json_match = re.search(r'(\{[^{}]*\{[^{}]*\}[^{}]*\}|\{[^{}]+\})', raw, re.DOTALL)
            if json_match:
                raw = json_match.group(1)
        
        # Try to parse the JSON
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            # Common issue: unescaped quotes in strings
            # Try to fix by escaping quotes that aren't already escaped
            fixed = re.sub(r'(?<!\\)"(?=(?:[^"]*"[^"]*")*[^"]*"[^"]*$)', r'\"', raw)
            try:
                return json.loads(fixed)
            except:
                # If that fails, raise the original error
                raise e


    def _request_story_beat(self, user_content: str) -> StoryBeat | None:
        """
        Send messages to the LLM, parse JSON response, convert to StoryBeat, and record history.
        """
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                raw = self.llm.generate(STORYTELLER_SYSTEM_PROMPT, user_content)
                if VERBOSITY >= HIGH_VERBOSE:
                    print(f"Raw response from LLM (attempt {attempt}):\n{LINE_STR}\n{raw}\n{LINE_STR}")
                data = Storyteller.parse_llm_json_response(raw)
                if VERBOSITY >= HIGH_VERBOSE:
                    print(f"Parsed JSON data (attempt {attempt}):\n{LINE_STR}\n{data}\n{LINE_STR}")
                    
                # Validate required fields
                if not isinstance(data, dict):
                    raise ValueError("Response must be a JSON object")
                
                if "beat" not in data:
                    raise ValueError("Missing required field: beat")


                # Parse choices
                choices: List[Choice] = []
                choice_data = data.get("choices", [])
                
                for choice_str in choice_data:
                    try:
                        parts = choice_str.split(",", 3)
                        if len(parts) < 4:
                            print(f"Warning: Skipping malformed choice: {choice_str}")
                            continue
                            
                        cid, label, diff, mode = parts
                        mode_map = {"1": MODE_ADVANTAGE, "-1": MODE_DISADVANTAGE, "0": MODE_NORMAL}
                        
                        choices.append(
                            Choice(
                                choice_id=int(cid.strip()),
                                label=label.strip(),
                                difficulty=int(diff.strip()),
                                mode=mode_map.get(mode.strip(), MODE_NORMAL),
                            )
                        )
                    except (ValueError, AttributeError) as e:
                        print(f"Warning: Error parsing choice '{choice_str}': {e}")
                        continue


                if VERBOSITY >= HIGH_VERBOSE:
                    print(f"Parsed choices: {choices}")

                # Build beat
                story_beat = StoryBeat(
                    beat_text=data.get("beat"),
                    choices=choices,
                    npcs=data.get("npcs", []),
                    atmosphere=data.get("atmosphere", ""),
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
        prompt = get_new_story_prompt(themes)
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
        prompt = f"Story history:\n{history}\n\nGenerate the next story beat and choices based on this outcome."
        if VERBOSITY >= HIGH_VERBOSE:
            print(f"Continuing story with prompt:\n{LINE_STR}{prompt}\n{LINE_STR}")
        beat = self._request_story_beat(prompt)
        if not beat:
            raise ValueError("Failed to continue the story")
        return beat

if __name__ == "__main__":
    from llm import OpenAILLM
    api_key_openai = get_api_keys().get("openai")
    api_key_anthropic = get_api_keys().get("anthropic")
    storyteller = Storyteller(OpenAILLM(api_key_openai)) # type: ignore

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
