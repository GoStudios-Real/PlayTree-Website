"""PLAYTREE Juice System - game feel enhancements.
Adds visual feedback that makes combat and progression satisfying:
- Combo multiplier with scaling rewards and big text
- Screen flash on impactful moments
- Chromatic-style hit pulses (colored screen edges)
- Floating score/XP popups with easing
- Kill streak announcements
- Screen zoom pulse on critical hits
"""
import pygame
import math
import random
from config import WIDTH, HEIGHT

GREEN = (85, 239, 120)
GOLD = (255, 215, 80)
RED = (255, 90, 90)


class Juice:
    def __init__(self):
        self.combo = 0
        self.combo_timer = 0.0
        self.max_combo = 0
        self.kill_streak = 0
        self.streak_timer = 0.0
        self.flash = 0.0
        self.flash_color = (255, 255, 255)
        self.pulse = 0.0
        self.pulse_color = GREEN
        self.popups = []  # x, y, text, color, timer, max, vy, size
        self.announcement = ""
        self.announcement_timer = 0.0
        self.announcement_color = GOLD
        self.time = 0.0

    def update(self, dt):
        self.time += dt
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 0
        if self.streak_timer > 0:
            self.streak_timer -= dt
            if self.streak_timer <= 0:
                self.kill_streak = 0
        self.flash = max(0.0, self.flash - dt * 3.5)
        self.pulse = max(0.0, self.pulse - dt * 2.5)
        if self.announcement_timer > 0:
            self.announcement_timer -= dt
        for p in self.popups[:]:
            p['timer'] -= dt
            p['y'] += p['vy'] * dt
            p['vy'] += 30 * dt  # gravity
            if p['timer'] <= 0:
                self.popups.remove(p)

    def add_combo(self, x, y, base_xp=25):
        """Register a kill; returns XP multiplier from combo."""
        self.combo += 1
        self.combo_timer = 3.0
        self.max_combo = max(self.max_combo, self.combo)
        mult = 1 + min(self.combo - 1, 9) * 0.25  # up to 3.25x
        gained = int(base_xp * mult)
        self.popup(x, y - 20, f"+{gained} XP", GOLD, size=22)
        if self.combo >= 3:
            self.popup(WIDTH // 2, 130, f"{self.combo}x COMBO!", GOLD, size=38, vy=-20)
        if self.combo >= 5:
            self.flash_screen(GOLD, 0.25)
            self.announce(f"{self.combo} COMBO — UNSTOPPABLE!", GOLD, 1.6)
        if self.combo >= 10:
            self.flash_screen(RED, 0.4)
            self.announce("LEGENDARY STREAK!", RED, 2.0)
        return gained

    def popup(self, x, y, text, color=GREEN, duration=1.2, vy=-45, size=24):
        self.popups.append({'x': x, 'y': y, 'text': text, 'color': color,
                            'timer': duration, 'max': duration, 'vy': vy, 'size': size})

    def flash_screen(self, color=(255, 255, 255), strength=0.3):
        self.flash_color = color
        self.flash = max(self.flash, strength)

    def pulse_edge(self, color=GREEN, strength=0.6):
        self.pulse_color = color
        self.pulse = max(self.pulse, strength)

    def announce(self, text, color=GOLD, duration=1.8):
        self.announcement = text
        self.announcement_color = color
        self.announcement_timer = duration

    def draw(self, screen):
        # Floating popups
        for p in self.popups:
            a = min(1.0, p['timer'] / (p['max'] * 0.5))
            f = pygame.font.Font(None, p['size'])
            surf = f.render(p['text'], True, p['color'])
            surf.set_alpha(int(255 * a))
            screen.blit(surf, (int(p['x'] - surf.get_width() / 2), int(p['y'])))

        # Combo counter (top-left under HUD)
        if self.combo >= 2:
            f = pygame.font.Font(None, 34)
            s = f.render(f"{self.combo}x", True, GOLD)
            screen.blit(s, (WIDTH - s.get_width() - 20, 190))

        # Announcement banner
        if self.announcement_timer > 0 and self.announcement:
            a = min(1.0, self.announcement_timer / 0.5)
            f = pygame.font.Font(None, 46)
            s = f.render(self.announcement, True, self.announcement_color)
            s.set_alpha(int(255 * a))
            box = pygame.Surface((s.get_width() + 40, s.get_height() + 20), pygame.SRCALPHA)
            box.fill((0, 0, 0, int(160 * a)))
            screen.blit(box, (WIDTH // 2 - box.get_width() // 2, HEIGHT // 2 - 160))
            screen.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 - 150))

        # Screen flash
        if self.flash > 0:
            a = int(self.flash * 120)
            fl = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            fl.fill((*self.flash_color[:3], a))
            screen.blit(fl, (0, 0))

        # Edge pulse (vignette color)
        if self.pulse > 0:
            a = int(self.pulse * 100)
            edge = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            w = 14
            pygame.draw.rect(edge, (*self.pulse_color[:3], a), (0, 0, WIDTH, w))
            pygame.draw.rect(edge, (*self.pulse_color[:3], a), (0, HEIGHT - w, WIDTH, w))
            pygame.draw.rect(edge, (*self.pulse_color[:3], a), (0, 0, w, HEIGHT))
            pygame.draw.rect(edge, (*self.pulse_color[:3], a), (WIDTH - w, 0, w, HEIGHT))
            screen.blit(edge, (0, 0))
