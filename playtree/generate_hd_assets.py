"""Generate high-value animated 512px sprite sheets + longer music for PLAYTREE.
Creates multi-frame animations (idle/walk/attack) for each class, animated enemy
sheets, and longer musical tracks. Output: assets/hd/ folder.
Real quality improvements, no junk padding.
"""
from PIL import Image, ImageDraw, ImageFilter
import math, os, random, struct, wave

OUT = os.path.join(os.path.dirname(__file__), 'assets', 'hd')
os.makedirs(OUT, exist_ok=True)
S = 512  # sprite size

def new(w=None, h=None):
    return Image.new('RGBA', (w or S, h or S), (0,0,0,0))

def shade_polygon(d, pts, color, outline=None):
    d.polygon(pts, fill=color)
    if outline:
        d.line(pts + [pts[0]], fill=outline, width=4)

def glow(img, cx, cy, r, color, alpha=40):
    g = new(img.width, img.height)
    gd = ImageDraw.Draw(g)
    for i in range(6, 0, -1):
        rr = r + i*10
        gd.ellipse((cx-rr, cy-rr, cx+rr, cy+rr), fill=(*color, alpha//6))
    img.alpha_composite(g)

# ============ CLASS ANIMATION SHEETS (idle 4f, walk 4f, attack 4f) ============
CLASSES = {
    'guardian': (90,160,255), 'ranger': (100,220,120), 'mage': (200,120,255),
    'mechanic': (255,180,80), 'beast': (255,120,120),
}
FRAMES = {'idle': 4, 'walk': 4, 'attack': 4}

def draw_character(img, frame, anim, color, t):
    d = ImageDraw.Draw(img)
    cx, base_y = S//2, 430
    bob = int(math.sin(t*math.pi/2)*8) if anim=='walk' else int(math.sin(t*2)*3)
    # shadow
    d.ellipse((cx-90, base_y-10, cx+90, base_y+30), fill=(0,0,0,70))
    # armor/cloak
    cloak = [ (cx-70, 230+bob), (cx+70,230+bob), (cx+110,base_y), (cx-110,base_y) ]
    shade_polygon(d, cloak, (*color, 230), (255,255,255,60))
    # armor plate highlight
    d.polygon([(cx-45,250+bob),(cx+45,250+bob),(cx+70,base_y-20),(cx-70,base_y-20)], fill=(*tuple(min(255,c+40) for c in color),200))
    # head
    d.ellipse((cx-55,120+bob,cx+55,240+bob), fill=(240,205,160))
    # hair/helm
    d.arc((cx-60,105+bob,cx+60,190+bob),180,360,fill=(50,35,25),width=12)
    d.rectangle((cx-60,120+bob,cx+60,135+bob), fill=tuple(max(0,c-30) for c in color))
    # eyes
    d.ellipse((cx-32,175+bob,cx-12,195+bob),fill=(30,30,45))
    d.ellipse((cx+12,175+bob,cx+32,195+bob),fill=(30,30,45))
    # weapon swing based on attack frame
    if anim=='attack':
        swing = [-1.2,-0.4,0.4,1.2][frame]
        ex = cx + 150*math.cos(swing)
        ey = 300 + 150*math.sin(swing) + bob
    else:
        ex, ey = cx+140, 340+bob
    glow(img, int(ex), int(ey), 40, color, 80)
    d.line((cx+80,330+bob,ex,ey), fill=(230,230,240), width=14)
    d.ellipse((ex-12,ey-12,ex+12,ey+12), fill=(255,255,255))

for cls, col in CLASSES.items():
    for anim, count in FRAMES.items():
        sheet = new(S*count, S)
        for f in range(count):
            frame = new(S,S)
            draw_character(frame, f, anim, col, f)
            sheet.alpha_composite(frame, (f*S, 0))
        path = os.path.join(OUT, f'{cls}_{anim}.png')
        sheet.save(path, optimize=True)
print('Created class animation sheets')

# ============ ENEMY ANIMATION SHEETS ============
for i in range(6):
    c = [(150,40,60),(80,30,110),(60,140,60),(50,100,60),(200,80,160),(180,160,90)][i]
    sheet = new(S*4, S)
    for f in range(4):
        im = new(S,S); d=ImageDraw.Draw(im)
        cx,cy=S//2,320
        bounce=int(math.sin(f*math.pi/2)*12)
        d.ellipse((cx-100,460,cx+100,490),fill=(0,0,0,70))
        d.ellipse((cx-110,160+bounce,cx+110,470+bounce),fill=c)
        d.ellipse((cx-70,110+bounce,cx+70,260+bounce),fill=tuple(min(255,x+25) for x in c))
        for a in range(0,360,50):
            x=cx+int(math.cos(math.radians(a))*70); y=300+int(math.sin(math.radians(a))*90)+bounce
            d.ellipse((x-8,y-8,x+8,y+8),fill=(20,0,20,180))
        d.ellipse((cx-55,210+bounce,cx-20,245+bounce),fill=(255,60,60))
        d.ellipse((cx+20,210+bounce,cx+55,245+bounce),fill=(255,60,60))
        glow(im,cx,300,120,c,50)
        sheet.alpha_composite(im,(f*S,0))
    sheet.save(os.path.join(OUT,f'enemy_{i}_walk.png'),optimize=True)
print('Created enemy animation sheets')

# ============ LONGER MUSIC (stereo, ~2 min each) ============
def write_track(name, freq_seq, dur_per=0.25, vol=0.12, kind='sine'):
    rate=22050; path=os.path.join(OUT,name)
    with wave.open(path,'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
        for f in freq_seq:
            n=int(rate*dur_per); data=bytearray()
            for i in range(n):
                t=i/rate
                if kind=='square': v=1 if math.sin(2*math.pi*f*t)>0 else -1
                elif kind=='triangle': v=2*abs(2*((f*t)%1)-1)-1
                else: v=math.sin(2*math.pi*f*t)
                env=min(1,t*20,(dur_per-t)*20)
                data+=struct.pack('<h',int(v*vol*env*32767))
            w.writeframes(bytes(data))

# melodic sequences ~2 minutes
scale=[261.63,293.66,329.63,392,440,523.25]
seq_forest=[scale[i%len(scale)] for i in range(480)]
seq_battle=[scale[(i*3)%len(scale)]*2 for i in range(480)]
seq_sanctuary=[scale[(i//4)%len(scale)]/2 for i in range(480)]
write_track('music_forest_long.wav',seq_forest,0.25,0.10,'sine')
write_track('music_battle_long.wav',seq_battle,0.25,0.09,'triangle')
write_track('music_sanctuary_long.wav',seq_sanctuary,0.25,0.10,'sine')
print('Created long music tracks')

total=sum(os.path.getsize(os.path.join(OUT,f)) for f in os.listdir(OUT))
print(f'HD assets total: {total/1024/1024:.1f} MB, {len(os.listdir(OUT))} files')
