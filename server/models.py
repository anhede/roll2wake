from typing import List, Optional
from enum import IntEnum


class AdvantageMode(IntEnum):
    """Enum for advantage/disadvantage modes"""
    DISADVANTAGE = -1
    NORMAL = 0
    ADVANTAGE = 1


class EndingType(IntEnum):
    """Enum for different types of story endings"""
    VICTORY = 1
    DEFEAT = 2
    NEUTRAL = 3


class StoryEnding:
    """Represents a story ending with type and narrative text"""
    
    def __init__(self, ending_type: EndingType, ending_text: str, reason: str):
        self.ending_type = ending_type
        self.ending_text = ending_text
        self.reason = reason
    
    def __repr__(self) -> str:
        return f"StoryEnding(type={self.ending_type.name}, reason='{self.reason}')"


class Choice:
    """Represents a choice in the story with its difficulty and advantage mode"""
    
    def __init__(self, choice_id: int, label: str, difficulty: int, mode: AdvantageMode = AdvantageMode.NORMAL):
        self.choice_id = choice_id
        self.label = label
        self.difficulty = difficulty
        self.mode = mode
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Choice':
        """Create a Choice from a dictionary (for JSON deserialization)"""
        mode_str = data.get('mode', 'normal').lower()
        mode_map = {
            'advantage': AdvantageMode.ADVANTAGE,
            'disadvantage': AdvantageMode.DISADVANTAGE,
            'normal': AdvantageMode.NORMAL
        }
        mode = mode_map.get(mode_str, AdvantageMode.NORMAL)
        
        return cls(
            choice_id=data['id'],
            label=data['label'],
            difficulty=data['DC'],
            mode=mode
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary (for JSON serialization)"""
        mode_str_map = {
            AdvantageMode.ADVANTAGE: 'advantage',
            AdvantageMode.DISADVANTAGE: 'disadvantage',
            AdvantageMode.NORMAL: 'normal'
        }
        
        return {
            'id': self.choice_id,
            'label': self.label,
            'DC': self.difficulty,
            'mode': mode_str_map[self.mode]
        }
    
    def __repr__(self) -> str:
        return f"{self.choice_id}. {self.label} ({self.difficulty} {self.mode.name})"


class StoryBeat:
    """Represents a story beat with text and available choices"""
    
    def __init__(self, beat_text: str, choices: List[Choice], turns_remaining: Optional[int] = None, ending: Optional[StoryEnding] = None):
        self.beat_text = beat_text
        self.choices = choices
        self.turns_remaining = turns_remaining
        self.ending = ending
    
    @property
    def is_ending(self) -> bool:
        """Check if this story beat represents an ending"""
        return self.ending is not None
    
    @classmethod
    def from_new_story_dict(cls, data: dict) -> 'StoryBeat':
        """Create a StoryBeat from a new story response dictionary"""
        choices = [Choice.from_dict(choice_data) for choice_data in data.get('choices', [])]
        return cls(
            beat_text=data.get('story_intro', ''),
            choices=choices
        )
    
    @classmethod
    def from_reaction_dict(cls, data: dict) -> 'StoryBeat':
        """Create a StoryBeat from a reaction response dictionary"""
        choices = [Choice.from_dict(choice_data) for choice_data in data.get('choices', [])]
        return cls(
            beat_text=data.get('story_beat', ''),
            choices=choices,
            turns_remaining=data.get('turns_remaining')
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary (for JSON serialization)"""
        result = {
            'story_beat': self.beat_text,
            'choices': [choice.to_dict() for choice in self.choices]
        }
        if self.turns_remaining is not None:
            result['turns_remaining'] = self.turns_remaining
        if self.ending is not None:
            result['ending'] = {
                'type': self.ending.ending_type.value,
                'text': self.ending.ending_text,
                'reason': self.ending.reason
            }
        return result
    
    def __repr__(self) -> str:
        ending_info = f", ending={self.ending}" if self.ending else ""
        return f"StoryBeat(beat_text='{self.beat_text[:50]}...', choices={len(self.choices)}, turns_remaining={self.turns_remaining}{ending_info})" 