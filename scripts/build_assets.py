"""Genera los SVG pixel-art del perfil (assets/).

Arte 100% original. Fuente: Press Start 2P (SIL Open Font License),
rasterizada a rectángulos para que se vea igual en cualquier navegador.

Uso:  python scripts/build_assets.py path/a/press-start-2p.woff
"""
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = sys.argv[1]
OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)
FONT = ImageFont.truetype(FONT_PATH, 8)

# Paleta "Sweetie 16"
C = dict(
    ink="#1a1c2c", plum="#5d275d", red="#b13e53", orange="#ef7d57",
    gold="#ffcd75", lime="#a7f070", green="#38b764", teal="#257179",
    navy="#29366f", blue="#3b5dc9", sky="#41a6f6", cyan="#73eff7",
    white="#f4f4f4", silver="#94b0c2", slate="#566c86", night="#333c57",
    dirt="#8b5a3c", dirt2="#5c3a28",
)


# ---------- utilidades ----------
def text_bitmap(s):
    w = max(8, len(s) * 8)
    im = Image.new("1", (w, 8), 0)
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    d.text((0, 0), s, font=FONT, fill=1)
    return {(x, y) for y in range(8) for x in range(w) if im.getpixel((x, y))}, w


def runs(pixels):
    """Agrupa píxeles en tramos horizontales -> (x, y, largo)."""
    out = []
    for y in sorted({p[1] for p in pixels}):
        xs = sorted(p[0] for p in pixels if p[1] == y)
        start = prev = xs[0]
        for x in xs[1:]:
            if x == prev + 1:
                prev = x
                continue
            out.append((start, y, prev - start + 1))
            start = prev = x
        out.append((start, y, prev - start + 1))
    return out


def rects(pixels, ox, oy, s, fill, extra=""):
    return "".join(
        f'<rect x="{ox + x * s}" y="{oy + y * s}" width="{n * s}" height="{s}" fill="{fill}"{extra}/>'
        for x, y, n in runs(pixels)
    )


def text(s, x, y, scale, fill, shadow=None, top=None, anchor="left"):
    """Texto pixelado. top=color de las 3 filas superiores (efecto dos tonos)."""
    px, w = text_bitmap(s)
    width = len(s) * 8 * scale
    if anchor == "center":
        x = x - width // 2
    out = ""
    if shadow:
        out += rects(px, x + scale, y + scale, scale, shadow)
    if top:
        out += rects({p for p in px if p[1] < 3}, x, y, scale, top)
        out += rects({p for p in px if p[1] >= 3}, x, y, scale, fill)
    else:
        out += rects(px, x, y, scale, fill)
    return out


def sprite(rows, palette, ox, oy, s):
    out = ""
    for key, color in palette.items():
        px = {(x, y) for y, r in enumerate(rows) for x, ch in enumerate(r) if ch == key}
        if px:
            out += rects(px, ox, oy, s, color)
    return out


def svg(w, h, body, style=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'shape-rendering="crispEdges">\n<style>{style}</style>\n{body}\n</svg>\n'
    )


# ---------- sprites originales ----------
BOT = [  # "Chep-bot", mascota original
    "......Y.....",
    "......O.....",
    "..OOOOOOOO..",
    ".OBBBBBBBBO.",
    ".OBCCBBCCBO.",
    ".OBCCBBCCBO.",
    ".OBBBBBBBBO.",
    ".OBBDDDDBBO.",
    "..OOOOOOOO..",
    ".OOSSGGSSOO.",
    "OSOSGGGGSOSO",
    "O.OSSSSSSO.O",
    "..OOO..OOO..",
    "..OO....OO..",
]
BOT_PAL = {"O": C["ink"], "B": C["silver"], "S": C["slate"], "C": C["cyan"],
           "D": C["night"], "G": C["lime"], "Y": C["gold"]}

COIN = [
    "..OOOO..",
    ".OYYYYO.",
    "OYYWYYYO",
    "OYYWYYYO",
    "OYYWYYYO",
    "OYYYYYDO",
    ".OYYYDO.",
    "..OOOO..",
]
COIN_PAL = {"O": C["ink"], "Y": C["gold"], "W": C["white"], "D": C["orange"]}

