"""Load and cache PLAYTREE PNG/WAV assets. Falls back to code drawing if missing."""
import pygame
import os
import sys

def _find_assets():
    # PyInstaller bundle
    if getattr(sys, 'frozen', False):
        p = os.path.join(sys._MEIPASS, 'assets')
        if os.path.exists(p):
            return p
    # source layout: playtree/assets (parent of src/)
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
    if os.path.exists(p):
        return p
    # fallback: cwd/assets
    return os.path.join(os.getcwd(), 'assets')

ASSET_DIR = _find_assets()
_image_cache = {}
_sound_cache = {}

def image(name):
    if name in _image_cache:
        return _image_cache[name]
    path = os.path.join(ASSET_DIR, name)
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            _image_cache[name] = img
            return img
        except Exception:
            pass
    _image_cache[name] = None
    return None

def sound(name):
    if name in _sound_cache:
        return _sound_cache[name]
    path = os.path.join(ASSET_DIR, name)
    if os.path.exists(path):
        try:
            s = pygame.mixer.Sound(path)
            _sound_cache[name] = s
            return s
        except Exception:
            pass
    _sound_cache[name] = None
    return None

def play(name, volume=0.5):
    s = sound(name)
    if s:
        s.set_volume(volume)
        s.play()
