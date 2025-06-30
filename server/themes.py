import random

# Theme categories for small DnD campaigns
MOOD = ["dark", "tragic", "epic", "adventure", "scary", "mysterious", "thrilling"]
GENRES = [
    "medieval",
    "sci-fi",
    "post-apocalyptic",
    "fantasy",
    "western",
    "urban",
    "horror",
    "cyberpunk",
    "steampunk",
    "dieselpunk",
    "ancient mythology",
    "pirate",
    "viking",
    "samurai",
    "noir detective",
    "wild west",
    "renaissance",
    "spy thriller",
    "superhero",
    "heist",
    "survival horror",
    "cosmic horror",
    "military",
    "conspiracy",
    "zombie apocalypse",
    "biopunk",
    "solarpunk",
    "time travel",
    "alternate history",
    "urban fantasy",
    "magical realism",
    "gothic",
    "weird west",
    "mythpunk",
    "cli-fi (climate fiction)",
]
AUTHORS = {
    "medieval": [
        "Geoffrey Chaucer",
        "Thomas Malory",
        "Chrétien de Troyes",
        "Marie de France",
        "Dante Alighieri",
    ],
    "sci-fi": [
        "Isaac Asimov",
        "Philip K. Dick",
        "Arthur C. Clarke",
        "Ursula K. Le Guin",
        "Octavia E. Butler",
    ],
    "steampunk": [
        "K.W. Jeter",
        "James P. Blaylock",
        "Tim Powers",
        "Cherie Priest",
        "Gail Carriger",
    ],
    "post-apocalyptic": [
        "Cormac McCarthy",
        "Stephen King",
        "Emily St. John Mandel",
        "Nevil Shute",
        "Octavia E. Butler",
    ],
    "fantasy": [
        "J.R.R. Tolkien",
        "George R.R. Martin",
        "Brandon Sanderson",
        "Robin Hobb",
        "Patrick Rothfuss",
    ],
    "western": [
        "Louis L'Amour",
        "Zane Grey",
        "Cormac McCarthy",
        "Larry McMurtry",
        "Elmore Leonard",
    ],
    "urban": [
        "Jim Butcher",
        "Neil Gaiman",
        "Patricia Briggs",
        "Laurell K. Hamilton",
        "Charles de Lint",
    ],
    "horror": [
        "Stephen King",
        "H.P. Lovecraft",
        "Shirley Jackson",
        "Clive Barker",
        "Peter Straub",
    ],
}
PLOT_TYPES = [
    "escape",
    "rescue mission",
    "heist",
    "investigation",
    "delivery",
    "exploration",
    "survival",
    "revenge",
    "assassination",
    "ambush",
    "defense",
    "infiltration",
    "time loop",
    "tournament/competition",
    "race against time",
    "rival faction war",
    "bounty hunting",
    "gladiatorial games",
    "prison break"
    "disaster response"
    "plague/outbreak"
    "portal adventure"
    "body swap"
    "parallel universe"
    "haunting/exorcism",
]
ROLES = [
    "with a small group",
    "as the leader of a group",
    "with a partner",
    "as a commoner",
    "as royalty/nobility",
    "as a prisoner/captive",
    "as an exile/outcast",
    "as a chosen one",
    "as a double agent",
    "as the villain",
    "as a mercenary",
    "as a detective/investigator",
    "as a healer/medic",
    "as a spy",
    "as a merchant/trader",
    "as a scholar/researcher",
    "with a rival",
    "with a mentor",
    "alone/solo",
    "with a family member",
    "as part of a crew",
    "with an unlikely companion",
    "as a child",
    "as an elder",
    "undercover/in disguise",
    "with amnesia",
    "as a supernatural being",
    "with a curse/blessing",
    "as a time traveler",
    "controlling multiple characters",
    "as a ghost/spirit",
    "protecting someone",
    "betraying your allies",
    "seeking revenge",
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
    "underwater/ocean depths",
    "in a desert",
    "in the arctic/tundra",
    "inside a volcano",
    "in a swamp/marsh",
    "on a mountain",
    "in a jungle",
    "on an island",
    "in a cave system",
    "in space",
    "on another planet",
    "in another dimension",
    "inside a virtual world",
    "in the afterlife",
    "inside someone's mind",
    "in a time vortex",
    "on a floating city",
    "in a castle/fortress",
    "in ancient ruins",
    "in a laboratory",
    "in a prison",
    "in a hospital",
    "in a mansion/estate",
    "in a space station",
    "in a village",
    "on a moving train",
    "aboard a ship",
    "in a war zone",
    "at a border crossing",
    "in a marketplace/bazaar",
    "in a dream realm",
    "during a natural disaster",
    "in a parallel universe",
    "inside a giant creature",
    "in a quarantine zone",
    "at a crossroads",
    "in a liminal space",
]
HEALTH_STATE = [
    "uninjured",
    "injured",
    "poisoned",
    "exhausted",
    "infected/diseased",
    "partially transformed",
    "enhanced/superhuman",
    "dying/critical",
    "immortal/regenerating",
    "intoxicated/drugged",
    "starving/dehydrated",
    "cursed",
    "possessed",
    "hallucinating",
    "memory-impaired",
    "mind-controlled",
    "berserking",
    "magically drained",
    "prophetic visions",
    "time-limited life",
    "shared damage link",
    "astral projecting",
    "radioactive",
    "invisible",
    "age-shifting",
    "partially phased",
]
ARMED_STATE = [
    "unarmed",
    "lightly armed",
    "heavily armed",
    "magically armed",
    "technologically armed",
    "improvised weapons",
    "biological weapons",
    "psychic abilities",
    "trapped/rigged",
    "vehicle-mounted weapons",
    "pacifist equipped (non-lethal only)",
    "cursed weapon bound",
    "shapeshifting arsenal",
    "experimental prototype",
    "ancient artifact wielder",
    "dual-wielding",
    "concealed weapons",
    "symbiotic weapon",
    "unstable/malfunctioning gear",
]

# Percentage chance of no mood
MOOD_EMPTY = 50
GENRES_EMPTY = 10
AUTHORS_EMPTY = 30
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
    genre = random.choice(genres)
    #authors = (
    #    AUTHORS[genre] if random.randint(0, 100) > AUTHORS_EMPTY and genre else [""]
    #)
    return [
        random.choice(mood),  # type: ignore
        genre,  # type: ignore
        random.choice(plot_types),  # type: ignore
        random.choice(roles),  # type: ignore
        random.choice(locations),  # type: ignore
        random.choice(health_state),  # type: ignore
        random.choice(armed_state),  # type: ignore
        #f"in the style of {random.choice(authors)}" if authors != [""] else "",  # type: ignore
    ]


def get_random_themes() -> list[str]:
    """Get a list of random themes for story generation."""
    return generate_theme()


if __name__ == "__main__":
    # Generate and display a random theme
    themes = [generate_theme() for _ in range(5)]
    for theme in themes:
        print(" ".join(theme))
