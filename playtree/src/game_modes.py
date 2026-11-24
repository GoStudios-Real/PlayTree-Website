"""PLAYTREE Game Modes - real distinct rules, spawns and maps.
Each mode changes: objectives, enemies, resources, HUD, map layout & rules.
"""
from config import WIDTH, HEIGHT
import pygame
import math
import random

MODES = {
    "story": {
        "name": "Story Mode", "icon": "S", "map": "forest",
        "map_name": "THE FOREST AWAKENING",
        "desc": "Campaign: defeat rounds, fight bosses, restore 5 Tree Cores.",
        "goal": "RESTORE THE TREE CORES",
        "enemies": 8, "bosses": True, "rounds": True, "saving": True,
        "pvp": False, "build": True, "tame": True, "infinite_resources": False,
        "sky": (10, 30, 12), "ground": (20, 55, 25), "accent": (85, 239, 120),
        "spawn_resource": "Tree Energy", "spawn_amount": 3,
    },
    "online": {
        "name": "Online Mode", "icon": "O", "map": "arena",
        "map_name": "THE CORRUPTED ARENA",
        "desc": "PvP arena: fight other players, capture points, climb the leaderboard.",
        "goal": "DEFEAT OTHER PLAYERS",
        "enemies": 4, "bosses": False, "rounds": False, "saving": False,
        "pvp": True, "build": False, "tame": False, "infinite_resources": False,
        "sky": (30, 10, 40), "ground": (60, 20, 50), "accent": (200, 120, 255),
        "spawn_resource": "Gold Leaves", "spawn_amount": 50,
    },
    "sandbox": {
        "name": "Sandbox Mode", "icon": "B", "map": "sanctuary",
        "map_name": "THE PLAYTREE SANCTUARY",
        "desc": "Creative: unlimited resources, build freely, no enemies attacking.",
        "goal": "BUILD & EXPLORE FREELY",
        "enemies": 0, "bosses": False, "rounds": False, "saving": True,
        "pvp": False, "build": True, "tame": True, "infinite_resources": True,
        "sky": (15, 40, 50), "ground": (30, 80, 70), "accent": (120, 220, 255),
        "spawn_resource": "Ancient Seeds", "spawn_amount": 99,
    },
}
MODE_ORDER = ["story", "online", "sandbox"]

# Map-specific static features drawn in world space
MAP_FEATURES = {
    "forest": [
        ("tree", 200, 300), ("tree", 600, 200), ("tree", 1000, 400),
        ("tree", 1400, 250), ("rock", 400, 500), ("rock", 1200, 450),
    ],
    "arena": [
        ("pillar", 300, 200), ("pillar", 900, 200), ("pillar", 300, 500), ("pillar", 900, 500),
        ("trap", 600, 350), ("trap", 600, 150), ("trap", 600, 550),
    ],
    "sanctuary": [
        ("fountain", 700, 350), ("platform", 200, 250), ("platform", 1100, 250),
        ("tree", 500, 150), ("tree", 900, 550), ("crystal", 700, 100),
    ],
}


def get_mode(key):
    return MODES.get(key, MODES["story"])


def draw_map(screen, cam_x, cam_y, mode_key, t=0):
    """Draw map-specific terrain features in screen space."""
    features = MAP_FEATURES.get(mode_key, [])
    accent = get_mode(mode_key)["accent"]
    for kind, wx, wy in features:
        x, y = int(wx - cam_x), int(wy - cam_y)
        if x < -120 or x > WIDTH + 120 or y < -120 or y > HEIGHT + 120:
            continue
        if kind == "tree":
            pygame.draw.rect(screen, (50, 35, 20), (x - 12, y, 24, 70))
            for dx, dy, r in [(0, -20, 48), (-35, 5, 32), (35, 5, 32)]:
                pygame.draw.circle(screen, (40, 120, 55), (x + dx, y + dy), r)
                pygame.draw.circle(screen, (60, 170, 75), (x + dx, y + dy - 8), int(r * 0.6))
        elif kind == "rock":
            pygame.draw.ellipse(screen, (90, 90, 100), (x - 30, y - 20, 60, 40))
            pygame.draw.ellipse(screen, (120, 120, 130), (x - 18, y - 26, 36, 24))
        elif kind == "pillar":
            pygame.draw.rect(screen, (60, 30, 70), (x - 20, y - 60, 40, 120))
            pygame.draw.rect(screen, accent[:3], (x - 20, y - 60, 40, 4))
            pygame.draw.circle(screen, (*accent[:3], 100), (x, y - 60), 18 + int(math.sin(t * 2 + x) * 4), 2)
        elif kind == "trap":
            r = 26 + int(math.sin(t * 3 + wx) * 4)
            pygame.draw.circle(screen, (200, 40, 60, 60), (x, y), r, 3)
            pygame.draw.circle(screen, (255, 80, 80), (x, y), 6)
        elif kind == "fountain":
            pygame.draw.ellipse(screen, (40, 90, 100), (x - 60, y - 20, 120, 50))
            pygame.draw.ellipse(screen, (80, 180, 220), (x - 45, y - 15, 90, 35))
            for i in range(4):
                a = t * 2 + i * 1.57
                px, py = x + math.cos(a) * 30, y - 25 - abs(math.sin(a)) * 40
                pygame.draw.circle(screen, (150, 220, 255), (int(px), int(py)), 3)
        elif kind == "platform":
            pygame.draw.rect(screen, (50, 80, 90), (x - 60, y - 10, 120, 20), border_radius=6)
            pygame.draw.rect(screen, accent[:3], (x - 60, y - 10, 120, 3))
        elif kind == "crystal":
            for i in range(3):
                h = 40 + i * 15
                pygame.draw.polygon(screen, (100 + i * 30, 200, 255),
                                    [(x + i * 16 - 8, y), (x + i * 16, y - h), (x + i * 16 + 8, y)])
