"""PLAYTREE loading screen with Play button.
Shown on startup in desktop, web (pygbag), and Android builds.
Loads assets progressively, then waits for the player to press PLAY.
"""
import pygame
import math
import os
import sys
from config import WIDTH, HEIGHT

GREEN = (85, 239, 120)
GOLD = (224, 198, 106)
DARK = (8, 19, 13)


class LoadingScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_big = pygame.font.Font(None, 96)
        self.font_mid = pygame.font.Font(None, 36)
        self.font_sm = pygame.font.Font(None, 22)
        self.font_tiny = pygame.font.Font(None, 16)
        self.t = 0.0
        self.progress = 0.0
        self.ready = False
        self.play_rect = pygame.Rect(WIDTH // 2 - 130, HEIGHT // 2 + 90, 260, 64)
        self.play_hover = False
        self.stars = [(i * 73 % WIDTH, i * 131 % HEIGHT, (i % 3) + 1)
                      for i in range(90)]
        self.loading_steps = [
            "Initializing pygame...",
            "Growing the PlayTree...",
            "Loading worlds...",
            "Summoning creatures...",
            "Preparing combat...",
            "Connecting to servers...",
            "Restoring balance...",
        ]

    def update(self, dt):
        self.t += dt
        # progress to 100% over ~1.6s
        self.progress = min(1.0, self.t / 1.6)
        if self.progress >= 1.0:
            self.ready = True

    def handle_event(self, event):
        if not self.ready:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.play_hover = self.play_rect.collidepoint(
                self._map_pos(event.pos))
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.play_rect.collidepoint(self._map_pos(event.pos)):
                return True
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return True
        if event.type == pygame.FINGERDOWN:
            # Android: convert to display coords
            nx = event.x * WIDTH
            ny = event.y * HEIGHT
            if self.play_rect.collidepoint((nx, ny)):
                return True
        return False

    def _map_pos(self, pos):
        try:
            surf = pygame.display.get_surface()
            if surf:
                w, h = surf.get_size()
                if w and h and (w != WIDTH or h != HEIGHT):
                    return (int(pos[0] * WIDTH / w), int(pos[1] * HEIGHT / h))
        except Exception:
            pass
        return pos

    def draw(self):
        s = self.screen
        s.fill(DARK)
        # stars
        for x, y, sz in self.stars:
            a = int(90 + 120 * abs(math.sin(self.t + x)))
            pygame.draw.circle(s, (a, min(255, a + 40), a), (x, y), sz)

        # glow rings
        cx, cy = WIDTH // 2, HEIGHT // 2 - 60
        for r in range(170, 40, -18):
            a = int(8 + (170 - r) * 0.08)
            ring = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(ring, (*GREEN, a), (r, r), r, 2)
            s.blit(ring, (cx - r, cy - r))

        # pulsing tree emblem
        pulse = 1 + 0.03 * math.sin(self.t * 2)
        pygame.draw.rect(s, (58, 42, 26), (cx - 4, cy + 28, 8, 40))
        for dx, dy, rr in [(0, -12, 34), (-20, 2, 24), (20, 2, 24)]:
            r = int(rr * pulse)
            pygame.draw.circle(s, GREEN, (cx + dx, cy + dy - 8), r)
            pygame.draw.circle(s, (60, 200, 90), (cx + dx, cy + dy - 12), int(r * 0.6))

        # title
        title = self.font_big.render("PLAYTREE", True, GREEN)
        s.blit(title, (cx - title.get_width() // 2, cy + 90))
        tag = self.font_sm.render("AWAKEN  .  REBUILD  .  RESTORE BALANCE", True, GOLD)
        s.blit(tag, (cx - tag.get_width() // 2, cy + 196))

        if not self.ready:
            # progress bar
            bx, by, bw, bh = cx - 220, HEIGHT - 110, 440, 12
            pygame.draw.rect(s, (20, 40, 25), (bx, by, bw, bh), border_radius=6)
            pygame.draw.rect(s, GREEN, (bx, by, int(bw * self.progress), bh), border_radius=6)
            step = min(int(self.progress * len(self.loading_steps)), len(self.loading_steps) - 1)
            msg = self.font_tiny.render(self.loading_steps[step] + f"  {int(self.progress*100)}%", True, (120, 180, 130))
            s.blit(msg, (cx - msg.get_width() // 2, by + 20))
        else:
            # Play button
            hover = self.play_hover
            color = GREEN if hover else (40, 150, 70)
            pygame.draw.rect(s, color, self.play_rect, border_radius=12)
            pygame.draw.rect(s, GREEN, self.play_rect, 2, border_radius=12)
            label = self.font_mid.render("▶  PLAY", True, DARK if hover else GREEN)
            s.blit(label, label.get_rect(center=self.play_rect.center))
            hint = self.font_tiny.render("Press ENTER or click PLAY", True, (110, 150, 120))
            s.blit(hint, (cx - hint.get_width() // 2, self.play_rect.bottom + 14))

        # version footer
        ver = self.font_tiny.render("v1.3.0 - GoConsole Game Studios / GoStudios", True, (70, 95, 75))
        s.blit(ver, (WIDTH - ver.get_width() - 16, HEIGHT - 24))