HEART = [
    ".RR.RR.",
    "RWRRRRR",
    "RRRRRRR",
    ".RRRRR.",
    "..RRR..",
    "...R...",
]
HEART_PAL = {"R": C["red"], "W": C["white"]}

TREE = [
    "...LLLL...",
    "..LLGLLL..",
    ".LLLLLGLL.",
    "LLGLLLLLLL",
    "LLLLLLGLLL",
    ".LLGLLLLL.",
    "..LLLLLL..",
    "....TT....",
    "....TT....",
    "....TT....",
]
TREE_PAL = {"L": C["green"], "G": C["lime"], "T": C["dirt2"]}

CLOUD = [
    "....WWWW......",
    "..WWWWWWWW.WW.",
    ".WWWWWWWWWWWWW",
    "SSWWWWWWWWWWWS",
    ".SSSSSSSSSSSS.",
]
CLOUD_PAL = {"W": C["white"], "S": C["silver"]}

FLOWER = [".R.", "RYR", ".R.", ".G."]
FLOWER_PAL = {"R": C["red"], "Y": C["gold"], "G": C["green"]}


def ground_pattern(pid, s=4, y0=0):
    """Bloque de pasto y tierra 14x14 (diseño propio)."""
    rnd = random.Random(7)
    rows = []
    for y in range(14):
        r = ""
        for x in range(14):
            if y < 3:
                r += "g" if rnd.random() < 0.25 else "G"
            elif y == 3:
                r += "G" if rnd.random() < 0.4 else "d"
            else:
                r += "k" if rnd.random() < 0.18 else "d"
        rows.append(r)
    rows[13] = "k" * 14
    rows = [r[:13] + "k" for r in rows]
    pal = {"G": C["green"], "g": C["lime"], "d": C["dirt"], "k": C["dirt2"]}
    size = 14 * s
    return (f'<pattern id="{pid}" y="{y0}" width="{size}" height="{size}" patternUnits="userSpaceOnUse">'
            + sprite(rows, pal, 0, 0, s) + "</pattern>")


def frame(w, h):
    """Marco de pixeles con esquinas recortadas."""
    return (
        f'<rect x="4" y="0" width="{w-8}" height="{h}" fill="{C["slate"]}"/>'
        f'<rect x="0" y="4" width="{w}" height="{h-8}" fill="{C["slate"]}"/>'
        f'<rect x="4" y="4" width="{w-8}" height="{h-8}" fill="{C["silver"]}"/>'
        f'<rect x="8" y="8" width="{w-16}" height="{h-16}" fill="{C["ink"]}"/>'
    )


BLINK = "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}.blink{animation:blink 1.2s steps(1) infinite}"
BOB = "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}.bob{animation:bob 2.4s steps(4) infinite}"
TWINKLE = "@keyframes tw{0%,100%{opacity:1}50%{opacity:.15}}.tw{animation:tw 3s steps(3) infinite}"
SPIN = ("@keyframes spin{0%,100%{transform:scaleX(1)}25%{transform:scaleX(.35)}50%{transform:scaleX(-1)}"
        "75%{transform:scaleX(-.35)}}.spin{animation:spin 1.6s steps(4) infinite;transform-box:fill-box;transform-origin:center}")
DRIFT = "@keyframes drift{from{transform:translateX(0)}to{transform:translateX(-1200px)}}.drift{animation:drift 60s linear infinite}"


