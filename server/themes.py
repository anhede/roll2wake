import random

# Theme categories for small DnD campaigns
SETTINGS = ['medieval', 'sci-fi', 'steampunk', 'post-apocalyptic', 'fantasy', 'western', 'urban']
PLOT_TYPES = ['escape', 'rescue mission', 'heist', 'investigation', 'delivery', 'exploration', 'survival']
CHARACTER_ROLES = ['hero', 'villain', 'partner in crime', 'mercenary', 'spy', 'outlaw', 'guardian']

def generate_theme():
    """Generate a random DnD story theme as a list of three elements."""
    return [
        random.choice(SETTINGS),
        random.choice(PLOT_TYPES), 
        random.choice(CHARACTER_ROLES)
    ]

def get_random_themes():
    """Get a list of random themes for story generation."""
    return generate_theme()

if __name__ == "__main__":
    # Generate and display a random theme
    theme = generate_theme()
    print(f"Generated theme: {theme}")
