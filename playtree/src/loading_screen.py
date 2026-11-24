"""PLAYTREE cinematic loading screen.
Layout inspired by modern game splash screens:
- Huge PLAYTREE logo lower-left
- World scene art (forest/tree) on the right
- "WELCOME TO THE FOREST" heading + blurb + progress bar bottom-left
- Tip text bottom-right
- ▶ PLAY button when ready (desktop, web, Android)
"""
import pygame
import math
import random
from config import WIDTH, HEIGHT

GREEN = (85, 239, 120)
GOLD = (224, 198, 106)
DARK = (6, 14, 9)
PINK = (255, 110, 180)


class LoadingScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_logo = pygame.font.Font(None, 110)
        self.font_head = pygame.font.Font(None, 26)
        self.font_sm = pygame.font.Font(None, 18)
        self.font_tiny = pygame.font.Font(None, 14)
        self.t = 0.0
        self.progress = 0.0
        self.ready = False
        self.play_rect = pygame.Rect(WIDTH - 230, HEIGHT - 130, 170, 50)
        self.play_hover = False
        self.stars = [(i * 73 % WIDTH, i * 131 % (HEIGHT // 2), (i % 3) + 1)
                      for i in range(110)]
        self.particles = []
        for _ in range(60):
            self.particles.append((random.uniform(0, WIDTH), random.uniform(0, HEIGHT),
                                   random.uniform(10, 40), random.uniform(0.3, 1.2)))
        self.steps = [
            "Initializing pygame...", "Growing the PlayTree...", "Loading worlds...",
            "Summoning creatures...", "Preparing combat...", "Connecting to servers...",
            "Restoring balance...", "Ready!"
        ]
        self.tips = [
            "TIP: Press E near villagers to hear their stories.",
            "TIP: Chain kills quickly for combo XP multipliers!",
            "TIP: Press S in-game to open the DATA STORE.",
            "TIP: Press F9 to script in GoSD, PLAYTREE's language.",
            "TIP: Gather Tree Energy to tame wild creatures.",
        ]

    def update(self, dt):
        self.t += dt
        self.progress = min(1.0, self.t / 2.2)
        if self.progress >= 1.0:
            self.ready = True
        new_particles = []
        for x, y, sp, a in self.particles:
            py = y - sp * dt
            if py < -10:
                new_particles.append((x, HEIGHT + 10, sp, a))
            else:
                new_particles.append((x, py, sp, a))
        self.particles = new_particles

    def handle_event(self, event):
        if not self.ready:
            return False
        pos = self._map_pos(event.pos) if hasattr(event, 'pos') else None
        if event.type == pygame.MOUSEMOTION and pos:
            self.play_hover = self.play_rect.collidepoint(pos)
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and pos:
            if self.play_rect.collidepoint(pos):
                return True
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            return True
        if event.type == pygame.FINGERDOWN:
            nx, ny = event.x * WIDTH, event.y * HEIGHT
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
        # Sky gradient
        sky = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(HEIGHT):
            t = y / HEIGHT
            c = (int(30 + 20 * t), int(70 + 60 * (1 - t)), int(60 + 40 * t))
            pygame.draw.line(sky, (*c, 255), (0, y), (WIDTH, y))
        s.blit(sky, (0, 0))
        # Sun glow
        glow = pygame.Surface((500, 500), pygame.SRCALPHA)
        for r in range(240, 0, -12):
            a = int(4 + (240 - r) * 0.12)
            pygame.draw.circle(glow, (255, 220, 150, a), (250, 250), r)
        s.blit(glow, (WIDTH * 0.62 - 250, HEIGHT * 0.25 - 250))
        # Stars
        for x, y, sz in self.stars:
            a = int(70 + 100 * abs(math.sin(self.t + x)))
            pygame.draw.circle(s, (a, a, a), (x, y), sz)
        # Floating motes
        for x, y, sp, a in self.particles:
            aa = min(1.0, max(0.0, a))
            pygame.draw.circle(s, (int(GREEN[0] * aa), int(GREEN[1] * aa), int(GREEN[2] * aa)),
                               (int(x), int(y)), 2)
        # Far mountains / islands
        for i in range(6):
            mx = i * 260 - 40
            pygame.draw.ellipse(s, (25, 55, 35), (mx, HEIGHT * 0.52, 280, 120))
        # Water
        water = pygame.Surface((WIDTH, HEIGHT * 0.42), pygame.SRCALPHA)
        for y in range(int(HEIGHT * 0.42)):
            t = y / (HEIGHT * 0.42)
            pygame.draw.line(water, (int(20 + 10*t), int(80 + 40*t), int(70 + 30*t), 200),
                             (0, y), (WIDTH, y))
        s.blit(water, (0, HEIGHT * 0.58))
        # reflection shimmer
        for i in range(30):
            rx = random.randint(0, WIDTH)
            ry = HEIGHT * 0.6 + (i * 7) % int(HEIGHT * 0.35)
            pygame.draw.line(s, (120, 200, 140, 40), (rx, ry), (rx + 30, ry), 1)

        # Big tree on the right (hero art)
        tx, ty = int(WIDTH * 0.72), int(HEIGHT * 0.58)
        pygame.draw.rect(s, (50, 35, 22), (tx - 22, ty, 44, 150))
        for dx, dy, rr in [(0, -40, 95), (-70, 10, 65), (70, 10, 65), (-35, -80, 55), (35, -85, 55)]:
            pulse = 1 + 0.02 * math.sin(self.t * 1.5 + dx)
            r = int(rr * pulse)
            pygame.draw.circle(s, (35, 110, 55), (tx + dx, ty + dy), r)
            pygame.draw.circle(s, (55, 160, 75), (tx + dx, ty + dy - 8), int(r * 0.7))
            pygame.draw.circle(s, GREEN, (tx + dx - 10, ty + dy - 18), int(r * 0.35))
        # quest marker above tree
        qy = ty - 150 + math.sin(self.t * 3) * 5
        pygame.draw.polygon(s, GOLD, [(tx, qy), (tx - 7, qy - 12), (tx + 7, qy - 12)])

        # Dark gradient at bottom for text readability
        shade = pygame.Surface((WIDTH, 220), pygame.SRCALPHA)
        for y in range(220):
            pygame.draw.line(shade, (0, 0, 0, int(200 * (1 - y / 220))), (0, y), (WIDTH, y))
        s.blit(shade, (0, HEIGHT - 220))

        # Left side: WELCOME text
        head = self.font_head.render("WELCOME TO THE FOREST", True, GOLD)
        s.blit(head, (40, HEIGHT - 190))
        blurb = self.font_sm.render("Sunshine. Corruption. Rebirth.", True, (200, 220, 200))
        s.blit(blurb, (40, HEIGHT - 160))
        blurb2 = self.font_sm.render("The PlayTree once connected all lands. Restore its cores.", True, (170, 200, 175))
        s.blit(blurb2, (40, HEIGHT - 140))
        blurb3 = self.font_sm.render("It is up to you to take it back.", True, (170, 200, 175))
        s.blit(blurb3, (40, HEIGHT - 120))

        # Logo lower-left (big, two lines like GTA VI)
        l1 = self.font_logo.render("PLAY", True, GREEN)
        l2 = self.font_logo.render("TREE", True, GREEN)
        s.blit(l1, (30, HEIGHT - 360))
        s.blit(l2, (30, HEIGHT - 270))

        # Loading bar bottom-left
        bx, by, bw, bh = 40, HEIGHT - 42, 520, 8
        pygame.draw.rect(s, (60, 60, 60), (bx, by, bw, bh), border_radius=4)
        pygame.draw.rect(s, PINK, (bx, by, int(bw * self.progress), bh), border_radius=4)
        step = min(int(self.progress * len(self.steps)), len(self.steps) - 1)
        msg = self.font_tiny.render(self.steps[step] + f"  {int(self.progress*100)}%", True, (200, 200, 200))
        s.blit(msg, (bx, by - 18))

        # Tip bottom-right
        tip = self.font_tiny.render(self.tips[int(self.t) // 4 % len(self.tips)], True, (200, 200, 200))
        s.blit(tip, (WIDTH - tip.get_width() - 40, HEIGHT - 44))
        hint = self.font_tiny.render("Opportunities don't always come marked on a map.", True, (140, 140, 140))
        s.blit(hint, (WIDTH - hint.get_width() - 40, HEIGHT - 28))

        # PLAY button
        if self.ready:
            color = GREEN if self.play_hover else (45, 150, 75)
            pygame.draw.rect(s, color, self.play_rect, border_radius=8)
            pygame.draw.rect(s, GREEN, self.play_rect, 2, border_radius=8)
            label = self.font_head.render("▶  PLAY", True, DARK if self.play_hover else GREEN)
            s.blit(label, label.get_rect(center=self.play_rect.center))
