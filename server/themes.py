import random

# Theme categories for small DnD campaigns
MOOD = ['dark', 'tragic', 'epic', 'adventure', 'scary']
SETTINGS = ['medieval', 'sci-fi', 'steampunk', 'post-apocalyptic', 'fantasy', 'western', 'urban', 'horror']
PLOT_TYPES = ['escape', 'rescue mission', 'heist', 'investigation', 'delivery', 'exploration', 'survival']
CHARACTER_ROLES = ['as the hero', 'as the villain', 'with a partner', 'as a mercenary', 'as a spy', 'as an outlaw', 'as a commoner']

def generate_theme() -> list[str]:
    """Generate a random DnD story theme as a list."""
    return [
        random.choice(MOOD), # type: ignore
        random.choice(SETTINGS), # type: ignore
        random.choice(PLOT_TYPES),  # type: ignore
        random.choice(CHARACTER_ROLES) # type: ignore
    ]

def get_random_themes() -> list[str]:
    """Get a list of random themes for story generation."""
    return generate_theme()

if __name__ == "__main__":
    # Generate and display a random theme
    theme = generate_theme()
    print(f"Generated theme: {theme}")
