"""Generate real PNG sprite sheets and WAV audio for PLAYTREE.
Creates HD-styled pixel art sprites (scaled 4x with smooth shading) and
procedural sound effects/music as WAV files. Output: assets/ folder.
"""
from PIL import Image, ImageDraw, ImageFilter
import math, random, os, wave, struct

OUT = os.path.join(os.path.dirname(__file__), 'assets')
os.makedirs(OUT, exist_ok=True)

def new(w, h):
    return Image.new('RGBA', (w, h), (0,0,0,0))

def glow_circle(img, cx, cy, r, color, alpha=60):
    g = new(img.width, img.height)
    d = ImageDraw.Draw(g)
    for i in range(5, 0, -1):
        rr = r + i*4
        d.ellipse((cx-rr, cy-rr, cx+rr, cy+rr), fill=(*color, alpha//5))
    img.alpha_composite(g)
    d = ImageDraw.Draw(img)
    d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=color)

# ===================== SPRITES =====================
# Player character sprite (4 classes) 64x64
CLASS_COLORS = {'guardian': (90,160,255), 'ranger': (100,220,120),
                'mage': (200,120,255), 'mechanic': (255,180,80), 'beast': (255,120,120)}
for cls, col in CLASS_COLORS.items():
    im = new(64,64)
    d = ImageDraw.Draw(im)
    # shadow
    d.ellipse((14,54,50,62), fill=(0,0,0,80))
    # cloak/body
    d.polygon([(20,30),(44,30),(50,54),(14,54)], fill=col)
    d.polygon([(24,32),(40,32),(42,52),(22,52)], fill=tuple(min(255,c+30) for c in col))
    # head
    d.ellipse((24,12,40,30), fill=(240,205,160))
    # hair
    d.arc((23,10,41,26), 180, 360, fill=(60,40,30), width=3)
    # eyes
    d.ellipse((28,20,31,24), fill=(30,30,40)); d.ellipse((34,20,37,24), fill=(30,30,40))
    # weapon glow
    glow_circle(im, 50, 38, 6, col, 100)
    d.line((46,42,54,28), fill=(220,220,230), width=3)
    im.save(os.path.join(OUT, f'player_{cls}.png'))
print('Created player sprites')

# Enemy sprite 48x48
for i in range(6):
    im = new(48,48); d=ImageDraw.Draw(im)
    c = [(150,40,60),(80,30,110),(60,140,60),(50,100,60),(200,80,160),(180,160,90)][i]
    d.ellipse((12,18,36,44), fill=c)
    d.ellipse((16,12,32,28), fill=tuple(min(255,x+20) for x in c))
    # corruption veins
    for a in range(0,360,60):
        x=24+math.cos(math.radians(a))*10; y=30+math.sin(math.radians(a))*10
        d.ellipse((x-2,y-2,x+2,y+2), fill=(20,0,20,150))
    # eyes
    d.ellipse((18,24,22,29), fill=(255,60,60)); d.ellipse((27,24,31,29), fill=(255,60,60))
    im.save(os.path.join(OUT, f'enemy_{i}.png'))
print('Created enemy sprites')

# Tree sprite 128x128
im = new(128,128); d=ImageDraw.Draw(im)
d.rectangle((58,80,70,128), fill=(70,45,25))
for cx,cy,r in [(64,50,38),(35,65,26),(93,65,26),(50,35,24),(80,35,24)]:
    d.ellipse((cx-r,cy-r,cx+r,cy+r), fill=(40,130,55))
    d.ellipse((cx-r+6,cy-r+4,cx+r-6,cy+r-10), fill=(70,190,80))
glow_circle(im,64,45,44,(85,239,120),50)
im.save(os.path.join(OUT,'tree.png'))
print('Created tree sprite')

# Item icon 32x32
for name,c in [('coin',(255,215,80)),('gem',(120,200,255)),('potion',(255,100,150)),('seed',(100,220,120))]:
    im=new(32,32); d=ImageDraw.Draw(im)
    if name=='coin':
        d.ellipse((6,6,26,26),fill=c); d.ellipse((9,9,23,23),outline=(200,150,30),width=2)
    elif name=='gem':
        d.polygon([(16,4),(28,14),(16,28),(4,14)],fill=c)
        d.polygon([(16,4),(22,14),(16,28),(10,14)],fill=(180,230,255))
    elif name=='potion':
        d.rectangle((13,4,19,10),fill=(200,200,200))
        d.ellipse((8,10,24,28),fill=c)
    else:
        d.ellipse((10,14,22,26),fill=c); d.polygon([(16,4),(16,14)],fill=(80,180,80),width=2)
    im.save(os.path.join(OUT,f'item_{name}.png'))
print('Created item icons')

# ===================== AUDIO =====================
def tone(freq, dur, vol=0.2, wave_type='sine'):
    rate = 22050
    n = int(rate*dur)
    data = bytearray()
    for i in range(n):
        t = i/rate
        if wave_type=='square': v = 1 if math.sin(2*math.pi*freq*t)>0 else -1
        elif wave_type=='saw': v = 2*((freq*t)%1)-1
        else: v = math.sin(2*math.pi*freq*t)
        env = min(1, t*30, (dur-t)*10)
        data += struct.pack('<h', int(v*vol*env*32767))
    return bytes(data)

def noise(dur, vol=0.15):
    rate=22050; n=int(rate*dur); data=bytearray()
    for i in range(n):
        v=random.uniform(-1,1); env=min(1,(dur-i/rate)*15)
        data+=struct.pack('<h',int(v*vol*env*32767))
    return bytes(data)

def save_wav(name, samples):
    with wave.open(os.path.join(OUT,name),'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(22050)
        w.writeframes(samples)

save_wav('sfx_hit.wav', noise(0.12,0.3)+tone(180,0.1,0.2,'square'))
save_wav('sfx_coin.wav', tone(880,0.08)+tone(1320,0.12))
save_wav('sfx_levelup.wav', tone(523,0.1)+tone(659,0.1)+tone(784,0.2))
save_wav('sfx_explode.wav', noise(0.4,0.35))
save_wav('sfx_select.wav', tone(440,0.06))
# simple background music loop (chords)
music = b''
for f in [220,277,330,277,220,330,392,330]:
    music += tone(f,0.5,0.08)
save_wav('music_theme.wav', music)
print('Created audio files')

print('Total assets:', len(os.listdir(OUT)))
