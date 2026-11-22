"""In-game Community Hub: Redeem, Profile, Store, Servers, Minigames.
Accessible from the main menu. ESC to go back.
"""
import pygame
import os
from config import WIDTH, HEIGHT, GameState


class CommunityHub:
    def __init__(self, game):
        self.game = game
        self.open = False
        self.screen = "hub"  # hub | redeem | profile | store | servers | minigames
        self.input_text = ""
        self.message = ""
        self.message_timer = 0
        self.font = pygame.font.Font(None, 28)
        self.small = pygame.font.Font(None, 18)
        self.tiny = pygame.font.Font(None, 14)
        self.buttons = []
        self._build_hub_buttons()

    def _build_hub_buttons(self):
        cx = WIDTH // 2
        start_y = 160
        gap = 60
        labels = ["Redeem Code", "Profile", "Store (Tree Points/Coins)", "Servers", "Minigames", "Play on TV", "Follow on X", "Join Discord", "Back"]
        self.hub_buttons = []
        for i, lbl in enumerate(labels):
            r = pygame.Rect(cx - 200, start_y + i * gap, 400, 50)
            self.hub_buttons.append((lbl, r))

    def handle_event(self, event):
        if not self.open:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.screen == "hub":
                    self.open = False
                    self.game.state = self.game._prev_state if hasattr(self.game, "_prev_state") else (self.game.state)
                else:
                    self.screen = "hub"
                return True
            if self.screen == "redeem" and event.key == pygame.K_RETURN:
                self._redeem(self.input_text.strip())
                self.input_text = ""
                return True
            if self.screen == "redeem" and event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
                return True
            if self.screen == "tv" and event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
                return True
            if self.screen == "tv" and event.key == pygame.K_RETURN:
                import webbrowser
                webbrowser.open("https://gostudios-real.github.io/PlayTree-Website/connect.html")
                self.message = "Opened connect page in browser"
                return True
            if self.screen == "tv" and event.unicode and len(event.unicode) == 1 and event.unicode.isdigit():
                if len(self.input_text) < 6:
                    self.input_text += event.unicode
                return True
            if self.screen == "redeem" and event.unicode and len(event.unicode) == 1 and event.unicode.isprintable():
                self.input_text += event.unicode
                return True
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.screen == "hub":
                for lbl, r in self.hub_buttons:
                    if r.collidepoint(pos):
                        if lbl == "Back":
                            self.open = False
                            self.game.state = GameState.MAIN_MENU if False else self.game.state
                        elif lbl == "Redeem Code":
                            self.screen = "redeem"; self.input_text = ""; self.message = ""
                        elif lbl == "Profile":
                            self.screen = "profile"
                        elif lbl == "Store (Tree Points/Coins)":
                            self.screen = "store"
                        elif lbl == "Servers":
                            self.screen = "servers"
                        elif lbl == "Minigames":
                            self.screen = "minigames"
                        elif lbl == "Play on TV":
                            self.screen = "tv"
                        elif lbl == "Follow on X":
                            import webbrowser
                            webbrowser.open("https://x.com/PlayTreeReal")
                            self.message = "Opening @PlayTreeReal on X"
                        elif lbl == "Join Discord":
                            import webbrowser
                            webbrowser.open("https://discord.com/users/1451398119110738147")
                            self.message = "Opening PLAYTREE on Discord"
                        return True
            # back button on sub-screens
            back_r = pygame.Rect(40, HEIGHT - 70, 120, 40)
            if back_r.collidepoint(pos) and self.screen != "hub":
                self.screen = "hub"
                return True
            # store buy buttons
            if self.screen == "store":
                self._handle_store_click(pos)
            # servers join
            if self.screen == "servers":
                self._handle_server_click(pos)
            # minigames play
            if self.screen == "minigames":
                self._handle_minigame_click(pos)
            return True
        return True

    def _redeem(self, code):
        if not code:
            self.message = "Enter a code first."
            return
        # Demo redeem logic
        import random
        rewards = {"PLAYTREE": (500, "Tree Points"), "GOSTUDIOS": (1000, "Tree Coins"), "WELCOME": (200, "Tree Points")}
        if code.upper() in rewards:
            amt, kind = rewards[code.upper()]
            if kind == "Tree Points":
                self.game.currency.tree_points += amt
            else:
                self.game.currency.tree_coins += amt
            self.game.currency.save()
            self.message = f"Redeemed {code}: +{amt} {kind}!"
        else:
            self.message = f"Invalid code: {code}"

    def _handle_store_click(self, pos):
        # Simple: clicking anywhere on a card buys the first pack
        packs = [(500, 4.99, True), (1000, 2.99, False)]
        for i, (amt, price, is_pts) in enumerate(packs):
            r = pygame.Rect(100 + i * 320, 260, 280, 140)
            if r.collidepoint(pos):
                if is_pts:
                    self.game.currency.tree_points += amt
                else:
                    self.game.currency.tree_coins += amt
                self.game.currency.save()
                self.message = f"Purchased {amt} {'Tree Points' if is_pts else 'Tree Coins'} (Demo)"
                return

    def _handle_server_click(self, pos):
        self.message = "Server browser coming soon. Multiplayer via src/multiplayer.py"

    def _handle_minigame_click(self, pos):
        self.message = "Launching fishing minigame..."
        try:
            from src.fishing import FishingMinigame
            self.game.fishing = FishingMinigame(self.game.player, self.game.audio)
            self.game.state = GameState.PLAYING
            self.open = False
        except Exception as e:
            self.message = f"Minigame error: {e}"

    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt

    def draw(self, screen):
        if not self.open:
            return
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        if self.screen == "hub":
            self._draw_hub(screen)
        elif self.screen == "redeem":
            self._draw_redeem(screen)
        elif self.screen == "profile":
            self._draw_profile(screen)
        elif self.screen == "store":
            self._draw_store(screen)
        elif self.screen == "servers":
            self._draw_servers(screen)
        elif self.screen == "minigames":
            self._draw_minigames(screen)
        elif self.screen == "tv":
            self._draw_tv(screen)

    def _draw_hub(self, screen):
        title = self.font.render("COMMUNITY HUB", True, (80, 255, 120))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 120)))
        for lbl, r in self.hub_buttons:
            pygame.draw.rect(screen, (20, 40, 25), r, border_radius=10)
            pygame.draw.rect(screen, (80, 255, 120), r, 2, border_radius=10)
            t = self.small.render(lbl, True, (200, 255, 200))
            screen.blit(t, t.get_rect(center=r.center))

    def _draw_redeem(self, screen):
        title = self.font.render("REDEEM CODE", True, (80, 255, 120))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 120)))
        # input box
        box = pygame.Rect(WIDTH // 2 - 200, 220, 400, 40)
        pygame.draw.rect(screen, (10, 20, 12), box)
        pygame.draw.rect(screen, (80, 255, 120), box, 2)
        t = self.font.render(self.input_text + "_", True, (200, 255, 200))
        screen.blit(t, (box.x + 10, box.y + 8))
        hint = self.small.render("Type a code and press Enter. Try: PLAYTREE, GOSTUDIOS, WELCOME", True, (150, 180, 150))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 290)))
        if self.message:
            m = self.small.render(self.message, True, (255, 200, 100))
            screen.blit(m, m.get_rect(center=(WIDTH // 2, 340)))
        back = pygame.Rect(40, HEIGHT - 70, 120, 40)
        pygame.draw.rect(screen, (40, 40, 40), back, border_radius=6)
        bt = self.small.render("Back", True, (200, 200, 200))
        screen.blit(bt, bt.get_rect(center=back.center))

    def _draw_profile(self, screen):
        title = self.font.render("PROFILE", True, (80, 255, 120))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 120)))
        user = getattr(self.game.account, "current_user", None)
        name = user.get("username", "Guest") if isinstance(user, dict) else "Guest"
        info = [f"Username: {name}", f"Tree Points: {self.game.currency.tree_points}", f"Tree Coins: {self.game.currency.tree_coins}"]
        y = 200
        for line in info:
            t = self.small.render(line, True, (200, 255, 200))
            screen.blit(t, (WIDTH // 2 - 150, y))
            y += 30
        back = pygame.Rect(40, HEIGHT - 70, 120, 40)
        pygame.draw.rect(screen, (40, 40, 40), back, border_radius=6)
        bt = self.small.render("Back", True, (200, 200, 200))
        screen.blit(bt, bt.get_rect(center=back.center))

    def _draw_store(self, screen):
        title = self.font.render("STORE - TREE POINTS & COINS", True, (80, 255, 120))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 120)))
        bal = self.small.render(f"Tree Points: {self.game.currency.tree_points}  |  Tree Coins: {self.game.currency.tree_coins}", True, (230, 200, 100))
        screen.blit(bal, bal.get_rect(center=(WIDTH // 2, 170)))
        packs = [(500, 4.99, True), (1000, 2.99, False)]
        for i, (amt, price, is_pts) in enumerate(packs):
            r = pygame.Rect(100 + i * 320, 220, 280, 120)
            pygame.draw.rect(screen, (20, 40, 25), r, border_radius=10)
            pygame.draw.rect(screen, (80, 255, 120), r, 2, border_radius=10)
            lbl = self.small.render(f"{'Tree Points' if is_pts else 'Tree Coins'} x{amt}", True, (200, 255, 200))
            screen.blit(lbl, (r.x + 20, r.y + 20))
            pr = self.small.render(f"${price}", True, (230, 200, 100))
            screen.blit(pr, (r.x + 20, r.y + 50))
            buy = self.tiny.render("Click card to buy (Demo)", True, (150, 180, 150))
            screen.blit(buy, (r.x + 20, r.y + 85))
        if self.message:
            m = self.small.render(self.message, True, (255, 200, 100))
            screen.blit(m, m.get_rect(center=(WIDTH // 2, 380)))
        back = pygame.Rect(40, HEIGHT - 70, 120, 40)
        pygame.draw.rect(screen, (40, 40, 40), back, border_radius=6)
        bt = self.small.render("Back", True, (200, 200, 200))
        screen.blit(bt, bt.get_rect(center=back.center))

    def _draw_servers(self, screen):
        title = self.font.render("SERVERS", True, (80, 255, 120))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 120)))
        info = self.small.render("Multiplayer servers via src/multiplayer.py", True, (200, 255, 200))
        screen.blit(info, info.get_rect(center=(WIDTH // 2, 200)))
        note = self.tiny.render("Host/Join a server from the main menu multiplayer option.", True, (150, 180, 150))
        screen.blit(note, note.get_rect(center=(WIDTH // 2, 240)))
        if self.message:
            m = self.small.render(self.message, True, (255, 200, 100))
            screen.blit(m, m.get_rect(center=(WIDTH // 2, 300)))
        back = pygame.Rect(40, HEIGHT - 70, 120, 40)
        pygame.draw.rect(screen, (40, 40, 40), back, border_radius=6)
        bt = self.small.render("Back", True, (200, 200, 200))
        screen.blit(bt, bt.get_rect(center=back.center))

    def _draw_tv(self, screen):
        title = self.font.render("PLAY ON TV", True, (80, 255, 120))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 120)))
        info = self.small.render("Enter the 6-digit code from your PLAYTREE TV app", True, (200, 255, 200))
        screen.blit(info, info.get_rect(center=(WIDTH // 2, 180)))
        # code input
        box = pygame.Rect(WIDTH // 2 - 150, 220, 300, 40)
        pygame.draw.rect(screen, (10, 20, 12), box)
        pygame.draw.rect(screen, (80, 255, 120), box, 2)
        t = self.font.render(self.input_text + "_", True, (200, 255, 200))
        screen.blit(t, (box.x + 10, box.y + 8))
        hint = self.tiny.render("Type the code shown on your TV, then press Enter", True, (150, 180, 150))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 280)))
        btn = pygame.Rect(WIDTH // 2 - 100, 310, 200, 40)
        pygame.draw.rect(screen, (40, 80, 50), btn, border_radius=6)
        bt = self.small.render("Open Connect Page", True, (200, 255, 200))
        screen.blit(bt, bt.get_rect(center=btn.center))
        if self.message:
            m = self.small.render(self.message, True, (255, 200, 100))
            screen.blit(m, m.get_rect(center=(WIDTH // 2, 370)))
        note = self.tiny.render("Or visit gostudios-real.github.io/PlayTree-Website/connect.html", True, (120, 140, 120))
        screen.blit(note, note.get_rect(center=(WIDTH // 2, 420)))
        back = pygame.Rect(40, HEIGHT - 70, 120, 40)
        pygame.draw.rect(screen, (40, 40, 40), back, border_radius=6)
        bbt = self.small.render("Back", True, (200, 200, 200))
        screen.blit(bbt, bbt.get_rect(center=back.center))

    def _draw_minigames(self, screen):
        title = self.font.render("MINIGAMES", True, (80, 255, 120))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 120)))
        info = self.small.render("Available: Fishing (click card to launch)", True, (200, 255, 200))
        screen.blit(info, info.get_rect(center=(WIDTH // 2, 200)))
        card = pygame.Rect(WIDTH // 2 - 140, 240, 280, 100)
        pygame.draw.rect(screen, (20, 40, 25), card, border_radius=10)
        pygame.draw.rect(screen, (80, 255, 120), card, 2, border_radius=10)
        t = self.small.render("Fishing Minigame", True, (200, 255, 200))
        screen.blit(t, t.get_rect(center=card.center))
        if self.message:
            m = self.small.render(self.message, True, (255, 200, 100))
            screen.blit(m, m.get_rect(center=(WIDTH // 2, 380)))
        back = pygame.Rect(40, HEIGHT - 70, 120, 40)
        pygame.draw.rect(screen, (40, 40, 40), back, border_radius=6)
        bt = self.small.render("Back", True, (200, 200, 200))
        screen.blit(bt, bt.get_rect(center=back.center))
""