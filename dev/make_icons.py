# Made by Claude (2026-10-20): Collider's app icons, after Apple's visionOS app icon guidance:
# a circular icon from a square canvas; a background layer (a gradient that leaves room) and two foreground layers of
# filled, overlapping shapes with clear edges, the rear one translucent; shadows between the layers for depth and a
# soft light from above (in visionOS the system adds these; Collider draws them itself). No text.
# Glyphs: Material Symbols Rounded, filled (Apache 2.0). python dev/make_icons.py <font.woff2|ttf> <out folder>
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
from fontTools.ttLib import TTFont
SRC, OUT = sys.argv[1], sys.argv[2]
tt = TTFont(SRC)
cmap = {v: k for k, v in tt.getBestCmap().items()}
import os
os.makedirs(OUT, exist_ok=True)
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_glyphs.ttf")
tt.flavor = None
tt.save(F)
N = 1024


def font(px):
    f = ImageFont.truetype(F, px)
    f.set_variation_by_axes([1])  # filled
    return f


def glyph(name, frac, dx, dy, opacity):
    im = Image.new('L', (N, N), 0)
    d = ImageDraw.Draw(im)
    ch, f = chr(cmap[name]), font(int(N * frac))
    l, t, r, b = d.textbbox((0, 0), ch, font=f)
    d.text(((N - (r - l)) / 2 - l + dx * N, (N - (b - t)) / 2 - t + dy * N), ch, font=f, fill=255)
    return im.point(lambda v: int(v * opacity))


def gradient(c1, c2):
    x = Image.linear_gradient('L').rotate(90).resize((N, N))
    y = Image.linear_gradient('L').resize((N, N))
    t = Image.blend(x, y, 0.67)
    return Image.composite(Image.new('RGB', (N, N), c2), Image.new('RGB', (N, N), c1), t)


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def icon(name, c1, c2, layers):
    img = gradient(rgb(c1), rgb(c2)).convert('RGBA')
    light = Image.new('L', (N, N), 0)
    ImageDraw.Draw(light).ellipse((-N * 0.2, -N * 0.75, N * 1.2, N * 0.55), fill=70)
    img = Image.composite(Image.new('RGBA', (N, N), (255, 255, 255, 255)), img, light.filter(ImageFilter.GaussianBlur(N * 0.08)))
    for (g, frac, dx, dy, op) in layers:
        a = glyph(g, frac, dx, dy, op)
        sh = ImageChops.offset(a.point(lambda v: int(v * 0.42)).filter(ImageFilter.GaussianBlur(N * 0.022)), 0, int(N * 0.018))
        img = Image.composite(Image.new('RGBA', (N, N), (0, 0, 0, 255)), img, sh)
        face = Image.composite(Image.new('RGBA', (N, N), (225, 228, 240, 255)), Image.new('RGBA', (N, N), (255, 255, 255, 255)),
                               Image.linear_gradient('L').resize((N, N)).point(lambda v: int(v * 0.10)))
        img = Image.composite(face, img, a)
    mask = Image.new('L', (N, N), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, N - 1, N - 1), fill=255)
    rim = Image.new('L', (N, N), 0)
    ImageDraw.Draw(rim).ellipse((6, 6, N - 7, N - 7), outline=110, width=6)
    rim = ImageChops.multiply(rim, Image.linear_gradient('L').rotate(180).resize((N, N)))
    img = Image.composite(Image.new('RGBA', (N, N), (255, 255, 255, 255)), img, rim.filter(ImageFilter.GaussianBlur(2)))
    img.putalpha(mask)
    img.resize((256, 256), Image.LANCZOS).save(f'{OUT}/claude_app_{name}.png')
    print('made', name)


ICONS = {
    'smart_gen':      ('#8A93FF', '#4C36D6', [('view_kanban', 0.60, -0.06, -0.06, 0.42), ('view_kanban', 0.54, 0.04, 0.04, 1.0)]),
    'discover':       ('#FFAA4D', '#FF2D6A', [('photo_library', 0.58, -0.05, -0.04, 0.42), ('auto_awesome', 0.40, 0.11, 0.10, 1.0)]),
    'theme_gallery':  ('#9BE564', '#22A84A', [('wallpaper', 0.62, -0.05, -0.05, 0.40), ('landscape', 0.50, 0.05, 0.06, 1.0)]),
    'premium_market': ('#E26BFF', '#6E34E8', [('diamond', 0.62, -0.06, -0.06, 0.40), ('play_circle', 0.44, 0.08, 0.09, 1.0)]),
    'files':          ('#6CC8FF', '#0A63F0', [('folder', 0.56, -0.06, -0.07, 0.45), ('folder', 0.56, 0.05, 0.05, 1.0)]),
    'music':          ('#FF7A95', '#D0105C', [('graphic_eq', 0.62, -0.06, -0.05, 0.40), ('music_note', 0.52, 0.06, 0.05, 1.0)]),
    'browser':        ('#46E6CF', '#0087A8', [('public', 0.60, -0.06, -0.06, 0.40), ('explore', 0.48, 0.06, 0.06, 1.0)]),
    'documents':      ('#FFD95A', '#FF8A00', [('description', 0.58, -0.06, -0.06, 0.42), ('edit_document', 0.50, 0.06, 0.06, 1.0)]),
}
for k, (a, b, layers) in ICONS.items():
    icon(k, a, b, layers)
