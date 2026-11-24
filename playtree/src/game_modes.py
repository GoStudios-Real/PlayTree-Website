"""PLAYTREE Game Modes - Story, Online, Sandbox.
Each mode has its own map, rules, loading text and spawn configuration.
"""
from config import WIDTH, HEIGHT

MODES = {
    "story": {
        "name": "Story Mode",
        "icon": "📖",
        "desc": "Chapter 0: Season 0. Follow the campaign, defeat bosses, restore the Tree Cores.",
        "map": "forest",
        "map_name": "THE FOREST AWAKENING",
        "loading": "Loading Chapter 0...",
        "enemies": 8,
        "bosses": True,
        "rounds": True,
        "saving": True,
        "sky": (10, 30, 12),
        "ground": (20, 55, 25),
        "accent": (85, 239, 120),
    },
    "online": {
        "name": "Online Mode",
        "icon": "🌐",
        "desc": "Team up with friends or face other players on live multiplayer servers.",
        "map": "arena",
        "map_name": "THE CORRUPTED ARENA",
        "loading": "Connecting to server...",
        "enemies": 6,
        "bosses": False,
        "rounds": False,
        "saving": False,
        "sky": (30, 10, 40),
        "ground": (60, 20, 50),
        "accent": (200, 120, 255),
    },
    "sandbox": {
        "name": "Sandbox Mode",
        "icon": "🏗️",
        "desc": "No objectives. Build, explore, tame creatures, and experiment freely.",
        "map": "sanctuary",
        "map_name": "THE PLAYTREE SANCTUARY",
        "loading": "Building your sanctuary...",
        "enemies": 2,
        "bosses": False,
        "rounds": False,
        "saving": True,
        "sky": (15, 40, 50),
        "ground": (30, 80, 70),
        "accent": (120, 220, 255),
    },
}

MODE_ORDER = ["story", "online", "sandbox"]


def get_mode(key):
    return MODES.get(key, MODES["story"])
