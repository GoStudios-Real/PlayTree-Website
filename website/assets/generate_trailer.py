"""Generate PLAYTREE trailer GIF from the trailer.html scene definitions.
Renders each scene as a stylized frame with PIL, then saves an animated GIF.
Output: website/assets/trailer.gif
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, random, os

random.seed(42)
OUT = os.path.join(os.path.dirname(__file__), 'trailer.gif')
W, H = 960, 540
GREEN = (85, 239, 120)
GOLD = (224, 198, 106)
DARK = (6, 14, 9)

def font(size, bold=True):
    p = r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"
    return ImageFont.truetype(p, size) if os.path.exists(p) else ImageFont.load_default()

# (seconds, title, subtitle, bg color)
SCENES = [
    (2.5, "THE FOREST AWAKENING", "The corruption spreads...", (10, 31, 10)),
    (2.5, "EPIC COMBAT", "5 Unique Classes", (26, 10, 31)),
    (2.5, "CRYSTAL DEPTHS", "A hydra stirs in the deep", (10, 26, 47)),
    (2.5, "BOSS FIGHTS", "Root Titan & Crystal Hydra", (47, 10, 10)),
    (2.5, "STORM PEAKS", "The Sky Guardian awaits", (10, 26, 47)),
    (2.0, "MULTIPLAYER", "Up to 8 players online", (26, 26, 10)),
    (2.0, "BASE BUILDING", "Construct your stronghold", (10, 31, 21)),
    (2.0, "CREATURE TAMING", "Hatch eggs & Evolve companions", (26, 15, 31)),
    (2.0, "THE HOLLOW THRONE", "End the corruption", (15, 10, 26)),
    (3.0, "PLAYTREE", "Awaken. Rebuild. Restore Balance.", (0, 0, 0)),
]

def draw_tree(d, cx, cy, scale, t, color=GREEN):
    r = int(18 * scale)
    d.rectangle((cx - 3, cy, cx + 3, cy + int(22 * scale)), fill=(58, 42, 26))
    for dx, dy, rr in [(0, -int(14*scale), r), (-int(11*scale), -int(8*scale), int(r*0.7)),
                       (int(11*scale), -int(8*scale), int(r*0.7))]:
        pulse = 1 + 0.04 * math.sin(t * 2)
        d.ellipse((cx+dx-int(rr*pulse), cy+dy-int(rr*pulse), cx+dx+int(rr*pulse), cy+dy+int(rr*pulse)), fill=color)

def draw_humanoid(d, cx, cy, color):
    d.ellipse((cx-7, cy-30, cx+7, cy-16), fill=(240, 208, 160))
    d.rectangle((cx-9, cy-16, cx+9, cy+6), fill=color)
    d.line((cx+9, cy-8, cx+18, cy-20), fill=color, width=3)

def frame(scene, t, scene_t):
    title, sub, bg = scene[1], scene[2], scene[3]
    img = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(img)
    # ambient motes
    for _ in range(30):
        x = random.randint(0, W); y = random.randint(0, H)
        a = random.randint(60, 140)
        d.ellipse((x, y, x+2, y+2), fill=(a, min(255, a+80), a))
    # ground
    d.rectangle((0, int(H*0.7), W, H), fill=tuple(max(0, c-5) for c in bg))
    # scene art
    name = title
    if 'FOREST' in name or 'COMBAT' in name:
        for i in range(6):
            draw_tree(d, 90 + i*160, int(H*0.72), 1.0, t)
        draw_humanoid(d, 300, int(H*0.7), GREEN)
        draw_humanoid(d, 380, int(H*0.72), (112, 160, 255))
        if 'COMBAT' in name:
            for i in range(3):
                ex = 650 + i*60
                d.ellipse((ex, int(H*0.67), ex+24, int(H*0.72)), fill=(138, 58, 58))
    elif 'CRYSTAL' in name:
        for i in range(12):
            cx = i*85; cy = 100 + int(math.sin(t+i)*40)
            d.polygon([(cx, cy-40), (cx-14, cy+20), (cx+14, cy+20)], fill=(60+ i*8, 120, 200))
        d.ellipse((W//2-40, H//2-40, W//2+40, H//2+40), outline=(120,180,255), width=3)
    elif 'BOSS' in name:
        draw_tree(d, W//2+120, int(H*0.7), 3.5, t, (138, 58, 58))
        d.ellipse((W//2+100, H//2-60, W//2+140, H//2-20), fill=(255, 60, 60))
        draw_humanoid(d, 300, int(H*0.7), GREEN)
    elif 'STORM' in name:
        for i in range(6):
            cx = (i*180 + int(t*20)) % W
            d.ellipse((cx, 70+i*10, cx+90, 95+i*10), fill=(100, 120, 160))
        d.line((W//2+80, 120, W//2+60, 200, W//2+90, 210), fill=(200, 220, 255), width=3)
    elif 'MULTIPLAYER' in name:
        colors = [GREEN, (112,160,255), (255,112,80), (255,160,80), (192,112,255), (255,80,160), (80,192,255), (160,255,80)]
        for i in range(8):
            draw_humanoid(d, 120+i*100, int(H*0.65+math.sin(t+i)*8), colors[i])
    elif 'BASE' in name:
        for i in range(7):
            bx = 60+i*130; bh = 60+int(math.sin(i*2)*30)
            d.rectangle((bx, H-60, bx+70, H+10), fill=(40, 70, 45))
            d.rectangle((bx+10, H-40, bx+25, H-25), fill=GREEN)
    elif 'CREATURE' in name:
        colors = [GREEN, (255,112,80), (112,160,255), (255,160,80), (192,112,255)]
        for i in range(5):
            ex = 180+i*150; ey = int(H*0.6+math.sin(t*1.5+i)*8)
            d.ellipse((ex-18, ey-24, ex+18, ey+24), fill=colors[i])
    elif 'HOLLOW' in name:
        d.ellipse((W//2-40, H//2-70, W//2+40, H//2+10), fill=(26, 10, 47))
        d.ellipse((W//2-20, H//2-50, W//2-10, H//2-40), fill=GREEN)
        d.ellipse((W//2+10, H//2-50, W//2+20, H//2-40), fill=GREEN)
        draw_humanoid(d, 300, int(H*0.7), GREEN)
    else:  # finale
        for i in range(40):
            ang = t*1.5 + i*math.pi*2/40
            r = 200 + math.sin(t*2+i)*20
            x = W//2 + int(math.cos(ang)*r); y = H//2 + int(math.sin(ang)*r)
            d.ellipse((x, y, x+3, y+3), fill=GREEN)
        draw_tree(d, W//2, int(H*0.75), 3, t)
        d.text((W//2, H//2-90), "PLAYTREE", font=font(64), fill=GREEN, anchor='mm')

    # text overlay with fade
    alpha = min(scene_t/0.5, 1)
    f1 = font(38); f2 = font(18)
    d.text((W//2, H//2-20), title, font=f1, fill=GREEN, anchor='mm')
    d.text((W//2, H//2+22), sub, font=f2, fill=GOLD, anchor='mm')
    # letterbox
    d.rectangle((0, 0, W, 22), fill=(0,0,0))
    d.rectangle((0, H-22, W, H), fill=(0,0,0))
    return img

frames = []
fps = 12
for dur, title, sub, bg in SCENES:
    scene = (dur, title, sub, bg)
    for step in range(int(dur*fps)):
        frames.append(frame(scene, step/fps + len(frames)/fps*0.1, step/fps).convert('P', palette=Image.ADAPTIVE, colors=128))

frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=int(1000/fps), loop=0)
print(f"Saved {OUT} ({len(frames)} frames, ~{sum(s[0] for s in SCENES):.0f}s)")
