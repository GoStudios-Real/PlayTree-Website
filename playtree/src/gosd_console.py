"""In-game GoSD scripting console for PLAYTREE.

Press F9 in-game to open. Write GoSD code, run it, see output.
Scripts are saved to scripts/ folder as .gosd files.
"""
import pygame
import os
from config import WIDTH, HEIGHT
from src.gosd import run_source, check_source

SCRIPTS_DIR = "scripts"


class GoSDConsole:
    def __init__(self):
        self.open = False
        self.code = ""
        self.output_lines = []
        self.input_focus = True
        self.error = ""
        self.scroll = 0
        self.font = pygame.font.Font(None, 18)
        self.small = pygame.font.Font(None, 14)
        if not os.path.exists(SCRIPTS_DIR):
            try:
                os.makedirs(SCRIPTS_DIR)
            except Exception:
                pass
        self.example = '''# GoSD - PLAYTREE scripting\nfn fib(n) {\n    if n <= 1 { return n }\n    return fib(n-1) + fib(n-2)\n}\nfor i in range(0, 8) {\n    print "fib(" + str(i) + ") = " + str(fib(i))\n}'''

    def capture(self, text):
        self.output_lines.append(str(text))
        if len(self.output_lines) > 200:
            self.output_lines = self.output_lines[-200:]

    def run(self):
        self.output_lines = []
        self.error = ""
        try:
            run_source(self.code, output=self.capture)
        except Exception as e:
            self.error = f"{type(e).__name__}: {e}"
            self.output_lines.append(self.error)

    def check(self):
        try:
            check_source(self.code)
            self.error = "Syntax OK"
        except Exception as e:
            self.error = f"{type(e).__name__}: {e}"

    def save(self, name="script.gosd"):
        try:
            path = os.path.join(SCRIPTS_DIR, name)
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.code)
            self.error = "Saved " + path
        except Exception as e:
            self.error = "Save failed: " + str(e)

    def handle_event(self, event):
        if not self.open:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F9:
                self.open = True
                if not self.code:
                    self.code = self.example
                return True
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F9 or event.key == pygame.K_ESCAPE:
                self.open = False
                return True
            if event.key == pygame.K_F5:
                self.run()
                return True
            if event.key == pygame.K_F6:
                self.check()
                return True
            if event.key == pygame.K_F2:
                self.save()
                return True
            if event.key == pygame.K_BACKSPACE:
                self.code = self.code[:-1]
                return True
            if event.key == pygame.K_RETURN:
                self.code += "\n"
                return True
            if event.key == pygame.K_TAB:
                self.code += "    "
                return True
            if event.unicode and len(event.unicode) == 1:
                self.code += event.unicode
                return True
            return True
        return False

    def draw(self, screen):
        if not self.open:
            return
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))

        panel = pygame.Rect(60, 40, WIDTH - 120, HEIGHT - 80)
        pygame.draw.rect(screen, (10, 20, 12), panel, border_radius=8)
        pygame.draw.rect(screen, (80, 255, 120), panel, 2, border_radius=8)

        title = self.font.render("GoSD CONSOLE - PLAYTREE Scripting", True, (80, 255, 120))
        screen.blit(title, (panel.x + 16, panel.y + 12))
        hint = self.small.render("F5 Run  |  F6 Check  |  F2 Save  |  F9/ESC Close", True, (150, 180, 150))
        screen.blit(hint, (panel.x + 16, panel.y + 36))

        mid = panel.y + 60
        code_h = (panel.height - 90) // 2
        left_w = (panel.width - 30) // 2
        code_rect = pygame.Rect(panel.x + 12, mid, left_w, code_h)
        out_rect = pygame.Rect(panel.x + left_w + 18, mid, left_w, code_h)

        pygame.draw.rect(screen, (6, 12, 8), code_rect)
        pygame.draw.rect(screen, (6, 12, 8), out_rect)
        pygame.draw.rect(screen, (40, 80, 50), code_rect, 1)
        pygame.draw.rect(screen, (40, 80, 50), out_rect, 1)

        lbl1 = self.small.render("CODE (.gosd)", True, (200, 200, 100))
        lbl2 = self.small.render("OUTPUT", True, (200, 200, 100))
        screen.blit(lbl1, (code_rect.x + 6, code_rect.y + 4))
        screen.blit(lbl2, (out_rect.x + 6, out_rect.y + 4))

        y = code_rect.y + 24
        for line in self.code.split("\n")[-20:]:
            s = self.font.render(line, True, (200, 255, 200))
            screen.blit(s, (code_rect.x + 6, y))
            y += 20
            if y > code_rect.bottom - 20:
                break

        y = out_rect.y + 24
        for line in self.output_lines[-20:]:
            color = (255, 100, 100) if "Error" in line or "Traceback" in line else (180, 255, 180)
            s = self.font.render(line[:80], True, color)
            screen.blit(s, (out_rect.x + 6, y))
            y += 20
            if y > out_rect.bottom - 20:
                break

        if self.error:
            e = self.font.render(self.error[:90], True, (255, 200, 100))
            screen.blit(e, (panel.x + 16, panel.bottom - 30))