def landscape(W, H, ground_rows=14, s=4, seed=3):
    """Cielo al atardecer, montañas, nubes y suelo. Devuelve (defs, body, ground_y)."""
    rnd = random.Random(seed)
    gh = ground_rows * s
    gy = H - gh
    bands = [(0.0, C["ink"]), (0.46, C["navy"]), (0.64, C["plum"]), (0.78, C["red"]), (0.88, C["orange"])]
    body = ""
    sky_h = gy
    for i, (f, col) in enumerate(bands):
        y0 = int(f * sky_h) // s * s
        y1 = sky_h if i == len(bands) - 1 else int(bands[i + 1][0] * sky_h) // s * s
        body += f'<rect x="0" y="{y0}" width="{W}" height="{y1 - y0}" fill="{col}"/>'
        if i:  # tramado entre bandas
            prev = bands[i - 1][1]
            body += "".join(f'<rect x="{x}" y="{y0}" width="{s}" height="{s}" fill="{prev}"/>'
                            for x in range(0, W, s * 2))
    # sol
    cx, cy, r = int(W * 0.8) // s * s, gy - 40, 60
    for y in range(-r, 0, s):
        if y > -24 and (y // s) % 3 == 0:
            continue  # franjas retro
        half = int((r * r - y * y) ** 0.5) // s * s
        col = C["gold"] if y < -30 else C["orange"]
        body += f'<rect x="{cx - half}" y="{cy + y}" width="{half * 2}" height="{s}" fill="{col}"/>'
    # estrellas
    for _ in range(int(W / 22)):
        x = rnd.randrange(0, W // s) * s
        y = rnd.randrange(0, int(sky_h * 0.45) // s) * s
        delay = rnd.random() * 3
        body += f'<rect class="tw" style="animation-delay:{delay:.2f}s" x="{x}" y="{y}" width="{s}" height="{s}" fill="{C["white"]}"/>'
    # montañas (dos capas)
    for col, base, amp, seg in ((C["night"], gy - 56, 36, 6), (C["teal"], gy - 24, 16, 4)):
        h = base
        x = 0
        while x < W:
            h = max(base - amp, min(base + amp // 3, h + rnd.choice([-2, -1, 1, 2]) * s))
            w = rnd.randrange(2, seg) * s
            body += f'<rect x="{x}" y="{h}" width="{w}" height="{gy - h}" fill="{col}"/>'
            x += w
    # nubes que se desplazan
    clouds = ""
    for i in range(6):
        x = 80 + i * 200 + rnd.randrange(0, 60)
        y = rnd.randrange(16, int(sky_h * 0.4))
        clouds += sprite(CLOUD, CLOUD_PAL, x, y, s)
        clouds += sprite(CLOUD, CLOUD_PAL, x + 1200, y, s)
    body += f'<g class="drift" opacity=".9">{clouds}</g>'
    defs = ground_pattern("ground", s, gy)
    body += f'<rect x="0" y="{gy}" width="{W}" height="{gh}" fill="url(#ground)"/>'
    return defs, body, gy


# ---------- banner ----------
def banner():
    W, H, s = 960, 340, 4
    defs, body, gy = landscape(W, H)
    body += f'<g class="bob">{text("CHEPE", W // 2, 64, 10, C["orange"], shadow=C["ink"], top=C["gold"], anchor="center")}</g>'
    body += text("WEB DEV / SYSADMIN / CYBERSEC", W // 2, 164, 2, C["white"], shadow=C["ink"], anchor="center")
    body += f'<g class="blink">{text("PRESS START", W // 2, 206, 2, C["cyan"], shadow=C["ink"], anchor="center")}</g>'
    # mascota, monedas, árbol y flores sobre el suelo
    body += f'<g class="bob" style="animation-duration:1.2s">{sprite(BOT, BOT_PAL, 96, gy - 14 * s, s)}</g>'
    for i, x in enumerate((236, 284, 332)):
        body += (f'<g class="bob" style="animation-delay:{i * .3}s"><g class="spin" style="animation-delay:{i * .2}s">'
                 f'{sprite(COIN, COIN_PAL, x, gy - 72, s)}</g></g>')
    body += sprite(TREE, TREE_PAL, 820, gy - 10 * s, s)
    for x in (40, 196, 600, 652, 760, 900):
        body += sprite(FLOWER, FLOWER_PAL, x, gy - 4 * s, s)
    (OUT / "banner.svg").write_text(svg(W, H, f"<defs>{defs}</defs>{body}",
                                        BLINK + BOB + TWINKLE + SPIN + DRIFT))


# ---------- tarjeta de jugador ----------
def player():
    W, H = 960, 232
    body = frame(W, H)
    # retrato
    body += f'<rect x="32" y="32" width="168" height="168" fill="{C["navy"]}"/>'
    body += f'<rect x="32" y="168" width="168" height="32" fill="{C["teal"]}"/>'
    body += f'<g class="bob" style="animation-duration:1.6s">{sprite(BOT, BOT_PAL, 68, 56, 8)}</g>'
    x0 = 232
    lines = [("PLAYER 1", "CHEPE", C["gold"]),
             ("CLASS", "FULL STACK DEV", C["white"]),
             ("PERKS", "WEB / SERVERS / SECURITY", C["white"])]
    for i, (k, v, col) in enumerate(lines):
        y = 36 + i * 32
        body += text(k, x0, y, 2, C["cyan"])
        body += text(v, x0 + 176, y, 2, col)
    # HP
    y = 36 + 3 * 32
    body += text("HP", x0, y, 2, C["cyan"])
    for i in range(5):
        body += sprite(HEART, HEART_PAL, x0 + 176 + i * 36, y - 2, 4)
    # XP con barra animada
    y += 32
    body += text("XP", x0, y, 2, C["cyan"])
    bx, bw = x0 + 176, 320
    body += f'<rect x="{bx}" y="{y - 4}" width="{bw}" height="24" fill="{C["slate"]}"/>'
    body += f'<rect x="{bx + 4}" y="{y}" width="{bw - 8}" height="16" fill="{C["night"]}"/>'
    body += f'<rect class="xp" x="{bx + 4}" y="{y}" width="{bw - 8}" height="16" fill="{C["lime"]}"/>'
    body += f'<rect class="xp" x="{bx + 4}" y="{y}" width="{bw - 8}" height="4" fill="{C["white"]}" opacity=".5"/>'
    body += f'<g class="blink">{text("LEVELING UP", bx + bw + 16, y, 2, C["gold"])}</g>'
    xp = ("@keyframes xp{0%{transform:scaleX(0)}70%,100%{transform:scaleX(.82)}}"
          ".xp{animation:xp 4s steps(20) infinite;transform-box:fill-box;transform-origin:left}")
    (OUT / "player.svg").write_text(svg(W, H, body, BLINK + BOB + xp))


# ---------- inventario de habilidades ----------
INVENTORY = [
    ("LANGUAGES", C["gold"], ["C#", "JAVA", "C++", "PYTHON", "PHP", "JS"]),
    ("WEB", C["orange"], ["HTML5", "CSS3", "BOOTSTRAP", "JQUERY", "BLADE", "LARAVEL", ".NET"]),
    ("DATABASES", C["sky"], ["MYSQL", "MARIADB"]),
    ("SYSTEMS", C["lime"], ["LINUX", "UBUNTU", "KALI", "WINDOWS", "UBUNTU SRV", "WIN SERVER"]),
    ("TOOLS", C["cyan"], ["GIT", "GITHUB", "VS CODE", "VISUAL STUDIO"]),
]


def inventory():
    W = 960
    row_h = 88
    H = 96 + row_h * len(INVENTORY) + 16
    body = frame(W, H)
    body += text("INVENTORY", 32, 32, 3, C["gold"], shadow=C["plum"])
    slots = []
    for r, (label, col, items) in enumerate(INVENTORY):
        y = 92 + r * row_h
        body += f'<rect x="32" y="{y + 2}" width="8" height="8" fill="{col}"/>'
        body += text(label, 48, y, 2, col)
        x = 32
        for it in items:
            w = len(it) * 16 + 28
            sy = y + 28
            body += (f'<rect x="{x}" y="{sy}" width="{w}" height="44" fill="{C["ink"]}"/>'
                     f'<rect x="{x}" y="{sy}" width="{w - 4}" height="40" fill="{C["slate"]}"/>'
                     f'<rect x="{x + 4}" y="{sy + 4}" width="{w - 8}" height="36" fill="{C["night"]}"/>'
                     f'<rect x="{x + 4}" y="{sy + 34}" width="{w - 8}" height="6" fill="{col}" opacity=".85"/>')
            body += text(it, x + 14, sy + 12, 2, C["white"])
            slots.append((x, sy, w))
            x += w + 8
    n = len(slots)
    step = 100 / n
    sel = f"@keyframes sel{{0%,{step:.3f}%{{opacity:1}}{step + .001:.3f}%,100%{{opacity:0}}}}"
    sel += f".sel{{opacity:0;animation:sel {n * .5:.1f}s steps(1) infinite}}"
    for i, (x, sy, w) in enumerate(slots):
        body += (f'<g class="sel" style="animation-delay:{i * .5:.1f}s" fill="{C["gold"]}">'
                 f'<rect x="{x - 4}" y="{sy - 4}" width="{w + 4}" height="4"/>'
                 f'<rect x="{x - 4}" y="{sy + 44}" width="{w + 4}" height="4"/>'
                 f'<rect x="{x - 4}" y="{sy}" width="4" height="44"/>'
                 f'<rect x="{x + w}" y="{sy}" width="4" height="44"/></g>')
    (OUT / "inventory.svg").write_text(svg(W, H, body, sel))


# ---------- títulos de sección ----------
def title(name, label, icon, pal):
    W, H = 960, 64
    body = (f'<rect x="4" y="0" width="{W - 8}" height="{H}" fill="{C["night"]}"/>'
            f'<rect x="0" y="4" width="{W}" height="{H - 8}" fill="{C["night"]}"/>'
            f'<rect x="4" y="4" width="{W - 8}" height="{H - 8}" fill="{C["ink"]}"/>')
    body += sprite(icon, pal, 24, (H - len(icon) * 4) // 2, 4)
    body += text(label, 24 + len(icon[0]) * 4 + 20, 20, 3, C["gold"], shadow=C["plum"])
    # cursor parpadeante
    cx = 24 + len(icon[0]) * 4 + 20 + len(label) * 24 + 12
    body += f'<rect class="blink" x="{cx}" y="20" width="16" height="24" fill="{C["cyan"]}"/>'
    (OUT / f"title-{name}.svg").write_text(svg(W, H, body, BLINK))


STAR = ["...Y...", "..YYY..", "YYYYYYY", ".YYYYY.", ".YY.YY.", "YY...YY"]
SCROLL = ["OOOOOOOO", "OWWWWWWO", "OWDDDDWO", "OWWWWWWO", "OWDDDWWO", "OWWWWWWO", "OOOOOOOO"]
CHART = ["......G", "....G.G", "..R.G.G", "..R.G.G", "B.R.G.G", "B.R.G.G"]
SWORD = ["......W", ".....W.", "....W..", ".O.W...", "..O....", ".O.O...", "O......"]
MAIL = ["OOOOOOOO", "OWOWWOWO", "OWWOOWWO", "OWWWWWWO", "OOOOOOOO"]


def titles():
    title("achievements", "ACHIEVEMENTS", STAR, {"Y": C["gold"]})
    title("quests", "QUEST LOG", SWORD, {"W": C["silver"], "O": C["dirt"]})
    title("stats", "STATS", CHART, {"G": C["lime"], "R": C["orange"], "B": C["sky"]})
    title("contact", "SAVE POINT", MAIL, {"O": C["ink"], "W": C["white"]})
    title("about", "ABOUT ME", SCROLL, {"O": C["dirt"], "W": C["gold"], "D": C["dirt2"]})


# ---------- divisor y pie ----------
def divider():
    W, H, s = 960, 40, 4
    body = f'<defs>{ground_pattern("g2", s, 12)}</defs>'
    body += f'<rect x="0" y="12" width="{W}" height="28" fill="url(#g2)"/>'
    for x in (60, 180, 420, 540, 700, 880):
        body += sprite(FLOWER, FLOWER_PAL, x, 0, s)
    (OUT / "divider.svg").write_text(svg(W, H, body))


def footer():
    W, H, s = 960, 236, 4
    defs, body, gy = landscape(W, H, seed=11)
    body += text("THANKS FOR PLAYING!", W // 2, 40, 3, C["gold"], shadow=C["ink"], anchor="center")
    body += f'<g class="blink">{text("CONTINUE? > YES", W // 2, 96, 2, C["cyan"], shadow=C["ink"], anchor="center")}</g>'
    body += f'<g class="bob" style="animation-duration:1.2s">{sprite(BOT, BOT_PAL, 440, gy - 14 * s, s)}</g>'
    (OUT / "footer.svg").write_text(svg(W, H, f"<defs>{defs}</defs>{body}", BLINK + BOB + TWINKLE + DRIFT))


if __name__ == "__main__":
    banner()
    player()
    inventory()
    titles()
    divider()
    footer()
    print("ok:", sorted(p.name for p in OUT.iterdir()))
