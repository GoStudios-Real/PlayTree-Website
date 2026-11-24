"""Cutscene player for PLAYTREE - loads animated GIF frames and plays them
fullscreen with pygame. Graceful fallback if PIL unavailable or files missing.
"""
import pygame
import os
import sys

def _find_dir():
    if getattr(sys, 'frozen', False):
        p = os.path.join(sys._MEIPASS, 'assets', 'hd', 'cutscenes')
        if os.path.exists(p):
            return p
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     'assets', 'hd', 'cutscenes')
    if os.path.exists(p):
        return p
    return os.path.join(os.getcwd(), 'assets', 'hd', 'cutscenes')

DIR = _find_dir()
_cache = {}

def load(name):
    """Return list of pygame surfaces for the GIF, or None."""
    if name in _cache:
        return _cache[name]
    path = os.path.join(DIR, name + '.gif')
    if not os.path.exists(path):
        _cache[name] = None
        return None
    try:
        from PIL import Image, ImageSequence
        im = Image.open(path)
        frames = []
        for f in ImageSequence.Iterator(im):
            rgb = f.convert('RGB')
            mode = rgb.tobytes()
            surf = pygame.image.fromstring(mode, rgb.size, 'RGB')
            frames.append(surf)
        dur = im.info.get('duration', 83) / 1000.0
        _cache[name] = (frames, dur)
        return _cache[name]
    except Exception:
        _cache[name] = None
        return None


class CutscenePlayer:
    def __init__(self):
        self.data = None
        self.name = None
        self.t = 0.0

    def play(self, name):
        d = load(name)
        if d:
            self.data = d
            self.name = name
            self.t = 0.0
            return True
        return False

    @property
    def active(self):
        return self.data is not None

    def update(self, dt):
        if not self.active:
            return
        self.t += dt
        frames, dur = self.data
        if self.t >= len(frames) * dur:
            self.stop()

    def stop(self):
        self.data = None
        self.name = None

    def handle_event(self, event):
        """Skip on any key/click."""
        if not self.active:
            return False
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self.stop()
            return True
        return False

    def draw(self, screen):
        if not self.active:
            return
        frames, dur = self.data
        idx = min(int(self.t / dur), len(frames) - 1)
        img = frames[idx]
        # scale to fill screen while keeping aspect
        sw, sh = screen.get_size()
        ratio = min(sw / img.get_width(), sh / img.get_height())
        nw, nh = int(img.get_width() * ratio), int(img.get_height() * ratio)
        scaled = pygame.transform.smoothscale(img, (nw, nh))
        screen.fill((0, 0, 0))
        screen.blit(scaled, ((sw - nw) // 2, (sh - nh) // 2))
