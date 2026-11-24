"""PLAYTREE CROSSOVER - 2D blend of Minecraft/Roblox/Fortnite/GTA VI.
Systems:
- STORM ZONE (Fortnite): shrinking circle outside damages player
- BUILDING (Fortnite/Minecraft): place wall/ramp blocks instantly
- WANTED LEVEL (GTA): crimes raise stars, enemies spawn
- VEHICLES (GTA): rideable mount vehicles with speed boost
- MINING (Minecraft): mine resource nodes with pickaxe
- AVATAR (Roblox): cosmetic customization
- PICKUPS (Fortnite): weapon/health drops from sky
"""
import pygame
import math
import random
import time
from config import WIDTH, HEIGHT

GOLD = (255, 215, 80)
RED = (255, 80, 80)
GREEN = (85, 239, 120)


class Storm:
    """Fortnite-style shrinking safe zone."""
    def __init__(self, center_x, center_y, radius=800):
        self.cx = center_x
        self.cy = center_y
        self.radius = radius
        self.target = 200
        self.active = False
        self.phase = 0
        self.timer = 0
        self.damage_timer = 0

    def start(self):
        self.active = True
        self.timer = 0

    def update(self, dt, player):
        if not self.active:
            return 0
        self.timer += dt
        # shrink every 30s
        if self.timer > 30:
            self.timer = 0
            self.phase += 1
            self.radius = max(self.target, self.radius * 0.7)
            self.cx += random.randint(-100, 100)
            self.cy += random.randint(-100, 100)
        if player:
            dist = math.hypot(player.x - self.cx, player.y - self.cy)
            if dist > self.radius:
                self.damage_timer += dt
                if self.damage_timer >= 1:
                    self.damage_timer = 0
                    return 5 + self.phase * 2  # damage per second
        return 0

    def draw(self, screen, cam_x, cam_y):
        if not self.active:
            return
        sx, sy = int(self.cx - cam_x), int(self.cy - cam_y)
        r = int(self.radius)
        # danger outside
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((120, 20, 80, 60))
        pygame.draw.circle(overlay, (0, 0, 0, 0), (sx, sy), r)
        pygame.draw.circle(overlay, (180, 60, 200, 160), (sx, sy), r, 4)
        screen.blit(overlay, (0, 0))
        # zone label
        f = pygame.font.Font(None, 20)
        s = f.render(f"STORM PHASE {self.phase+1} — MOVE TO SAFE ZONE!", True, (255, 120, 220))
        screen.blit(s, (WIDTH // 2 - s.get_width() // 2, 30))


class BuildSystem:
    """Fortnite/Minecraft-style rapid building."""
    def __init__(self):
        self.blocks = []  # x, y, type, hp
        self.selected = "wall"
        self.types = {"wall": (20, 60, (150, 120, 80)),
                      "ramp": (40, 40, (120, 160, 100)),
                      "platform": (60, 15, (100, 140, 180))}

    def place(self, x, y, player):
        bw, bh, color = self.types[self.selected]
        # cost resources
        res = player.inventory.setdefault("resources", {})
        if res.get("Ancient Seeds", 0) < 1:
            return False
        res["Ancient Seeds"] -= 1
        self.blocks.append({"x": x - bw/2, "y": y - bh/2, "w": bw, "h": bh,
                            "type": self.selected, "hp": 100, "color": color})
        return True

    def update(self, dt, enemies):
        for b in self.blocks[:]:
            # buildings take damage from nearby enemies
            for e in enemies:
                if abs(e.x - b['x']) < b['w'] + 20 and abs(e.y - b['y']) < b['h'] + 20:
                    b['hp'] -= 5 * dt
            if b['hp'] <= 0:
                self.blocks.remove(b)

    def draw(self, screen, cam_x, cam_y):
        for b in self.blocks:
            x, y = int(b['x'] - cam_x), int(b['y'] - cam_y)
            pygame.draw.rect(screen, b['color'], (x, y, int(b['w']), int(b['h'])), border_radius=3)
            pygame.draw.rect(screen, (255, 255, 255, 60), (x, y, int(b['w']), int(b['h'])), 1)
            if b['hp'] < 100:
                pygame.draw.rect(screen, RED, (x, y - 6, int(b['w'] * b['hp'] / 100), 3))


class WantedSystem:
    """GTA-style wanted stars."""
    def __init__(self):
        self.level = 0
        self.cooldown = 0

    def add(self, amount=1):
        self.level = min(5, self.level + amount)
        self.cooldown = 8.0

    def update(self, dt):
        if self.cooldown > 0:
            self.cooldown -= dt
            if self.cooldown <= 0 and self.level > 0:
                self.level -= 1
                self.cooldown = 8.0

    def draw(self, screen):
        if self.level <= 0:
            return
        f = pygame.font.Font(None, 24)
        stars = "★" * self.level + "☆" * (5 - self.level)
        s = f.render("WANTED: " + stars, True, GOLD)
        screen.blit(s, (WIDTH // 2 - s.get_width() // 2, 10))


class MiningSystem:
    """Minecraft-style resource nodes."""
    NODES = ["crystal", "iron", "gold", "seed"]
    COLORS = {"crystal": (120, 200, 255), "iron": (180, 180, 190),
              "gold": (255, 200, 60), "seed": (100, 220, 120)}

    def __init__(self):
        self.nodes = []
        for _ in range(20):
            self.nodes.append({"x": random.randint(100, 2000), "y": random.randint(100, 2000),
                               "type": random.choice(self.NODES), "hp": 3})

    def mine(self, px, py, facing, player):
        fx, fy = px + math.cos(facing) * 40, py + math.sin(facing) * 40
        for n in self.nodes[:]:
            if math.hypot(n['x'] - fx, n['y'] - fy) < 45:
                n['hp'] -= 1
                if n['hp'] <= 0:
                    self.nodes.remove(n)
                    res = player.inventory.setdefault("resources", {})
                    key = {"crystal": "Crystal Dust", "iron": "Ancient Root",
                           "gold": "Gold Leaves", "seed": "Ancient Seeds"}[n['type']]
                    res[key] = res.get(key, 0) + 3
                    return f"+3 {key}"
                return f"Mining... {n['hp']} hits left"
        return None

    def draw(self, screen, cam_x, cam_y):
        for n in self.nodes:
            x, y = int(n['x'] - cam_x), int(n['y'] - cam_y)
            if -30 < x < WIDTH + 30 and -30 < y < HEIGHT + 30:
                c = self.COLORS[n['type']]
                pygame.draw.polygon(screen, c, [(x, y-12), (x-10, y+8), (x+10, y+8)])
                pygame.draw.ellipse(screen, (255,255,255,60), (x-4, y-4, 6, 6))


class PickupSystem:
    """Fortnite-style supply drops."""
    ITEMS = [("Med Kit", 50), ("Shield", 30), ("Weapon crate", 0), ("Tree Coins", 200)]

    def __init__(self):
        self.drops = []
        self.timer = 0

    def update(self, dt, player):
        self.timer += dt
        if self.timer > 20 and len(self.drops) < 5:
            self.timer = 0
            self.drops.append({"x": player.x + random.randint(-300, 300),
                               "y": player.y + random.randint(-300, 300),
                               "item": random.choice(self.ITEMS), "t": 0})
        for d in self.drops[:]:
            d['t'] += dt
            if math.hypot(d['x'] - player.x, d['y'] - player.y) < 40:
                name, val = d['item']
                if name == "Med Kit":
                    player.hp = min(player.max_hp, player.hp + val)
                elif name == "Shield":
                    player.energy = min(player.max_energy, player.energy + val)
                elif name == "Tree Coins":
                    pass  # currency handled by game
                self.drops.remove(d)
                return name
        return None

    def draw(self, screen, cam_x, cam_y):
        for d in self.drops:
            x, y = int(d['x'] - cam_x), int(d['y'] - cam_y)
            bob = math.sin(d['t'] * 3) * 6
            pygame.draw.rect(screen, (80, 200, 120, 180), (x-14, y-14+bob, 28, 28), border_radius=4)
            pygame.draw.rect(screen, GOLD, (x-14, y-14+bob, 28, 28), 2, border_radius=4)
            f = pygame.font.Font(None, 16)
            s = f.render(d['item'][0][:6], True, GOLD)
            screen.blit(s, (x - s.get_width()//2, y - 6 + bob))
