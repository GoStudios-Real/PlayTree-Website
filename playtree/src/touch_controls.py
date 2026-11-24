import pygame
import math
import sys
import os
from config import WIDTH, HEIGHT

IS_MOBILE = sys.platform in ("android", "ios") or hasattr(sys, "getandroidapilevel")


def haptic_feedback(duration_ms=50):
    """Trigger haptic feedback on mobile devices (Android/iOS)."""
    if IS_MOBILE:
        try:
            # Android
            import android
            android.vibrator.vibrate(duration_ms / 1000.0)
        except Exception:
            try:
                # Alternative Android path
                import jnius
                from jnius import autoclass
                Vibrator = autoclass('android.os.Vibrator')
                Context = autoclass('android.content.Context')
                # This requires a valid context; best-effort
            except Exception:
                pass
    # Desktop: no-op (no haptic hardware typically)


def detect_touchscreen():
    """Return True when a touch digitizer / virtual touchpad is available.

    Works on Android/iOS, Windows touch devices (laptops, tablets, AIO PCs)
    and can be forced on any platform with the PLAYTREE_TOUCH=1 env var.
    """
    if IS_MOBILE:
        return True

    # Manual override: PLAYTREE_TOUCH=1 / 0
    env = os.environ.get("PLAYTREE_TOUCH", "").strip().lower()
    if env in ("1", "true", "yes", "on"):
        return True
    if env in ("0", "false", "no", "off"):
        return False

    # Windows: SM_MAXIMUMTOUCHES (95) reports the number of simultaneous
    # touch contacts. > 0 means a touch digitizer is present.
    if sys.platform.startswith("win"):
        try:
            import ctypes
            if ctypes.windll.user32.GetSystemMetrics(95) > 0:
                return True
        except Exception:
            pass

    # SDL2 can report touch devices directly.
    try:
        num_touch = pygame.display.get_num_touch_devices() if hasattr(pygame.display, "get_num_touch_devices") else 0
        if num_touch > 0:
            return True
    except Exception:
        pass

    # Linux: look for touch/tablet entries in the input device list.
    if sys.platform.startswith("linux"):
        try:
            with open("/proc/bus/input/devices", "r") as f:
                content = f.read().lower()
            if "touch" in content or "tablet" in content:
                return True
        except Exception:
            pass

    return False


def display_to_game(pos):
    """Map a window-space point to the 1280x720 game render surface."""
    try:
        surf = pygame.display.get_surface()
        if surf:
            w, h = surf.get_size()
            if w and h and (w != WIDTH or h != HEIGHT):
                return (int(pos[0] * WIDTH / w), int(pos[1] * HEIGHT / h))
    except Exception:
        pass
    return pos

