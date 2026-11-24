"""Generate cinematic cutscene GIFs for PLAYTREE.
Creates animated, letterboxed scenes with dramatic camera moves:
- Boss intro: Root Titan rises, screen shake, red glow
- Story: corruption spreads over the peaceful forest
- Victory: tree restored, light returns
- Chapter intro: world map pan with title cards
Output: assets/hd/cutscenes/*.gif
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os, random

OUT = os.path.join(os.path.dirname(__file__), 'assets', 'hd', 'cutscenes')
os.makedirs(OUT, exist_ok=True)
W, H = 960, 540
GREEN = (85, 239, 120)
GOLD = (255, 215, 80)
RED = (255, 70, 70)

def font(size, bold=True):
    p = r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"
    return ImageFont.truetype(p, size) if os.path.exists(p) else ImageFont.load_default()

def letterbox(img):
    d = ImageDraw.Draw(img)
    d.rectangle((0,0,W,42), fill=(0,0,0))
    d.rectangle((0,H-42,W,H), fill=(0,0,0))
    return img

def vignette(img, strength=120):
    overlay = Image.new('L', (W,H), 0)
    d = ImageDraw.Draw(overlay)
    d.ellipse((-100,-100,W+100,H+100), fill=strength)
    overlay = overlay.filter(ImageFilter.GaussianBlur(90))
    dark = Image.new('RGBA',(W,H),(0,0,0))
    return Image.composite(img, dark, overlay)

def stars(img, t, n=60):
    d=ImageDraw.Draw(img)
    random.seed(1)
    for _ in range(n):
        x=random.randint(0,W); y=random.randint(0,H-84)+42
        a=int(120+100*math.sin(t+ x))
        d.ellipse((x,y,x+2,y+2),fill=(a,a,a))
    return d

def draw_tree_scene(img, t, corruption=0.0, healed=False):
    d=ImageDraw.Draw(img)
    cx=W//2; base=H-90
    # ground
    d.rectangle((0,base-40,W,H),fill=(20,55+ (30 if healed else 0),25))
    # tree trunk
    d.rectangle((cx-26,base-160,cx+26,base),fill=(70,45,25))
    # canopy layers
    for dx,dy,r in [(0,-90,85),(-60,-40,60),(60,-40,60),(-35,-130,50),(35,-130,50)]:
        c = GREEN if healed else (40+int(corruption*60), 130-int(corruption*80), 55)
        d.ellipse((cx+dx-r,base+dy-r,cx+dx+r,base+dy+r),fill=c)
        d.ellipse((cx+dx-r+10,base+dy-r+8,cx+dx+r-10,base+dy+r-12),
                  fill=tuple(min(255,x+25) for x in c))
    # glow
    if healed:
        g=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(g)
        for i in range(8,0,-1):
            gd.ellipse((cx-150-i*10,base-160-i*10,cx+150+i*10,base+160+i*10),
                       fill=(*GREEN, 8))
        img.alpha_composite(g)
    return d

def frame_boss(t):
    """Root Titan boss intro."""
    img=Image.new('RGBA',(W,H),(20,5,15)); d=stars(img,t)
    # ground
    d.rectangle((0,H-130,W,H),fill=(40,10,10))
    # screen shake
    shake=int(math.sin(t*20)*6*min(1,t))
    cx=W//2+shake; cy=H-130
    # titan body rises
    rise=max(0, min(1,(t-0.5)/1.5))
    ty=cy-100-int(rise*120)
    d.rectangle((cx-70,ty,cx+70,cy),fill=(90,30,20))
    d.rectangle((cx-55,ty+15,cx+55,cy),fill=(120,45,30))
    # eyes
    d.ellipse((cx-30,ty+40,cx-10,ty+60),fill=RED)
    d.ellipse((cx+10,ty+40,cx+30,ty+60),fill=RED)
    # roots
    for i in range(7):
        a=math.pi+i*math.pi/6+math.sin(t+i)*0.1
        d.line((cx,cy,cx+math.cos(a)*180,cy+math.sin(a)*60),fill=(70,30,15),width=8)
    # red aura
    if t>1.5:
        g=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(g)
        gd.ellipse((cx-200,ty-120,cx+200,ty+260),fill=(*RED,25))
        img.alpha_composite(g)
    # hero silhouette
    d.ellipse((160,H-210,190,H-180),fill=(240,205,160))
    d.rectangle((155,H-180,195,H-120),fill=(60,150,80))
    d=letterbox(img)
    # title card
    if t>1.8:
        a=min(1,(t-1.8)/0.6)
        f=font(52)
        img.paste(Image.blend(img, Image.new('RGBA',(W,H),(0,0,0)), 0.4),(0,0))
        dd=ImageDraw.Draw(img)
        dd.text((W//2,H//2-80),"ROOT TITAN",font=f,fill=(255,90,90),anchor='mm')
        dd.text((W//2,H//2-20),"GUARDIAN OF THE FIRST CORE",font=font(20),fill=GOLD,anchor='mm')
    return img

def frame_story(t):
    """Corruption spreads over forest."""
    img=Image.new('RGBA',(W,H),(10,30,20)); stars(img,t)
    corrupt=min(1,max(0,(t-1)/3))
    draw_tree_scene(img,t,corruption=corrupt)
    # corruption particles
    d=ImageDraw.Draw(img)
    random.seed(5)
    for _ in range(40):
        x=random.randint(0,W); y=42+int((t*40+random.randint(0,400))%400)
        a=int(100*corrupt)
        d.ellipse((x,y,x+3,y+3),fill=(120,20,80,a))
    d=letterbox(img)
    dd=ImageDraw.Draw(img)
    if t<2:
        dd.text((W//2,110),"THE FOREST ONCE FLOURISHED",font=font(32),fill=GREEN,anchor='mm')
    elif t<4:
        dd.text((W//2,110),"THEN THE CORRUPTION CAME",font=font(32),fill=(200,60,120),anchor='mm')
    else:
        dd.text((W//2,110),"AWAKEN. REBUILD. RESTORE BALANCE.",font=font(28),fill=GOLD,anchor='mm')
    return img

def frame_victory(t):
    """Tree restored, light returns."""
    img=Image.new('RGBA',(W,H),(8,20,14)); stars(img,t)
    heal=min(1,max(0,(t-1)/3))
    draw_tree_scene(img,t,healed=heal>0.6)
    d=ImageDraw.Draw(img)
    # light rays
    for i in range(12):
        a=i*30+math.sin(t)*5
        x=W//2+math.cos(math.radians(a))*300
        d.line((W//2,60,x,H-90),fill=(255,255,180,int(30*heal)),width=3)
    d=letterbox(img)
    dd=ImageDraw.Draw(img)
    if t>1.5:
        dd.text((W//2,110),"THE CORE IS RESTORED",font=font(38),fill=GOLD,anchor='mm')
        dd.text((W//2,160),"Balance returns to the forest",font=font(20),fill=GREEN,anchor='mm')
    return img

def frame_chapter(t):
    """Chapter intro world pan with title."""
    img=Image.new('RGBA',(W,H),(10,20,40)); stars(img,t,100)
    d=ImageDraw.Draw(img)
    # parallax islands
    for i in range(8):
        x=int((i*180 - t*60)%(W+300)-150)
        y=200+int(math.sin(i*1.3)*80)
        d.ellipse((x,y,x+180,y+50),fill=(30,70,45))
        d.ellipse((x+40,y-30,x+140,y+10),fill=(50,100,60))
    d.rectangle((0,H-90,W,H),fill=(15,35,25))
    d=letterbox(img)
    dd=ImageDraw.Draw(img)
    a=min(1,max(0,(t-0.5)/0.8))
    dd.text((W//2,H//2-30),"CHAPTER 0",font=font(64),fill=GREEN,anchor='mm')
    dd.text((W//2,H//2+40),"SEASON 0  -  THE FOREST AWAKENING",font=font(22),fill=GOLD,anchor='mm')
    return img

CUTSCENES = {
    'boss_intro': (frame_boss, 4.5),
    'story_corruption': (frame_story, 5.5),
    'victory': (frame_victory, 4.5),
    'chapter_intro': (frame_chapter, 4.0),
}

for name,(fn,dur) in CUTSCENES.items():
    fps=12
    frames=[]
    for i in range(int(dur*fps)):
        t=i/fps
        fr=fn(t).convert('P',palette=Image.ADAPTIVE,colors=128)
        frames.append(fr)
    path=os.path.join(OUT,f'{name}.gif')
    frames[0].save(path,save_all=True,append_images=frames[1:],duration=int(1000/fps),loop=0)
    print(f'{name}: {len(frames)} frames, {os.path.getsize(path)/1024:.0f} KB')

print('Cutscenes generated in', OUT)

