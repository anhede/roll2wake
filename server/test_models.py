#!/usr/bin/env python3
"""
Test file to demonstrate the new StoryBeat and Choice classes
"""

from models import StoryBeat, Choice, AdvantageMode
import json


def test_choice_creation():
    """Test creating Choice objects"""
    print("=== Testing Choice Creation ===")
    
    # Create choices with different modes
    choice1 = Choice(1, "Venture into the city remains", 15, AdvantageMode.NORMAL)
    choice2 = Choice(2, "Search your ship for supplies", 10, AdvantageMode.ADVANTAGE)
    choice3 = Choice(3, "Activate ship's sensor array", 18, AdvantageMode.DISADVANTAGE)
    
    print(f"Choice 1: {choice1}")
    print(f"Choice 2: {choice2}")
    print(f"Choice 3: {choice3}")
    print()


def test_choice_serialization():
    """Test Choice serialization to/from dict"""
    print("=== Testing Choice Serialization ===")
    
    # Create a choice
    original_choice = Choice(1, "Test choice", 12, AdvantageMode.ADVANTAGE)
    
    # Convert to dict
    choice_dict = original_choice.to_dict()
    print(f"Choice as dict: {json.dumps(choice_dict, indent=2)}")
    
    # Convert back from dict
    reconstructed_choice = Choice.from_dict(choice_dict)
    print(f"Reconstructed choice: {reconstructed_choice}")
    print(f"Are they equal? {original_choice.choice_id == reconstructed_choice.choice_id}")
    print()


def test_story_beat_creation():
    """Test creating StoryBeat objects"""
    print("=== Testing StoryBeat Creation ===")
    
    # Create some choices
    choices = [
        Choice(1, "Go left", 10, AdvantageMode.NORMAL),
        Choice(2, "Go right", 15, AdvantageMode.ADVANTAGE),
        Choice(3, "Stay put", 5, AdvantageMode.DISADVANTAGE)
    ]
    
    # Create a story beat
    story_beat = StoryBeat(
        beat_text="You stand at a crossroads in the dark forest...",
        choices=choices,
        turns_remaining=5
    )
    
    print(f"Story Beat: {story_beat}")
    print(f"Beat text: {story_beat.beat_text}")
    print(f"Number of choices: {len(story_beat.choices)}")
    print(f"Turns remaining: {story_beat.turns_remaining}")
    print()


def test_story_beat_serialization():
    """Test StoryBeat serialization"""
    print("=== Testing StoryBeat Serialization ===")
    
    # Create a story beat
    choices = [
        Choice(1, "Fight the dragon", 20, AdvantageMode.DISADVANTAGE),
        Choice(2, "Run away", 8, AdvantageMode.ADVANTAGE)
    ]
    
    original_beat = StoryBeat(
        beat_text="A mighty dragon appears before you!",
        choices=choices,
        turns_remaining=3
    )
    
    # Convert to dict
    beat_dict = original_beat.to_dict()
    print("StoryBeat as dict:")
    print(json.dumps(beat_dict, indent=2))
    print()


def test_from_dict_methods():
    """Test creating objects from dictionary data"""
    print("=== Testing from_dict Methods ===")
    
    # Sample new story data
    new_story_data = {
        "story_intro": "Welcome to the adventure!",
        "choices": [
            {"id": 1, "label": "Start the journey", "DC": 10, "mode": "normal"},
            {"id": 2, "label": "Gather supplies first", "DC": 8, "mode": "advantage"}
        ]
    }
    
    # Sample reaction data
    reaction_data = {
        "story_beat": "You encounter a mysterious door...",
        "choices": [
            {"id": 1, "label": "Open the door", "DC": 12, "mode": "normal"},
            {"id": 2, "label": "Listen at the door", "DC": 6, "mode": "advantage"}
        ],
        "turns_remaining": 4
    }
    
    # Create StoryBeat objects from the data
    new_story_beat = StoryBeat.from_new_story_dict(new_story_data)
    reaction_beat = StoryBeat.from_reaction_dict(reaction_data)
    
    print(f"New story beat: {new_story_beat}")
    print(f"Reaction beat: {reaction_beat}")
    print()


if __name__ == "__main__":
    test_choice_creation()
    test_choice_serialization()
    test_story_beat_creation()
    test_story_beat_serialization()
    test_from_dict_methods()
    
    print("All tests completed successfully!") 