class VirtualJoystick:
    def __init__(self, x, y, radius=60):
        self.base_x = x
        self.base_y = y
        self.radius = radius
        self.knob_x = x
        self.knob_y = y
        self.active = False
        self.finger_id = None
        self.dx = 0.0
        self.dy = 0.0

    def handle_event(self, event):
        if event.type == pygame.FINGERDOWN:
            fx = event.x * WIDTH
            fy = event.y * HEIGHT
            dist = math.hypot(fx - self.base_x, fy - self.base_y)
            if dist < self.radius * 1.7:
                self.active = True
                self.finger_id = event.finger_id
                self._update(fx, fy)
                return True
        elif event.type == pygame.FINGERUP:
            if event.finger_id == self.finger_id:
                self.active = False
                self.finger_id = None
                self.knob_x = self.base_x
                self.knob_y = self.base_y
                self.dx = 0.0
                self.dy = 0.0
                return True
        elif event.type == pygame.FINGERMOTION:
            if event.finger_id == self.finger_id:
                fx = event.x * WIDTH
                fy = event.y * HEIGHT
                self._update(fx, fy)
                return True
        # Mouse fallback (touchscreens reported as pointer devices)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            fx, fy = display_to_game(event.pos)
            if math.hypot(fx - self.base_x, fy - self.base_y) < self.radius * 1.7:
                self.active = True
                self.finger_id = "mouse"
                self._update(fx, fy)
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.finger_id == "mouse":
                self.active = False
                self.finger_id = None
                self.knob_x = self.base_x
                self.knob_y = self.base_y
                self.dx = 0.0
                self.dy = 0.0
                return True
        elif event.type == pygame.MOUSEMOTION:
            if self.finger_id == "mouse":
                self._update(*display_to_game(event.pos))
                return True
        return False

    def _update(self, fx, fy):
        dx = fx - self.base_x
        dy = fy - self.base_y
        dist = math.hypot(dx, dy)
        if dist > self.radius:
            dx = dx / dist * self.radius
            dy = dy / dist * self.radius
            dist = self.radius
        self.knob_x = self.base_x + dx
        self.knob_y = self.base_y + dy
        self.dx = dx / self.radius if self.radius > 0 else 0
        self.dy = dy / self.radius if self.radius > 0 else 0

    def draw(self, surface):
        alpha_surface = pygame.Surface((self.radius * 2 + 20, self.radius * 2 + 20), pygame.SRCALPHA)
        cx = self.radius + 10
        cy = self.radius + 10
        pygame.draw.circle(alpha_surface, (80, 255, 120, 40), (cx, cy), self.radius)
        pygame.draw.circle(alpha_surface, (80, 255, 120, 80), (cx, cy), self.radius, 2)
        knob_dx = self.knob_x - self.base_x
        knob_dy = self.knob_y - self.base_y
        pygame.draw.circle(alpha_surface, (80, 255, 120, 150), (int(cx + knob_dx), int(cy + knob_dy)), 22)
        pygame.draw.circle(alpha_surface, (80, 255, 120, 200), (int(cx + knob_dx), int(cy + knob_dy)), 22, 2)
        surface.blit(alpha_surface, (self.base_x - cx, self.base_y - cy))


class TouchButton:
    def __init__(self, x, y, radius, label, color=(80, 255, 120)):
        self.x = x
        self.y = y
        self.radius = radius
        self.label = label
        self.color = color
        self.pressed = False
        self.finger_id = None
        self.press_time = 0
        self._was_pressed = False
        self._cooldown = 0

    def handle_event(self, event):
        if event.type == pygame.FINGERDOWN:
            fx = event.x * WIDTH
            fy = event.y * HEIGHT
            dist = math.hypot(fx - self.x, fy - self.y)
            if dist < self.radius * 1.4:
                self.pressed = True
                self.finger_id = event.finger_id
                self.press_time = pygame.time.get_ticks()
                return True
        elif event.type == pygame.FINGERUP:
            if event.finger_id == self.finger_id:
                self.pressed = False
                self.finger_id = None
                return True
        # Mouse fallback
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            fx, fy = display_to_game(event.pos)
            if math.hypot(fx - self.x, fy - self.y) < self.radius * 1.4:
                self.pressed = True
                self.finger_id = "mouse"
                self.press_time = pygame.time.get_ticks()
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.finger_id == "mouse":
                self.pressed = False
                self.finger_id = None
                return True
        return False

    def just_pressed(self):
        now = self.pressed
        was = self._was_pressed
        self._was_pressed = now
        return now and not was

    def is_pressed(self):
        return self.pressed

    def draw(self, surface):
        alpha_surface = pygame.Surface((self.radius * 2 + 4, self.radius * 2 + 4), pygame.SRCALPHA)
        cx = self.radius + 2
        cy = self.radius + 2
        bg_alpha = 100 if self.pressed else 50
        border_alpha = 200 if self.pressed else 100
        bg_color = (*self.color[:3], bg_alpha)
        border_color = (*self.color[:3], border_alpha)
        pygame.draw.circle(alpha_surface, bg_color, (cx, cy), self.radius)
        pygame.draw.circle(alpha_surface, border_color, (cx, cy), self.radius, 2)
        font = pygame.font.Font(None, 24)
        txt = font.render(self.label, True, self.color)
        txt_rect = txt.get_rect(center=(cx, cy))
        alpha_surface.blit(txt, txt_rect)
        surface.blit(alpha_surface, (self.x - cx, self.y - cy))


