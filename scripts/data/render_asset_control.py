"""Render one authored 2D count/layout control; never a final reference photograph."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

root = Path(__file__).resolve().parents[2]
output = root / "public/generated/frame-assets/controls/hair-N07-six-rows.png"
image = Image.new("RGB", (1024, 1536), "#d7d7d7")
draw = ImageDraw.Draw(image)
draw.polygon([(145,1536),(145,1190),(240,1100),(430,1040),
              (594,1040),(784,1100),(879,1190),(879,1536)], fill="#85878a")
draw.rounded_rectangle((425,760,599,1120), radius=70, fill="#b3a39a")
draw.ellipse((151,522,223,670), fill="#b3a39a")
draw.ellipse((801,522,873,670), fill="#b3a39a")
draw.ellipse((172,138,852,898), fill="#aaa09a", outline="#75675e", width=8)
draw.line((512,144,512,850), fill="#e4ddd7", width=12)
curves = [
    ((310,240),(265,340),(225,550),(225,820),1240),
    ((410,190),(385,360),(340,570),(340,840),1260),
    ((480,170),(475,390),(455,570),(455,860),1280),
    ((544,170),(549,390),(569,570),(569,860),1280),
    ((614,190),(639,360),(684,570),(684,840),1260),
    ((714,240),(759,340),(799,550),(799,820),1240),
]
for start, first, second, end, tip in curves:
    points = []
    for step in range(101):
        t = step / 100
        points.append(tuple((1-t)**3*start[axis] + 3*(1-t)**2*t*first[axis]
                            + 3*(1-t)*t*t*second[axis] + t**3*end[axis]
                            for axis in (0,1)))
    points.append((end[0],tip))
    draw.line(points, fill="#49362c", width=50, joint="curve")
    for y in range(end[1],tip-18,38):
        x = end[0]
        draw.line([(x-20,y),(x+20,y+18),(x-20,y+36)], fill="#8c6f59", width=5)
        draw.line([(x+20,y),(x-20,y+18),(x+20,y+36)], fill="#8c6f59", width=5)
    draw.rounded_rectangle((end[0]-25,tip-10,end[0]+25,tip+4),radius=5,fill="#151515")
output.parent.mkdir(parents=True,exist_ok=True)
image.save(output,format="PNG")
print(output.relative_to(root))

# Auxiliary working composite only: split the original central column into two.
# A native image edit must still naturalize the join; this is never a final asset.
base = Image.open(root / "public/generated/frame-assets/controls/hair-N07-five-row-edit-base.png").convert("RGB")
column = base.crop((432,160,576,1410))
half = column.resize((72,1250),Image.Resampling.LANCZOS)
working = base.copy()
working.paste(half,(432,160))
working.paste(half,(504,160))
working_path = output.with_name("hair-N07-six-row-photo-layout.png")
working.save(working_path,format="PNG")
print(working_path.relative_to(root))

# Keep inner brow heads fixed while moving only the lateral brow regions.
# This auxiliary appearance target still requires a native image cleanup result.
brow_base = Image.open(root / "public/generated/frame-assets/expression-E02-subtle.png").convert("RGB")
def brow_offset(x, y):
    if not 410 < y < 535:
        return 0.0
    for center in (330,694):
        if abs(x-center) < 80:
            horizontal = (1-((x-center)/80)**2)**2
            vertical = (1-((y-474)/64)**2)**2
            return 10*horizontal*max(0.0,vertical)
    return 0.0
mesh = []
for top in range(0,brow_base.height,16):
    bottom = min(top+16,brow_base.height)
    for left in range(0,brow_base.width,16):
        right = min(left+16,brow_base.width)
        quad = []
        for x,y in ((left,top),(left,bottom),(right,bottom),(right,top)):
            quad.extend((x,y+brow_offset(x,y)))
        mesh.append(((left,top,right,bottom),tuple(quad)))
brow_working = brow_base.transform(brow_base.size,Image.Transform.MESH,mesh,Image.Resampling.BICUBIC)
brow_path = output.with_name("expression-E02-outer-brow-layout.png")
brow_working.save(brow_path,format="PNG")
print(brow_path.relative_to(root))

skin_mask = Image.new("L",brow_working.size,0)
skin_draw = ImageDraw.Draw(skin_mask)
skin_draw.ellipse((215,270,815,1070),fill=255)
for box in ((275,435,475,505),(550,435,755,505),(312,495,473,594),
            (551,495,718,594),(335,760,680,890)):
    skin_draw.rectangle(box,fill=0)
skin_draw.ellipse((671,684,688,706),fill=0)
skin_mask = skin_mask.filter(ImageFilter.GaussianBlur(5))
soft_working = Image.composite(brow_working.filter(ImageFilter.GaussianBlur(1.2)),
                               brow_working,skin_mask)
soft_path = output.with_name("expression-E02-soft-photo-layout.png")
soft_working.save(soft_path,format="PNG")
print(soft_path.relative_to(root))
