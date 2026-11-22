"""Generate PLAYTREE X icon + social banner with PIL."""
from PIL import Image, ImageDraw, ImageFont
import os

ASSETS = os.path.dirname(os.path.abspath(__file__))
os.makedirs(ASSETS, exist_ok=True)

GREEN = (85, 239, 120)
GOLD = (224, 198, 106)
DARK = (8, 19, 13)

def font(size):
    p = r"C:\Windows\Fonts\arialbd.ttf"
    return ImageFont.truetype(p, size) if os.path.exists(p) else ImageFont.load_default()

# --- X icon (400x400) ---
icon = Image.new('RGBA', (400, 400), (8, 19, 13, 255))
d = ImageDraw.Draw(icon)
# green glow circle
for r in range(180, 120, -10):
    a = int(20 + (180-r)*0.6)
    d.ellipse((200-r, 200-r, 200+r, 200+r), outline=(*GREEN, a), width=6)
# Stylized tree
d.rectangle((188, 230, 212, 320), fill=(*GREEN, 255))  # trunk
for cx, cy, rr in [(200, 180, 70), (160, 200, 50), (240, 200, 50), (200, 140, 45)]:
    d.ellipse((cx-rr, cy-rr, cx+rr, cy+rr), fill=(*GREEN, 255))
# X mark top-right badge
d.ellipse((300, 300, 380, 380), fill=(0, 0, 0, 255))
f = font(44)
d.text((340, 340), "X", font=f, fill=(255,255,255,255), anchor='mm')
icon.save(os.path.join(ASSETS, 'x_icon.png'))

# --- Social banner (1200x630) for X cards ---
banner = Image.new('RGB', (1200, 630), DARK)
d = ImageDraw.Draw(banner)
# radial-ish glow rings
for r in range(500, 100, -40):
    a = int(8 + (500-r)*0.03)
    d.ellipse((600-r, 315-r, 600+r, 315+r), outline=GREEN, width=2)
# Title
f1 = font(110)
d.text((600, 230), "PLAYTREE", font=f1, fill=GREEN, anchor='mm')
# Tagline
f2 = font(44)
d.text((600, 330), "AWAKEN  .  REBUILD  .  RESTORE BALANCE", font=f2, fill=GOLD, anchor='mm')
# Handle
f3 = font(30)
d.text((600, 420), "x.com/PlayTreeReal   |   GoConsole Game Studios / GoStudios", font=f3, fill=(150, 200, 160), anchor='mm')
# download line
d.text((600, 500), "Download for Windows & Android - playtree.game", font=font(28), fill=(120, 160, 130), anchor='mm')
banner.save(os.path.join(ASSETS, 'banner_x.png'))

print("Created x_icon.png and banner_x.png in", ASSETS)
