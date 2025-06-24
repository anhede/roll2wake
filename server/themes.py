import random

# Theme categories for small DnD campaigns
MOOD = ["dark", "tragic", "epic", "adventure", "scary", "mysterious", "thrilling"]
GENRES = [
    "medieval",
    "sci-fi",
    "steampunk",
    "post-apocalyptic",
    "fantasy",
    "western",
    "urban",
    "horror",
]
PLOT_TYPES = [
    "escape",
    "rescue mission",
    "heist",
    "investigation",
    "delivery",
    "exploration",
    "survival",
]
ROLES = [
    "as the hero",
    "as the villain",
    "with a partner",
    "as a mercenary",
    "as a spy",
    "as an outlaw",
    "as a commoner",
]
LOCATIONS = [
    "on a vehicle",
    "underground",
    "above ground",
    "in the sky",
    "in a city",
    "in the wilderness",
    "in a building",
    "in a dark place you dont know",
]
HEALTH_STATE = [
    "uninjured",
    "injured",
]
ARMED_STATE = ["unarmed", "lightly armed", "heavily armed"]

# Percentage chance of no mood
MOOD_EMPTY = 50
GENRES_EMPTY = 10
PLOT_TYPES_EMPTY = 30
ROLES_EMPTY = 50
LOCATIONS_EMPTY = 30
HEALTH_STATE_EMPTY = 30
ARMED_STATE_EMPTY = 30


def generate_theme() -> list[str]:
    """Generate a random DnD story theme as a list."""
    mood = MOOD if random.randint(0, 100) > MOOD_EMPTY else [""]
    genres = GENRES if random.randint(0, 100) > GENRES_EMPTY else [""]
    plot_types = PLOT_TYPES if random.randint(0, 100) > PLOT_TYPES_EMPTY else [""]
    roles = ROLES if random.randint(0, 100) > ROLES_EMPTY else [""]
    locations = LOCATIONS if random.randint(0, 100) > LOCATIONS_EMPTY else [""]
    health_state = HEALTH_STATE if random.randint(0, 100) > HEALTH_STATE_EMPTY else [""]
    armed_state = ARMED_STATE if random.randint(0, 100) > ARMED_STATE_EMPTY else [""]
    return [
        random.choice(mood),  # type: ignore
        random.choice(genres),  # type: ignore
        random.choice(plot_types),  # type: ignore
        random.choice(roles),  # type: ignore
        random.choice(locations),  # type: ignore
        random.choice(health_state),  # type: ignore
        random.choice(armed_state),  # type: ignore
    ]


def get_random_themes() -> list[str]:
    """Get a list of random themes for story generation."""
    return generate_theme()


if __name__ == "__main__":
    # Generate and display a random theme
    themes = [generate_theme() for _ in range(5)]
    for theme in themes:
        print(" ".join(theme))
