AdvantageMode = int
MODE_DISADVANTAGE = -1
MODE_NORMAL = 0
MODE_ADVANTAGE = 1
MODES_STRINGS = {
    MODE_DISADVANTAGE: "disadvantage",
    MODE_NORMAL: "normal",
    MODE_ADVANTAGE: "advantage",
}
MODES_SYMBOLS = {MODE_DISADVANTAGE: "-", MODE_NORMAL: "", MODE_ADVANTAGE: "+"}


class Choice:
    """Represents a choice in the story with its difficulty and advantage mode"""

    def __init__(
        self,
        choice_id: int,
        label: str,
        difficulty: int,
        mode: AdvantageMode = MODE_NORMAL,
    ):
        self.choice_id = choice_id
        self.label = label
        self.difficulty = difficulty
        self.mode = mode

    @classmethod
    def from_dict(cls, data: dict) -> "Choice":
        """Create a Choice from a dictionary (for JSON deserialization)"""
        mode_str = data.get("mode", "normal").lower()
        mode_map = {
            "advantage": MODE_ADVANTAGE,
            "disadvantage": MODE_DISADVANTAGE,
            "normal": MODE_NORMAL,
        }
        mode = mode_map.get(mode_str, MODE_NORMAL)

        return cls(
            choice_id=data["id"], label=data["label"], difficulty=data["DC"], mode=mode
        )

    def to_dict(self) -> dict:
        """Convert to dictionary (for JSON serialization)"""
        mode_str_map = {
            MODE_ADVANTAGE: "advantage",
            MODE_DISADVANTAGE: "disadvantage",
            MODE_NORMAL: "normal",
        }

        return {
            "id": self.choice_id,
            "label": self.label,
            "DC": self.difficulty,
            "mode": mode_str_map[self.mode],
        }

    def __repr__(self) -> str:
        return f"{self.choice_id}. {self.label} ({self.difficulty}{MODES_SYMBOLS[self.mode]})"


class StoryBeat:
    """Represents a story beat with text and available choices"""

    def __init__(
        self,
        beat_text: str,
        choices: list[Choice],
        npcs: list[str],
        atmosphere: str = "",
        is_ending: bool = False,
    ):
        self.beat_text = beat_text
        self.choices = choices
        self.npcs = npcs
        self.atmosphere = atmosphere
        self.is_ending = is_ending

    @classmethod
    def from_dict(cls, data: dict) -> "StoryBeat":
        """Create a StoryBeat from a dictionary (for JSON deserialization)"""
        choices = [Choice.from_dict(choice_data) for choice_data in data["choices"]]
        return cls(
            beat_text=data["story_beat"],
            choices=choices,
            npcs=data.get("npcs", []),
            atmosphere=data.get("atmosphere", ""),
            is_ending=data.get("is_ending", False),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary (for JSON serialization)"""
        result = {
            "story_beat": self.beat_text,
            "choices": [choice.to_dict() for choice in self.choices],
            "npcs": self.npcs,
            "atmosphere": self.atmosphere,
            "is_ending": self.is_ending,
        }
        return result

    def full_format(self) -> str:
        """Return a full formatted string of the story beat"""
        choices_str = "\n".join(repr(choice) for choice in self.choices)
        return f"{self.beat_text}\n\nChoices:\n{choices_str}"
    
    def llm_format(self) -> str:
        """Return a formatted string for LLM input"""
        choices_str = ", ".join(
            f"{choice.choice_id},{choice.label},{choice.difficulty},{MODES_STRINGS[choice.mode]}"
            for choice in self.choices
        )
        return (
            f'{{"beat": "{self.beat_text}", "choices": [{choices_str}], '
            f'"npcs": {self.npcs}, "atmosphere": "{self.atmosphere}", "endstory": {str(self.is_ending).lower()}}}'
        )

    def __repr__(self) -> str:
        return f"StoryBeat(beat_text='{self.beat_text[:50]}...', choices={len(self.choices)}, is_ending={self.is_ending})"
