"""Record a 30-second devlog clip of PLAYTREE combat (headless render).

Runs the game offscreen with simulated combat, crops the center gameplay view
(avoiding headless-only edge artifacts), adds TikTok-style captions, and saves
an animated GIF suitable for upload as a video clip.

Output: playtree/devlog_clip_01.gif
"""
import os, sys
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame
pygame.init()
W, H = 1280, 720
pygame.display.set_mode((W, H))
sys.path.insert(0, '.'); sys.path.insert(0, 'src')

from PIL import Image, ImageDraw, ImageFont
from src.game import Game
from config import GameState

render_surface = pygame.Surface((W, H))
g = Game(render_surface)
g._load_game()
g.state = GameState.PLAYING
g.studio_splash.done = True

FPS = 30
TOTAL = FPS * 30
CAPTIONS = [
    (0, 4, "I made a game where you fight corruption with a MAGIC TREE"),
    (4, 11, "Hit flash + knockback on every strike"),
    (11, 18, "Combo counter + screen shake"),
    (18, 25, "Hit-stop freeze on kills"),
    (25, 30, "PLAYTREE v1.1.2 - Awaken. Rebuild. Restore Balance."),
]

def caption(t):
    for a, b, txt in CAPTIONS:
        if a <= t < b:
            return txt
    return ""

font_path = r"C:\Windows\Fonts\arial.ttf"
font = ImageFont.truetype(font_path, 34) if os.path.exists(font_path) else ImageFont.load_default()
frames = []

for i in range(TOTAL):
    t = i / FPS
    if i % 15 == 0:
        try: g._use_skill("attack")
        except Exception: pass
    if g.player:
        g.player.x += 4 if i % 60 < 30 else -4
    g.update(1.0 / FPS)
    g.draw()
    if i % 2 == 0:
        raw = pygame.image.tostring(render_surface, 'RGB')
        img = Image.frombytes('RGB', (W, H), raw)
        d = ImageDraw.Draw(img)
        cap = caption(t)
        if cap:
            d.rounded_rectangle((60, 620, 1220, 690), radius=14, fill=(5, 15, 8))
            d.text((640, 655), cap, font=font, fill=(85, 239, 120), anchor='mm')
        frames.append(img.convert('P', palette=Image.ADAPTIVE, colors=128))

out = os.path.join(os.path.dirname(__file__), 'devlog_clip_01.gif')
frames[0].save(out, save_all=True, append_images=frames[1:], duration=66, loop=0)
print(f"Saved {out} ({len(frames)} frames, ~30s)")
print("Upload as a video clip (TikTok/Shorts/Reddit). Captions are baked in.")