class TouchControls:
    def __init__(self, screen_w=WIDTH, screen_h=HEIGHT, enabled=None):
        self.screen_w = screen_w
        self.screen_h = screen_h
        margin = 30
        btn_r = 28
        spacing = 70

        self.joystick = VirtualJoystick(margin + 90, screen_h - margin - 60, radius=50)

        attack_x = screen_w - margin - 50
        attack_y = screen_h - margin - 160
        self.attack_btn = TouchButton(attack_x, attack_y, btn_r, "ATK", (255, 80, 80))

        dodge_x = screen_w - margin - 50 - spacing
        dodge_y = screen_h - margin - 100
        self.dodge_btn = TouchButton(dodge_x, dodge_y, btn_r, "DGE", (80, 180, 255))

        special_x = screen_w - margin - 50
        special_y = screen_h - margin - 80
        self.special_btn = TouchButton(special_x, special_y, btn_r, "SPL", (255, 200, 50))

        interact_x = screen_w - margin - 50 - spacing
        interact_y = screen_h - margin - 170
        self.interact_btn = TouchButton(interact_x, interact_y, btn_r * 0.8, "ACT", (100, 255, 180))

        potion_x = screen_w - margin - 50 - spacing * 2
        potion_y = screen_h - margin - 130
        self.potion_btn = TouchButton(potion_x, potion_y, btn_r * 0.7, "POT", (60, 200, 60))

        # Menu buttons moved to TOP-CENTER (top-left is occupied by HUD bars/skills/weapon)
        inv_x = screen_w // 2 - spacing - 20
        inv_y = margin + 30
        self.inventory_btn = TouchButton(inv_x, inv_y, btn_r * 0.7, "INV", (200, 180, 100))

        craft_x = screen_w // 2 + spacing + 20
        craft_y = margin + 30
        self.craft_btn = TouchButton(craft_x, craft_y, btn_r * 0.7, "CRF", (180, 140, 80))

        mount_x = screen_w // 2 - 20
        mount_y = margin + 30
        self.mount_btn = TouchButton(mount_x, mount_y, btn_r * 0.6, "MNT", (150, 200, 255))

        self.all_buttons = [self.attack_btn, self.dodge_btn, self.special_btn,
                           self.interact_btn, self.potion_btn, self.inventory_btn,
                           self.craft_btn, self.mount_btn]

        self.menu_btn = TouchButton(screen_w - margin - 50, margin + 230, btn_r * 0.6, "|||", (200, 200, 200))

        self.enabled = detect_touchscreen() if enabled is None else enabled

    def set_enabled(self, enabled):
        self.enabled = enabled

    def handle_event(self, event):
        if not self.enabled:
            return False
        if self.joystick.handle_event(event):
            return True
        if self.menu_btn.handle_event(event):
            return True
        for btn in self.all_buttons:
            if btn.handle_event(event):
                return True
        return False

    def hit_test(self, gx, gy):
        """True if game-space point (gx, gy) is over an on-screen control."""
        if not self.enabled:
            return False
        if math.hypot(gx - self.joystick.base_x, gy - self.joystick.base_y) < self.joystick.radius * 1.7:
            return True
        if math.hypot(gx - self.menu_btn.x, gy - self.menu_btn.y) < self.menu_btn.radius * 1.4:
            return True
        for btn in self.all_buttons:
            if math.hypot(gx - btn.x, gy - btn.y) < btn.radius * 1.4:
                return True
        return False

    def draw(self, surface):
        if not self.enabled:
            return
        self.joystick.draw(surface)
        self.menu_btn.draw(surface)
        for btn in self.all_buttons:
            btn.draw(surface)

    def get_movement(self):
        return self.joystick.dx, self.joystick.dy


def detect_mobile():
    if sys.platform in ("android", "ios"):
        return True
    if hasattr(sys, "getandroidapilevel"):
        return True
    try:
        import os
        if os.path.exists("/system/build.prop"):
            return True
    except Exception:
        pass
    return False
