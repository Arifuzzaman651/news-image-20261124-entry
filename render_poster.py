#!/usr/bin/env python3
"""Draw "The World in One Day" — a newspaper front page summing up
Tuesday 24 November 2026 — as a 1024x1024 PNG (entry.png).

System python3 + Pillow only; no network. Deterministic: the same
bytes every run. Run: python3 render_poster.py
"""

import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (248, 244, 232)
INK = (20, 20, 20)
RED = (178, 34, 34)
BLUE = (30, 80, 140)
GREEN = (34, 120, 60)
ORANGE = (200, 90, 20)
TEAL = (18, 110, 105)
GOLD = (180, 140, 20)
PANEL = (238, 240, 230)
GREY = (90, 88, 80)

BOLD_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
]
REG_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
]


def font(paths, size):
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def bold(size):
    return font(BOLD_PATHS, size)


def regular(size):
    return font(REG_PATHS, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def centred(draw, text, cx, y, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)


def rule(draw, x0, x1, y, width=3, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


# --- small drawn motifs -------------------------------------------------

def motif_chart(draw, x0, y0, x1, y1):
    """Rising bar chart with an arrow: the market jumps."""
    draw.rectangle([x0, y0, x1, y1], fill=PANEL, outline=INK, width=2)
    bars = [0.25, 0.38, 0.34, 0.55, 0.72, 0.92]
    bw = (x1 - x0 - 40) // len(bars)
    base = y1 - 24
    for i, h in enumerate(bars):
        bx = x0 + 20 + i * bw
        top = base - int(h * (y1 - y0 - 60))
        draw.rectangle([bx, top, bx + bw - 8, base], fill=GREEN)
    draw.line([(x0 + 22, base - 20), (x1 - 22, y0 + 26)], fill=RED, width=5)
    draw.polygon([(x1 - 30, y0 + 18), (x1 - 14, y0 + 26), (x1 - 30, y0 + 38)], fill=RED)
    draw.text((x0 + 20, y0 + 8), "+31%", font=bold(34), fill=RED)


def motif_ship(draw, x0, y0, s):
    """A warship on waves."""
    draw.rectangle([x0, y0 + 18, x0 + s, y0 + 46], fill=INK)
    draw.polygon([(x0, y0 + 46), (x0 + s, y0 + 46), (x0 + s - 14, y0 + 62),
                  (x0 + 14, y0 + 62)], fill=INK)
    draw.line([(x0 + s // 2, y0 + 18), (x0 + s // 2, y0)], fill=INK, width=4)
    for k, wy in enumerate([y0 + 70, y0 + 78]):
        draw.arc([x0, wy - 8, x0 + s, wy + 8], 0, 180, fill=BLUE, width=3)


def motif_document(draw, x0, y0, s):
    """A document stamped with a count."""
    draw.rectangle([x0 + 6, y0, x0 + s - 6, y0 + s], fill=(255, 255, 255),
                   outline=INK, width=2)
    for i in range(3):
        draw.line([(x0 + 16, y0 + 16 + i * 12), (x0 + s - 16, y0 + 16 + i * 12)],
                  fill=GREY, width=3)
    draw.text((x0 + 10, y0 + s - 40), "500k", font=bold(26), fill=RED)


def motif_talks(draw, x0, y0, s):
    """Four seats at one table: four-way talks."""
    c = [(x0 + 20, y0 + 20), (x0 + s - 20, y0 + 20),
         (x0 + 20, y0 + s - 20), (x0 + s - 20, y0 + s - 20)]
    cols = [BLUE, GOLD, RED, TEAL]
    cx, cy = x0 + s // 2, y0 + s // 2
    for (px, py), col in zip(c, cols):
        draw.line([(cx, cy), (px, py)], fill=GREY, width=3)
        draw.ellipse([px - 13, py - 13, px + 13, py + 13], fill=col)
    draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=INK)


def motif_fire(draw, x0, y0, s):
    """A factory with a flame above it."""
    draw.polygon([(x0 + s // 2, y0), (x0 + s - 8, y0 + 26), (x0 + s // 2 + 8, y0 + 30),
                  (x0 + s // 2 + 16, y0 + 14), (x0 + s // 2, y0 + 40),
                  (x0 + 8, y0 + 26)], fill=ORANGE)
    draw.rectangle([x0 + 6, y0 + 46, x0 + s - 6, y0 + s - 6], fill=INK)
    draw.rectangle([x0 + s - 22, y0 + 34, x0 + s - 12, y0 + 48], fill=INK)
    draw.rectangle([x0 + 16, y0 + s - 22, x0 + 30, y0 + s - 6], fill=PAPER)
    draw.rectangle([x0 + 38, y0 + s - 22, x0 + 52, y0 + s - 6], fill=PAPER)


def motif_ballot(draw, x0, y0, s):
    """A ballot box and the winning number."""
    draw.rectangle([x0 + 8, y0 + 26, x0 + s - 8, y0 + s - 6], fill=BLUE)
    draw.line([(x0 + 22, y0 + 26), (x0 + s - 22, y0 + 26)], fill=PAPER, width=5)
    draw.text((x0 + 2, y0 - 2), "258", font=bold(32), fill=RED)


# --- the poster ---------------------------------------------------------

STORIES = [
    # (kicker, headline, body, motif)
    ("WAR IN UKRAINE", "UKRAINE SINKS RUSSIAN WARSHIP",
     "Sea drones sink the corvette Merkury off Benghazi, Libya. A helicopter is destroyed.",
     motif_ship),
    ("RUSSIA", "RUSSIAN WAR DEAD NEAR 500,000",
     "Hacked official data counts more than 490,000 dead by September 2026.",
     motif_document),
    ("DIPLOMACY", "ZELENSKY SEEKS FOUR-WAY TALKS",
     "Ukraine, Europe, the US and Russia should meet \u201cas soon as possible\u201d.",
     motif_talks),
    ("INDONESIA", "FACTORY FIRE KILLS 24",
     "A blaze at a candy factory in Cikande leaves about 30 people missing.",
     motif_fire),
    ("UNITED STATES", "DEMOCRATS TAKE 258 SEATS",
     "The largest House majority since 1992. The Senate stands at 56 seats.",
     motif_ballot),
]


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([14, 14, W - 15, H - 15], outline=INK, width=3)

    # Masthead
    centred(d, "THE WORLD IN ONE DAY", W // 2, 34, bold(60), INK)
    rule(d, 60, W - 60, 118, 3)
    centred(d, "TUESDAY, 24 NOVEMBER 2026", W // 2, 130, bold(30), RED)
    centred(d, "Six stories that defined the day, from every corner of the globe",
            W // 2, 168, regular(20), GREY)
    rule(d, 30, W - 30, 200, 3)

    # Lead story: Nvidia
    lx, ly = 30, 216
    d.text((lx, ly), "TECHNOLOGY  \u00b7  MARKETS", font=bold(20), fill=RED)
    head = "HUANG RETURNS TO NVIDIA"
    d.text((lx, ly + 30), head, font=bold(38), fill=INK)
    body = ("Jensen Huang is reinstated as chief executive, "
            "and Nvidia shares surge 31% in a single day.")
    draw_lines(d, wrap(d, body, regular(23), 640), lx, ly + 92, regular(23), INK, 30)
    d.text((lx, ly + 158), "The chipmaker brings its founder back to the top job.",
           font=regular(20), fill=GREY)
    motif_chart(d, 716, 216, 994, 396)

    rule(d, 30, W - 30, 420, 3)

    # Grid: five stories plus a footer cell
    cw, ch, gap = 472, 168, 8
    gx, gy = 30, 438
    for i, (kicker, headline, body, motif) in enumerate(STORIES):
        cx = gx + (i % 2) * (cw + gap)
        cy = gy + (i // 2) * (ch + gap)
        motif(d, cx + 6, cy + 14, 84)
        tx = cx + 104
        d.text((tx, cy + 8), kicker, font=bold(16), fill=RED)
        hl = wrap(d, headline, bold(25), cw - 104)
        y = draw_lines(d, hl, tx, cy + 30, bold(25), INK, 29)
        draw_lines(d, wrap(d, body, regular(18), cw - 104), tx, y + 4,
                   regular(18), INK, 23)

    # Footer cell (sixth cell)
    fx = gx + cw + gap
    fy = gy + 2 * (ch + gap)
    d.rectangle([fx, fy, fx + cw, fy + ch], fill=INK)
    centred(d, "THE WORLD IN ONE DAY", fx + cw // 2, fy + 26, bold(26), PAPER)
    centred(d, "Tuesday, 24 November 2026", fx + cw // 2, fy + 62, bold(20), PAPER)
    centred(d, "Six stories, verified from", fx + cw // 2, fy + 100, regular(18), PAPER)
    centred(d, "multiple news reports.", fx + cw // 2, fy + 122, regular(18), PAPER)

    centred(d, "make.fun  \u00b7  The World in One Day  \u00b7  Tuesday 24 November 2026",
            W // 2, 972, regular(16), GREY)
    return img


if __name__ == "__main__":
    poster = build()
    poster.save("entry.png", format="PNG")
    print("wrote entry.png", poster.size, os.path.getsize("entry.png"), "bytes")
