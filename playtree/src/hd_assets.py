"""Load HD animated sprite sheets and TTS voice lines with graceful fallback."""
import pygame
import os
import sys

def _find_hd():
    if getattr(sys, 'frozen', False):
        p = os.path.join(sys._MEIPASS, 'assets', 'hd')
        if os.path.exists(p):
            return p
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'hd')
    if os.path.exists(p):
        return p
    return os.path.join(os.getcwd(), 'assets', 'hd')

HD = _find_hd()
_cache = {}

def sheet(name):
    if name in _cache:
        return _cache[name]
    p = os.path.join(HD, name)
    if os.path.exists(p):
        try:
            img = pygame.image.load(p).convert_alpha()
            _cache[name] = img
            return img
        except Exception:
            pass
    _cache[name] = None
    return None

def frame(name, index, total=4):
    """Extract frame `index` from a horizontal sprite sheet."""
    s = sheet(name)
    if not s:
        return None
    w = s.get_width() // total
    return s.subsurface((index * w, 0, w, s.get_height()))

def voice(name):
    key = 'v_' + name
    if key in _cache:
        return _cache[key]
    p = os.path.join(HD, 'voice', name + '.wav')
    if os.path.exists(p):
        try:
            s = pygame.mixer.Sound(p)
            _cache[key] = s
            return s
        except Exception:
            pass
    _cache[key] = None
    return None

def play_voice(name, volume=0.8):
    s = voice(name)
    if s:
        s.set_volume(volume)
        s.play()
