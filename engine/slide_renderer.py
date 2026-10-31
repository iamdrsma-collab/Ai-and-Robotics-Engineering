"""
Cinematic Luxury University Slide Renderer (2560x1440 supersampled -> 1280x720 HD)
Course: AI.101 — Introduction to Artificial Intelligence (Module 01)
Footer Mandate: TRIUNE BIBLICAL UNIVERSITY GLOBAL EXTENSION USA (Text-Only, No Logo, No Faith Content)
"""

import os
import textwrap
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 2560, 1440
OUT_W, OUT_H = 1280, 720

FONT_DIR = ".cache/fonts"
ASSET_DIR = ".cache/assets"
FOOTER_TEXT = "TRIUNE BIBLICAL UNIVERSITY GLOBAL EXTENSION USA"

# Luxury Obsidian & Champagne-Gold Palette
BG_DEEP = (6, 9, 19)
BG_NAVY = (11, 18, 35)
BG_CARD = (14, 22, 42, 232)
BG_CARD_ALT = (19, 30, 56, 238)
GOLD_BRIGHT = (243, 229, 171)
GOLD = (212, 175, 55)
GOLD_DIM = (142, 111, 30)
CYAN = (56, 189, 248)
TEAL = (45, 212, 191)
EMERALD = (52, 211, 153)
CORAL = (251, 113, 133)
IVORY = (248, 250, 252)
SLATE_LIGHT = (203, 213, 225)
SLATE_MUTED = (148, 163, 184)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = os.path.join(FONT_DIR, name)
    return ImageFont.truetype(path, size)


F_CINZEL_HERO = lambda s: font("cinzel-latin-700-normal.ttf", s)
F_CINZEL_REG = lambda s: font("cinzel-latin-600-normal.ttf", s)
F_SERIF_ITALIC = lambda s: font("cormorant-garamond-latin-600-italic.ttf", s)
F_SANS_BOLD = lambda s: font("plus-jakarta-sans-latin-700-normal.ttf", s)
F_SANS_SEMI = lambda s: font("plus-jakarta-sans-latin-600-normal.ttf", s)
F_SANS_REG = lambda s: font("plus-jakarta-sans-latin-400-normal.ttf", s)
F_MONO_BOLD = lambda s: font("jetbrains-mono-latin-700-normal.ttf", s)
F_MONO_REG = lambda s: font("jetbrains-mono-latin-400-normal.ttf", s)


def make_luxury_canvas(bg_photo: str | None = None, vignette_strength: float = 0.82) -> Image.Image:
    """Create 2560x1440 obsidian-luxury background with optional photorealistic background."""
    base = Image.new("RGBA", (W, H), (*BG_DEEP, 255))
    draw = ImageDraw.Draw(base)

    if bg_photo and os.path.exists(os.path.join(ASSET_DIR, bg_photo)):
        photo = Image.open(os.path.join(ASSET_DIR, bg_photo)).convert("RGBA")
        # Aspect-fill resize to 2560x1440
        pw, ph = photo.size
        scale = max(W / pw, H / ph)
        nw, nh = int(pw * scale), int(ph * scale)
        photo = photo.resize((nw, nh), Image.Resampling.LANCZOS)
        left, top = (nw - W) // 2, (nh - H) // 2
        photo = photo.crop((left, top, left + W, top + H))
        base = Image.alpha_composite(base, photo)

        # Left-heavy cinematic luxury gradient overlay so text has high contrast
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        odraw = ImageDraw.Draw(overlay)
        for x in range(W):
            t = x / W
            # Stronger dark veil on left & bottom, clearer window on right
            alpha = int(255 * (vignette_strength - 0.26 * (t ** 1.2)))
            alpha = max(95, min(245, alpha))
            odraw.line([(x, 0), (x, H)], fill=(6, 10, 22, alpha))
        base = Image.alpha_composite(base, overlay)
    else:
        # Subtle deep architectural gradient + radial gold/cyan ambient glow
        for y in range(H):
            t = y / H
            r = int(6 + 7 * (1 - t))
            g = int(10 + 11 * (1 - t))
            b = int(20 + 22 * (1 - t))
            draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow)
        gdraw.ellipse([1650, -250, 2750, 750], fill=(212, 175, 55, 22))
        gdraw.ellipse([-300, 500, 750, 1450], fill=(56, 189, 248, 18))
        glow = glow.filter(ImageFilter.GaussianBlur(radius=120))
        base = Image.alpha_composite(base, glow)

        # Subtle architectural dot grid
        grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gr = ImageDraw.Draw(grid)
        for gx in range(120, W - 80, 96):
            for gy in range(140, 1180, 96):
                gr.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=(212, 175, 55, 22))
        base = Image.alpha_composite(base, grid)

    return base


def draw_chrome(img: Image.Image, slide_num: int, total_slides: int, section_tag: str, is_cover: bool = False) -> None:
    """Draw luxury top bar, architectural corner lines, and mandatory text-only footer."""
    draw = ImageDraw.Draw(img, "RGBA")

    if not is_cover:
        # Top header bar
        draw.rectangle([0, 0, W, 104], fill=(5, 8, 17, 225))
        draw.line([(0, 104), (W, 104)], fill=(*GOLD_DIM, 180), width=2)
        draw.line([(88, 104), (620, 104)], fill=(*GOLD, 255), width=3)

        draw.text((88, 34), "AI.101  •  INTRODUCTION TO ARTIFICIAL INTELLIGENCE", font=F_SANS_BOLD(24), fill=GOLD_BRIGHT)
        right_txt = f"{section_tag.upper()}   |   SLIDE {slide_num:02d} OF {total_slides:02d}"
        bbox = draw.textbbox((0, 0), right_txt, font=F_SANS_SEMI(22))
        draw.text((W - 88 - (bbox[2] - bbox[0]), 36), right_txt, font=F_SANS_SEMI(22), fill=SLATE_LIGHT)
    else:
        # Luxury outer double hairline frame on Cover Slides (above footer)
        m1, m2 = 46, 58
        draw.rectangle([m1, m1, W - m1, 1320], outline=(*GOLD_DIM, 150), width=2)
        draw.rectangle([m2, m2, W - m2, 1308], outline=(*GOLD, 95), width=1)
        # Corner L-accents
        cl = 44
        for cx, cy, dx, dy in [(m1, m1, 1, 1), (W - m1, m1, -1, 1), (m1, 1320, 1, -1), (W - m1, 1320, -1, -1)]:
            draw.line([(cx, cy), (cx + dx * cl, cy)], fill=GOLD_BRIGHT, width=5)
            draw.line([(cx, cy), (cx, cy + dy * cl)], fill=GOLD_BRIGHT, width=5)

    # Mandatory Institutional Footer Bar (y = 1352..1440 at 2x -> 676..720 in 720p)
    # STRICTLY TEXT ONLY — NO IMAGE LOGO ALLOWED
    draw.rectangle([0, 1352, W, H], fill=(4, 7, 15, 255))
    draw.line([(0, 1352), (W, 1352)], fill=(*GOLD, 235), width=3)
    draw.line([(560, 1352), (W - 560, 1352)], fill=GOLD_BRIGHT, width=4)

    f_foot = F_CINZEL_HERO(29)
    fb = draw.textbbox((0, 0), FOOTER_TEXT, font=f_foot)
    fw = fb[2] - fb[0]
    draw.text(((W - fw) // 2, 1380), FOOTER_TEXT, font=f_foot, fill=GOLD_BRIGHT)


def draw_pill(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, fg=GOLD_BRIGHT, bg=(12, 19, 36, 238), border=GOLD) -> int:
    f = F_SANS_BOLD(22)
    b = draw.textbbox((0, 0), text, font=f)
    pw = (b[2] - b[0]) + 44
    ph = 48
    draw.rounded_rectangle([x, y, x + pw, y + ph], radius=24, fill=bg, outline=(*border, 220), width=2)
    draw.text((x + 22, y + 10), text, font=f, fill=fg)
    return pw


def draw_card(draw: ImageDraw.ImageDraw, box: list[int], fill=BG_CARD, border=GOLD_DIM, radius: int = 24, accent_top: tuple | None = None):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=(*border, 175), width=2)
    if accent_top:
        draw.rounded_rectangle([x1 + 2, y1 + 2, x2 - 2, y1 + 10], radius=6, fill=(*accent_top, 255))


def draw_wrapped(draw: ImageDraw.ImageDraw, text: str, x: int, y: int, font_obj, fill, max_width: int, line_gap: int = 10) -> int:
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = ""
        for w in words:
            test = f"{cur} {w}".strip()
            b = draw.textbbox((0, 0), test, font=font_obj)
            if b[2] - b[0] <= max_width or not cur:
                cur = test
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    cy = y
    for ln in lines:
        if ln:
            draw.text((x, cy), ln, font=font_obj, fill=fill)
            b = draw.textbbox((0, 0), ln, font=font_obj)
            cy += (b[3] - b[1]) + line_gap
        else:
            cy += line_gap * 2
    return cy


def paste_framed_photo(base: Image.Image, photo_name: str, box: list[int], caption: str | None = None):
    x1, y1, x2, y2 = box
    bw, bh = x2 - x1, y2 - y1
    p = Image.open(os.path.join(ASSET_DIR, photo_name)).convert("RGBA")
    pw, ph = p.size
    sc = max(bw / pw, bh / ph)
    nw, nh = int(pw * sc), int(ph * sc)
    p = p.resize((nw, nh), Image.Resampling.LANCZOS)
    p = p.crop(((nw - bw) // 2, (nh - bh) // 2, (nw - bw) // 2 + bw, (nh - bh) // 2 + bh))

    mask = Image.new("L", (bw, bh), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, bw, bh], radius=24, fill=255)

    if caption:
        ov = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        od.rectangle([0, bh - 86, bw, bh], fill=(6, 10, 22, 220))
        od.line([(0, bh - 86), (bw, bh - 86)], fill=(*GOLD, 190), width=2)
        od.text((28, bh - 58), caption, font=F_SANS_SEMI(24), fill=GOLD_BRIGHT)
        p = Image.alpha_composite(p, ov)

    base.paste(p, (x1, y1), mask)
    draw = ImageDraw.Draw(base, "RGBA")
    draw.rounded_rectangle(box, radius=24, outline=(*GOLD, 210), width=3)


def draw_title_block(draw: ImageDraw.ImageDraw, tag: str, title: str, subtitle: str | None = None):
    draw_pill(draw, 88, 134, tag)
    draw.text((88, 198), title, font=F_CINZEL_HERO(48), fill=IVORY)
    if subtitle:
        draw.text((88, 262), subtitle, font=F_SANS_REG(27), fill=SLATE_LIGHT)


# ==============================================================================
# 24 LUXURY SLIDE LAYOUTS
# ==============================================================================

def render_all_slides(out_dir: str) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    total = 24

    def save_slide(img: Image.Image, idx: int):
        small = img.convert("RGB").resize((OUT_W, OUT_H), Image.Resampling.LANCZOS)
        p = os.path.join(out_dir, f"slide_{idx:02d}.png")
        small.save(p, "PNG", optimize=True)
        paths.append(p)

    # ------------------------------------------------------------------
    # SLIDE 01: MASTER CINEMATIC COVER
    # ------------------------------------------------------------------
    img = make_luxury_canvas("cover_robotics_lab.jpg", vignette_strength=0.88)
    draw_chrome(img, 1, total, "Course Cover", is_cover=True)
    d = ImageDraw.Draw(img, "RGBA")
    draw_pill(d, 130, 150, "BACHELOR OF AI & ROBOTICS ENGINEERING  •  YEAR 1 SEMESTER 1")
    d.text((130, 240), "AI.101 — INTRODUCTION TO", font=F_CINZEL_HERO(68), fill=IVORY)
    d.text((130, 328), "ARTIFICIAL INTELLIGENCE", font=F_CINZEL_HERO(74), fill=GOLD_BRIGHT)
    # Geometric luxury divider line (no emblem/logo)
    d.line([(130, 440), (980, 440)], fill=GOLD, width=4)
    d.rectangle([992, 434, 1004, 446], fill=GOLD_BRIGHT)
    d.text((130, 474), "Module 01: Foundations of AI & Intelligent Agents", font=F_SERIF_ITALIC(54), fill=IVORY)
    draw_wrapped(
        d,
        "A clear, practical university lecture covering how intelligent machines sense their world, "
        "evaluate choices mathematically, and execute safe actions in Python.",
        130, 560, F_SANS_REG(30), SLATE_LIGHT, max_width=1280, line_gap=14
    )
    # Luxury specs strip
    specs = [
        ("MODULE DEPTH", "12 Structured Sections"),
        ("PRACTICAL LAB", "Live Python Robot Agent"),
        ("LEVEL", "Undergraduate Year 1"),
    ]
    sx = 130
    for k, v in specs:
        draw_card(d, [sx, 760, sx + 410, 895], fill=(9, 15, 30, 215), border=GOLD)
        d.text((sx + 30, 784), k, font=F_SANS_BOLD(20), fill=GOLD)
        d.text((sx + 30, 822), v, font=F_SANS_SEMI(28), fill=IVORY)
        sx += 438
    save_slide(img, 1)

    # ------------------------------------------------------------------
    # SLIDE 02: LEARNING OBJECTIVES
    # ------------------------------------------------------------------
    img = make_luxury_canvas()
    draw_chrome(img, 2, total, "01 • Learning Objectives")
    d = ImageDraw.Draw(img, "RGBA")
    draw_title_block(d, "SECTION 01  •  LEARNING OBJECTIVES", "WHAT YOU WILL MASTER IN MODULE 01",
                     "Five clear, practical goals explained in simple everyday English")
    goals = [
        ("01", "Plain-English Definition", "Explain clearly what Artificial Intelligence is and how it differs from a regular fixed computer program."),
        ("02", "History & AI Levels", "Trace five major milestones since 1950 and distinguish Narrow AI, General AI, and Superintelligence."),
        ("03", "Intelligent Agent Loop", "Identify Sensors, Environment, Reasoning Engine, and Actuators using the PEAS checklist."),
        ("04", "Mathematical Decision Scoring", "Calculate action scores step by step with the Utility Formula U = w_s·S + w_p·P − w_e·E."),
        ("05", "Hands-On Python Coding", "Build, execute, and test a real Python decision program for a smart warehouse robot."),
    ]
    positions = [
        (88, 336, 1252, 560), (1308, 336, 2472, 560),
        (88, 594, 1252, 818), (1308, 594, 2472, 818),
        (88, 852, 2472, 1068),
    ]
    for (num, heading, desc), (x1, y1, x2, y2) in zip(goals, positions):
        draw_card(d, [x1, y1, x2, y2], accent_top=GOLD if num != "05" else CYAN)
        d.rounded_rectangle([x1 + 28, y1 + 36, x1 + 108, y1 + 116], radius=18, fill=(212, 175, 55, 38), outline=GOLD, width=2)
        d.text((x1 + 45, y1 + 52), num, font=F_CINZEL_HERO(34), fill=GOLD_BRIGHT)
        d.text((x1 + 136, y1 + 36), heading, font=F_SANS_BOLD(31), fill=IVORY)
        draw_wrapped(d, desc, x1 + 136, y1 + 86, F_SANS_REG(25), SLATE_LIGHT, max_width=(x2 - x1 - 170), line_gap=8)
    save_slide(img, 2)

    # ------------------------------------------------------------------
    # SLIDE 03: INTRODUCTION — WHAT IS AI?
    # ------------------------------------------------------------------
    img = make_luxury_canvas()
    draw_chrome(img, 3, total, "02 • Introduction")
    d = ImageDraw.Draw(img, "RGBA")
    draw_title_block(d, "SECTION 02  •  INTRODUCTION", "WHAT IS ARTIFICIAL INTELLIGENCE?",
                     "Building machines that observe, choose smartly, learn from experience, and act toward a goal")
    # Left card: Fixed Calculator
    draw_card(d, [88, 344, 1236, 860], fill=(14, 20, 36, 230), border=SLATE_MUTED)
    d.text((132, 388), "TRADITIONAL FIXED PROGRAM", font=F_SANS_BOLD(24), fill=SLATE_MUTED)
    d.text((132, 432), "Pocket Calculator", font=F_CINZEL_HERO(40), fill=IVORY)
    bullets_l = [
        "• Follows exact, rigid button rules written ahead of time",
        "• Never observes surroundings or changing conditions",
        "• Does not improve or adapt from past experience",
        "• Stops or fails when given unexpected messy inputs",
    ]
    cy = 516
    for b in bullets_l:
        cy = draw_wrapped(d, b, 132, cy, F_SANS_REG(27), SLATE_LIGHT, 1040, 12) + 14

    # Right card: AI System
    draw_card(d, [1324, 344, 2472, 860], fill=(16, 28, 52, 242), border=GOLD, accent_top=GOLD)
    d.text((1368, 388), "ARTIFICIAL INTELLIGENCE SYSTEM", font=F_SANS_BOLD(24), fill=GOLD_BRIGHT)
    d.text((1368, 432), "Adaptive Smart System", font=F_CINZEL_HERO(40), fill=GOLD_BRIGHT)
    bullets_r = [
        "• Observes real-world data through cameras, text, or sensors",
        "• Evaluates options to pick the best action for its goal",
        "• Learns useful patterns from historical examples",
        "• Adapts safely when its environment changes",
    ]
    cy = 516
    for b in bullets_r:
        cy = draw_wrapped(d, b, 1368, cy, F_SANS_REG(27), IVORY, 1040, 12) + 14

    # Bottom 4-step flow strip
    steps = [("1. OBSERVE", CYAN), ("2. REASON", GOLD_BRIGHT), ("3. LEARN", TEAL), ("4. ACT SAFELY", EMERALD)]
    fx = 88
    for idx_s, (st, col) in enumerate(steps):
        draw_card(d, [fx, 916, fx + 550, 1068], fill=(10, 18, 34, 240), border=col)
        d.text((fx + 44, 968), st, font=F_CINZEL_HERO(34), fill=col)
        if idx_s < 3:
            ax = fx + 560
            d.line([(ax, 992), (ax + 34, 992)], fill=GOLD, width=5)
            d.polygon([(ax + 40, 992), (ax + 24, 980), (ax + 24, 1004)], fill=GOLD_BRIGHT)
        fx += 607
    save_slide(img, 3)

    # ------------------------------------------------------------------
    # SLIDE 04: TIMELINE — HISTORY OF AI
    # ------------------------------------------------------------------
    img = make_luxury_canvas()
    draw_chrome(img, 4, total, "02 • Historical Foundations")
    d = ImageDraw.Draw(img, "RGBA")
    draw_title_block(d, "HISTORICAL TIMELINE", "FIVE MILESTONES IN ARTIFICIAL INTELLIGENCE",
                     "How AI grew from a philosophical question in 1950 into modern intelligent robotics")
    # Timeline horizontal spine
    d.line([(160, 680), (2400, 680)], fill=GOLD, width=6)
    milestones = [
        ("1950", "Alan Turing", "Asked 'Can machines think?' and proposed a practical communication test.", True),
        ("1956", "Dartmouth Workshop", "Scientists officially coined the name Artificial Intelligence.", False),
        ("1980s", "Expert Systems", "If–Then rule engines helped doctors and factories make structured choices.", True),
        ("1990s–00s", "Machine Learning", "Faster computers learned directly from datasets instead of hand-written rules.", False),
        ("2012–Today", "Deep & Hybrid AI", "Neural networks, language models, and autonomous robots transform industry.", True),
    ]
    xs = [280, 780, 1280, 1780, 2280]
    for (yr, title_m, desc_m, top_pos), cx in zip(milestones, xs):
        d.ellipse([cx - 20, 660, cx + 20, 700], fill=GOLD_BRIGHT, outline=BG_DEEP, width=5)
        if top_pos:
            d.line([(cx, 590), (cx, 660)], fill=GOLD, width=3)
            box = [cx - 210, 344, cx + 210, 590]
        else:
            d.line([(cx, 700), (cx, 770)], fill=CYAN, width=3)
            box = [cx - 210, 770, cx + 210, 1026]
        draw_card(d, box, border=GOLD if top_pos else CYAN)
        d.text((box[0] + 24, box[1] + 20), yr, font=F_CINZEL_HERO(32), fill=GOLD_BRIGHT if top_pos else CYAN)
        d.text((box[0] + 24, box[1] + 64), title_m, font=F_SANS_BOLD(26), fill=IVORY)
        draw_wrapped(d, desc_m, box[0] + 24, box[1] + 106, F_SANS_REG(22), SLATE_LIGHT, 372, 6)
    save_slide(img, 4)

    # ------------------------------------------------------------------
    # SLIDE 05: THREE CAPABILITY LEVELS
    # ------------------------------------------------------------------
    img = make_luxury_canvas()
    draw_chrome(img, 5, total, "02 • Capability Levels")
    d = ImageDraw.Draw(img, "RGBA")
    draw_title_block(d, "AI CLASSIFICATION", "NARROW AI VS. GENERAL AI VS. SUPERINTELLIGENCE",
                     "Understanding what exists in real engineering today versus long-term theory")
    cols = [
        ("LEVEL 01  •  REAL TODAY", "Narrow AI", EMERALD,
         "100% of Working Systems Today",
         "Built to master one specific task very well: translating speech, inspecting circuit boards, playing chess, or steering a warehouse robot.",
         "Status: Deployed across industry worldwide"),
        ("LEVEL 02  •  RESEARCH GOAL", "General AI (AGI)", GOLD_BRIGHT,
         "Broad Human-Level Flexibility",
         "A future single system able to learn, reason, and transfer skills across any intellectual subject just like a human engineer or scientist.",
         "Status: Active long-term scientific research"),
        ("LEVEL 03  •  THEORETICAL", "Superintelligence", CYAN,
         "Hypothetical Concept Only",
         "A purely theoretical idea of a machine surpassing the brightest human minds across science, engineering, and strategic reasoning.",
         "Status: Philosophical & safety thought experiment"),
    ]
    cx = 88
    for badge_t, name_t, col, sub_t, body_t, foot_t in cols:
        draw_card(d, [cx, 344, cx + 756, 1072], border=col, accent_top=col)
        draw_pill(d, cx + 36, 388, badge_t, fg=col, border=col)
        d.text((cx + 36, 466), name_t, font=F_CINZEL_HERO(42), fill=IVORY)
        d.text((cx + 36, 530), sub_t, font=F_SANS_BOLD(26), fill=col)
        d.line([(cx + 36, 582), (cx + 720, 582)], fill=(*col, 110), width=2)
        draw_wrapped(d, body_t, cx + 36, 614, F_SANS_REG(27), SLATE_LIGHT, 684, 12)
        d.rounded_rectangle([cx + 36, 956, cx + 720, 1034], radius=16, fill=(8, 13, 26, 230), outline=(*col, 130), width=2)
        d.text((cx + 56, 980), foot_t, font=F_SANS_SEMI(23), fill=IVORY)
        cx += 794
    save_slide(img, 5)

    # ------------------------------------------------------------------
    # SLIDE 06: SECTION COVER — CORE THEORY
    # ------------------------------------------------------------------
    img = make_luxury_canvas("ai_computing_history.jpg", vignette_strength=0.86)
    draw_chrome(img, 6, total, "03 • Core Theory", is_cover=True)
    d = ImageDraw.Draw(img, "RGBA")
    draw_pill(d, 130, 210, "SECTION 03  •  CORE UNIVERSITY THEORY")
    d.text((130, 304), "HOW ARTIFICIAL INTELLIGENCE", font=F_CINZEL_HERO(66), fill=IVORY)
    d.text((130, 392), "SYSTEMS THINK", font=F_CINZEL_HERO(74), fill=GOLD_BRIGHT)
    d.line([(130, 502), (920, 502)], fill=GOLD, width=4)
    d.text((130, 540), "Symbolic Logic, Probability, Neural Networks & Modern Hybrid Robotics",
           font=F_SERIF_ITALIC(50), fill=IVORY)
    draw_wrapped(
        d,
        "Great engineers never rely on just one tool. Discover the four main schools of AI "
        "and why modern robots combine them together.",
        130, 636, F_SANS_REG(30), SLATE_LIGHT, 1260, 14
    )
    save_slide(img, 6)

    # ------------------------------------------------------------------
    # SLIDE 07: FOUR SCHOOLS OF AI (2x2 BENTO)
    # ------------------------------------------------------------------
    img = make_luxury_canvas()
    draw_chrome(img, 7, total, "03 • Four Schools of AI")
    d = ImageDraw.Draw(img, "RGBA")
    draw_title_block(d, "CORE THEORY  •  AI PARADIGMS", "FOUR ENGINEERING APPROACHES TO AI",
                     "Choosing the right method—or combining them—for reliability, learning, and safety")
    quads = [
        ("01 • SYMBOLIC AI", "Clear Human Logic Rules", GOLD_BRIGHT,
         "Engineers write explicit IF–THEN rules (e.g., IF temp > 90°C THEN open cooling valve). Easy to inspect and audit, but struggles with raw camera pixels."),
        ("02 • STATISTICAL AI", "Reasoning Under Uncertainty", CYAN,
         "Uses probability math to make smart estimates even when sensor measurements are noisy, blurry, or incomplete."),
        ("03 • CONNECTIONISM", "Neural Networks & Deep Learning", TEAL,
         "Layers of connected mathematical nodes learn complex visual and language patterns automatically from thousands of examples."),
        ("04 • MODERN HYBRID AI", "The Robotics Gold Standard", EMERALD,
         "Combines neural networks for vision, statistical filters for position tracking, and hard symbolic rules to guarantee human safety."),
    ]
    qboxes = [(88, 340, 1252, 688), (1308, 340, 2472, 688), (88, 724, 1252, 1072), (1308, 724, 2472, 1072)]
    for (tag_q, title_q, col, desc_q), box in zip(quads, qboxes):
        draw_card(d, box, border=col, accent_top=col)
        d.text((box[0] + 36, box[1] + 34), tag_q, font=F_SANS_BOLD(22), fill=col)
        d.text((box[0] + 36, box[1] + 74), title_q, font=F_CINZEL_HERO(34), fill=IVORY)
        draw_wrapped(d, desc_q, box[0] + 36, box[1] + 136, F_SANS_REG(26), SLATE_LIGHT, 1088, 10)
    save_slide(img, 7)

    # ------------------------------------------------------------------
    # HELPER FOR PROGRESSIVE ANIMATED AGENT LOOP (SLIDES 08, 09, 10)
    # ------------------------------------------------------------------
    def render_agent_stage(slide_idx: int, stage: int, sub_head: str, stage_caption: str):
        im = make_luxury_canvas()
        draw_chrome(im, slide_idx, total, f"04 • Visual Explanation (Stage {stage}/3)")
        dr = ImageDraw.Draw(im, "RGBA")
        draw_title_block(dr, f"SECTION 04  •  ANIMATED ARCHITECTURE (STAGE {stage} OF 3)",
                         "THE INTELLIGENT AGENT LOOP: SENSE • THINK • ACT", sub_head)
        # Left photo of mobile robot with callouts
        paste_framed_photo(im, "intelligent_agent_robot.jpg", [88, 348, 980, 1068],
                           "Autonomous Mobile Robot: Cameras + LiDAR + Wheel Motors")

        # Right progressive architecture diagram [1040..2472, 348..1068]
        draw_card(dr, [1036, 348, 2472, 1068], fill=(10, 16, 32, 240), border=GOLD_DIM)

        # Nodes:
        # 1. ENVIRONMENT (left vertical pill inside diagram: 1090..1390, 430..980)
        env_active = stage in (1, 3)
        sens_active = stage >= 1
        brain_active = stage >= 2
        act_active = stage >= 3

        def node_style(active: bool, highlight_now: bool, col):
            if highlight_now:
                return (28, 46, 78, 255), col, 5
            elif active:
                return (18, 30, 54, 245), col, 3
            else:
                return (12, 18, 34, 180), (70, 82, 104), 2

        # Environment box
        f_env, b_env, w_env = node_style(True, stage == 1, CYAN)
        dr.rounded_rectangle([1084, 430, 1410, 990], radius=24, fill=f_env, outline=b_env, width=w_env)
        dr.text((1120, 470), "ENVIRONMENT", font=F_CINZEL_HERO(30), fill=CYAN if sens_active else SLATE_MUTED)
        draw_wrapped(dr, "Physical or digital world:\n• Hallways\n• Roads\n• Farm fields\n• Obstacles",
                     1120, 535, F_SANS_REG(25), IVORY if sens_active else SLATE_MUTED, 260, 12)

        # Sensors box (top-right: 1560..2416, 400..565)
        f_s, b_s, w_s = node_style(sens_active, stage == 1, GOLD_BRIGHT)
        dr.rounded_rectangle([1560, 396, 2420, 566], radius=22, fill=f_s, outline=b_s, width=w_s)
        dr.text((1596, 422), "1. SENSORS  (Eyes & Ears)", font=F_SANS_BOLD(27), fill=GOLD_BRIGHT if sens_active else SLATE_MUTED)
        dr.text((1596, 468), "Cameras  •  LiDAR  •  Microphones  •  Battery Meter",
                font=F_SANS_REG(24), fill=IVORY if sens_active else SLATE_MUTED)

        # Reasoning Engine box (middle-right: 1560..2416, 625..795)
        f_b, b_b, w_b = node_style(brain_active, stage == 2, GOLD_BRIGHT)
        dr.rounded_rectangle([1560, 625, 2420, 795], radius=22, fill=f_b, outline=b_b, width=w_b)
        dr.text((1596, 650), "2. REASONING ENGINE  (Agent Brain)", font=F_SANS_BOLD(27),
                fill=GOLD_BRIGHT if brain_active else SLATE_MUTED)
        dr.text((1596, 698), "Evaluates Percept + Goal  >>  Selects Best Action",
                font=F_SANS_REG(24), fill=IVORY if brain_active else SLATE_MUTED)

        # Actuators box (bottom-right: 1560..2416, 854..1024)
        f_a, b_a, w_a = node_style(act_active, stage == 3, EMERALD)
        dr.rounded_rectangle([1560, 854, 2420, 1024], radius=22, fill=f_a, outline=b_a, width=w_a)
        dr.text((1596, 880), "3. ACTUATORS  (Hands & Wheels)", font=F_SANS_BOLD(27),
                fill=EMERALD if act_active else SLATE_MUTED)
        dr.text((1596, 928), "Wheel Motors  •  Robotic Gripper  •  Brakes  •  Screen",
                font=F_SANS_REG(24), fill=IVORY if act_active else SLATE_MUTED)

        # Connecting arrows
        c1 = GOLD_BRIGHT if stage >= 1 else (70, 82, 104)
        dr.line([(1410, 482), (1554, 482)], fill=c1, width=5)
        dr.polygon([(1558, 482), (1536, 468), (1536, 496)], fill=c1)
        dr.text((1430, 444), "Observe", font=F_SANS_SEMI(20), fill=c1)

        c2 = GOLD_BRIGHT if stage >= 2 else (70, 82, 104)
        dr.line([(1990, 566), (1990, 620)], fill=c2, width=5)
        dr.polygon([(1990, 624), (1976, 604), (2004, 604)], fill=c2)
        dr.text((2010, 578), "Percept Data", font=F_SANS_SEMI(20), fill=c2)

        c3 = EMERALD if stage >= 3 else (70, 82, 104)
        dr.line([(1990, 795), (1990, 848)], fill=c3, width=5)
        dr.polygon([(1990, 853), (1976, 833), (2004, 833)], fill=c3)
        dr.text((2010, 808), "Chosen Action", font=F_SANS_SEMI(20), fill=c3)

        dr.line([(1560, 940), (1416, 940)], fill=c3, width=5)
        dr.polygon([(1412, 940), (1434, 926), (1434, 954)], fill=c3)
        dr.text((1434, 902), "Changes", font=F_SANS_SEMI(20), fill=c3)

        save_slide(im, slide_idx)

    render_agent_stage(8, 1, "Stage 1: Sensors capture fresh observations from the surrounding world", "Sensors")
    render_agent_stage(9, 2, "Stage 2: Percepts enter the Reasoning Engine to evaluate possible choices", "Reasoning")
    render_agent_stage(10, 3, "Stage 3: Actuators carry out the chosen action and update the world", "Actuators")

    # ------------------------------------------------------------------
    # SLIDE 11: PEAS ENGINEERING FRAMEWORK
    # ------------------------------------------------------------------
    img = make_luxury_canvas()
    draw_chrome(img, 11, total, "04 • PEAS Specification")
    d = ImageDraw.Draw(img, "RGBA")
    draw_title_block(d, "ENGINEERING DESIGN CHECKLIST", "THE P.E.A.S. FRAMEWORK FOR INTELLIGENT AGENTS",
                     "Four essential questions engineers answer before writing a single line of code")
    peas = [
        ("P", "Performance Measure", GOLD_BRIGHT, "How do we score success? (Safety, speed, accuracy, energy efficiency, passenger comfort)"),
        ("E", "Environment", CYAN, "Where does the agent work? (Roads, hallways, weather, lighting, humans, moving obstacles)"),
        ("A", "Actuators", EMERALD, "What parts perform actions? (Electric motors, steering, robotic grippers, brakes, speakers)"),
        ("S", "Sensors", TEAL, "What inputs measure the world? (Cameras, LiDAR laser scanners, radar, GPS, battery sensors)"),
    ]
    ry = 344
    for letter, word, col, desc_p in peas:
        draw_card(d, [88, ry, 2472, ry + 162], border=col)
        d.rounded_rectangle([118, ry + 24, 232, ry + 138], radius=20, fill=(*col, 35), outline=col, width=3)
        d.text((152, ry + 42), letter, font=F_CINZEL_HERO(56), fill=col)
        d.text((274, ry + 32), word, font=F_CINZEL_HERO(36), fill=IVORY)
        d.text((274, ry + 88), desc_p, font=F_SANS_REG(27), fill=SLATE_LIGHT)
        ry += 184
    save_slide(img, 11)

    # ------------------------------------------------------------------
    # SLIDE 12: WORKED EXAMPLE 1 — CAMPUS SHUTTLE PEAS
    # ------------------------------------------------------------------
    img = make_luxury_canvas()
    draw_chrome(img, 12, total, "05 • Worked Example 1")
    d = ImageDraw.Draw(img, "RGBA")
    draw_title_block(d, "SECTION 05  •  WORKED EXAMPLE 01", "DESIGNING AN AUTONOMOUS CAMPUS SHUTTLE",
                     "Applying the PEAS checklist to a real electric self-driving campus vehicle")
    paste_framed_photo(img, "autonomous_shuttle.jpg", [88, 348, 1020, 1068],
                       "Electric Autonomous Shuttle with Roof LiDAR & Cameras")
    rows = [
        ("PERFORMANCE", GOLD_BRIGHT, "100% collision-free safety, on-time stop arrival, smooth braking, obeying campus speed limits."),
        ("ENVIRONMENT", CYAN, "Campus roads, pedestrian crosswalks, students, bicycles, rain, shadows, and bright sunset glare."),
        ("ACTUATORS", EMERALD, "Electric traction motor, power steering actuator, hydraulic brakes, turn signals, cabin display."),
        ("SENSORS", TEAL, "360° roof LiDAR, stereo vision cameras, front radar, wheel encoders, and GPS receiver."),
    ]
    ry = 348
    for k, col, val in rows:
        draw_card(d, [1068, ry, 2472, ry + 164], border=col)
        d.text((1104, ry + 24), k, font=F_SANS_BOLD(23), fill=col)
        draw_wrapped(d, val, 1104, ry + 64, F_SANS_REG(26), IVORY, 1330, 8)
        ry += 184
    save_slide(img, 12)

    # ------------------------------------------------------------------
    # SLIDE 13: MATHEMATICAL UTILITY EQUATION
    # ------------------------------------------------------------------
    img = make_luxury_canvas()
    draw_chrome(img, 13, total, "05 • Mathematical Foundation")
    d = ImageDraw.Draw(img, "RGBA")
    draw_title_block(d, "MATHEMATICS IN SIMPLE ENGLISH", "HOW AGENTS SCORE CHOICES: THE UTILITY FORMULA",
                     "Turning competing goals—safety, speed, and battery energy—into one clear score")
    # Hero Equation Card
    draw_card(d, [88, 344, 2472, 610], fill=(15, 25, 48, 248), border=GOLD, accent_top=GOLD)
    eq = "U  =  ( w_s × S )  +  ( w_p × P )  −  ( w_e × E )"
    eb = d.textbbox((0, 0), eq, font=F_MONO_BOLD(62))
    d.text(((W - (eb[2] - eb[0])) // 2, 412), eq, font=F_MONO_BOLD(62), fill=GOLD_BRIGHT)
    sub_eq = "Higher Utility Score (U)  =  Better, Smarter Action for the Robot"
    sb = d.textbbox((0, 0), sub_eq, font=F_SANS_SEMI(28))
    d.text(((W - (sb[2] - sb[0])) // 2, 522), sub_eq, font=F_SANS_SEMI(28), fill=CYAN)

    vars_info = [
        ("S  &  w_s", "Safety Score (0–10)", EMERALD, "How safe the action is for people and the robot, multiplied by safety weight w_s."),
        ("P  &  w_p", "Progress / Speed (0–10)", GOLD_BRIGHT, "How quickly the action moves the robot toward its goal, multiplied by weight w_p."),
        ("E  &  w_e", "Energy Cost (0–10)", CORAL, "Battery power consumed by the action—subtracted so wasteful actions lose points."),
        ("Weights (w)", "Engineer Priorities", CYAN, "Positive numbers set by the engineer. Setting w_s = 5 makes safety top priority!"),
    ]
    vx = 88
    for sym, vtitle, col, vdesc in vars_info:
        draw_card(d, [vx, 654, vx + 566, 1072], border=col)
        d.text((vx + 32, 690), sym, font=F_MONO_BOLD(36), fill=col)
        d.text((vx + 32, 752), vtitle, font=F_SANS_BOLD(27), fill=IVORY)
        draw_wrapped(d, vdesc, vx + 32, 810, F_SANS_REG(25), SLATE_LIGHT, 502, 10)
        vx += 606
    save_slide(img, 13)

    # ------------------------------------------------------------------
    # SLIDE 14: WORKED EXAMPLE 2 — STEP-BY-STEP ROUTE ARITHMETIC
    # ------------------------------------------------------------------
    img = make_luxury_canvas()
    draw_chrome(img, 14, total, "05 • Worked Example 2")
    d = ImageDraw.Draw(img, "RGBA")
    draw_title_block(d, "WORKED EXAMPLE 02  •  STEP-BY-STEP MATH",
                     "COMPARING TWO ROBOT ROUTES WITH WEIGHTS w_s=5, w_p=3, w_e=1",
                     "Why our utility formula automatically protects human bystanders")

    # Route A Card
    draw_card(d, [88, 348, 1244, 930], border=CORAL, accent_top=CORAL)
    d.text((132, 388), "OPTION A  •  CROWDED SHORTCUT", font=F_SANS_BOLD(24), fill=CORAL)
    d.text((132, 434), "Fast, But Low Safety", font=F_CINZEL_HERO(38), fill=IVORY)
    lines_a = [
        "Ratings :  Safety S = 2  |  Speed P = 9  |  Energy E = 4",
        "Step 1  :  w_s × S  =  5 × 2  =  10",
        "Step 2  :  w_p × P  =  3 × 9  =  27",
        "Step 3  :  w_e × E  =  1 × 4  =   4",
        "Total U :  10 + 27 − 4  =  33 points",
    ]
    cy = 516
    for ln in lines_a:
        d.text((132, cy), ln, font=F_MONO_REG(26), fill=SLATE_LIGHT if "Total" not in ln else CORAL)
        cy += 68

    # Route B Card
    draw_card(d, [1316, 348, 2472, 930], border=EMERALD, accent_top=EMERALD)
    d.text((1360, 388), "OPTION B  •  CLEAR SIDE CORRIDOR   [WINNER]", font=F_SANS_BOLD(24), fill=EMERALD)
    d.text((1360, 434), "High Safety, Steady Speed", font=F_CINZEL_HERO(38), fill=GOLD_BRIGHT)
    lines_b = [
        "Ratings :  Safety S = 9  |  Speed P = 7  |  Energy E = 5",
        "Step 1  :  w_s × S  =  5 × 9  =  45",
        "Step 2  :  w_p × P  =  3 × 7  =  21",
        "Step 3  :  w_e × E  =  1 × 5  =   5",
        "Total U :  45 + 21 − 5  =  61 points  (Selected!)",
    ]
    cy = 516
    for ln in lines_b:
        d.text((1360, cy), ln, font=F_MONO_REG(26), fill=IVORY if "Total" not in ln else EMERALD)
        cy += 68

    # Score visual comparison bar at bottom
    draw_card(d, [88, 962, 2472, 1082], fill=(10, 17, 33, 240), border=GOLD_DIM)
    d.text((132, 1002), "RESULT:  Route B (61 pts)  beats  Route A (33 pts)  —  Agent chooses Safe Clear Corridor",
           font=F_SANS_BOLD(29), fill=GOLD_BRIGHT)
    save_slide(img, 14)

    # ------------------------------------------------------------------
    # SLIDE 15: SECTION COVER — PRACTICAL CODE DEMONSTRATION
    # ------------------------------------------------------------------
    img = make_luxury_canvas("vision_conveyor_lab.jpg", vignette_strength=0.86)
    draw_chrome(img, 15, total, "06 • Practical Demonstration", is_cover=True)
    d = ImageDraw.Draw(img, "RGBA")
    draw_pill(d, 130, 210, "SECTION 06  •  PRACTICAL PYTHON DEMONSTRATION")
    d.text((130, 304), "FROM EQUATION TO WORKING", font=F_CINZEL_HERO(66), fill=IVORY)
    d.text((130, 392), "ROBOT SOFTWARE", font=F_CINZEL_HERO(74), fill=GOLD_BRIGHT)
    d.line([(130, 502), (920, 502)], fill=GOLD, width=4)
    d.text((130, 540), "Building & Running warehouse_agent_demo.py Line by Line",
           font=F_SERIF_ITALIC(50), fill=IVORY)
    draw_wrapped(
        d,
        "See how 35 clean lines of Python turn sensor readings and utility math "
        "into safe, real-time warehouse robot decisions.",
        130, 636, F_SANS_REG(30), SLATE_LIGHT, 1240, 14
    )
    save_slide(img, 15)

    # ------------------------------------------------------------------
    # SLIDE 16: PYTHON CODE WALKTHROUGH
    # ------------------------------------------------------------------
    img = make_luxury_canvas()
    draw_chrome(img, 16, total, "06 • Python Code Walkthrough")
    d = ImageDraw.Draw(img, "RGBA")
    draw_title_block(d, "LIVE CODE WALKTHROUGH  •  PYTHON 3", "UTILITY-BASED WAREHOUSE ROBOT AGENT",
                     "Clean, readable Python functions connecting sensors, utility math, and action choice")

    # Left IDE window
    draw_card(d, [88, 340, 1610, 1084], fill=(9, 13, 24, 250), border=GOLD_DIM)
    d.rounded_rectangle([90, 342, 1608, 398], radius=20, fill=(18, 26, 46, 255))
    d.ellipse([118, 358, 138, 378], fill=CORAL)
    d.ellipse([150, 358, 170, 378], fill=GOLD)
    d.ellipse([182, 358, 202, 378], fill=EMERALD)
    d.text((230, 353), "warehouse_agent_demo.py", font=F_MONO_BOLD(22), fill=SLATE_LIGHT)

    code_lines = [
        ("def sense_environment(dist, battery, clear):", CYAN),
        ("    return {'dist': dist, 'bat': battery, 'clear': clear}", IVORY),
        ("", IVORY),
        ("def score_action(action, p):", CYAN),
        ("    w_s, w_p, w_e = 5.0, 3.0, 1.0  # Safety first!", GOLD_BRIGHT),
        ("    if action == 'STOP_AND_WAIT':", IVORY),
        ("        s, sp, e = (10.0 if p['dist'] < 1.5 else 6.0), 0.0, 0.5", EMERALD),
        ("    elif action == 'FAST_FORWARD':", IVORY),
        ("        ok = p['clear'] and p['dist'] > 3.0 and p['bat'] >= 20", EMERALD),
        ("        s, sp, e = (9.0 if ok else 1.0), 9.5, 4.0", EMERALD),
        ("    elif action == 'GO_CHARGE':", IVORY),
        ("        s, sp, e = 9.0, (8.0 if p['bat'] < 20 else 1.0), 1.0", EMERALD),
        ("    return round(w_s*s + w_p*sp - w_e*e, 2)", GOLD_BRIGHT),
        ("", IVORY),
        ("def choose_best_action(percept):", CYAN),
        ("    scores = {a: score_action(a, percept) for a in ACTIONS}", IVORY),
        ("    return max(scores, key=scores.get)", GOLD_BRIGHT),
    ]
    cy = 418
    for idx_l, (cl, ccol) in enumerate(code_lines, 1):
        d.text((114, cy), f"{idx_l:02d}", font=F_MONO_REG(21), fill=(90, 105, 135))
        d.text((168, cy), cl, font=F_MONO_REG(22), fill=ccol)
        cy += 38

    # Right explanation cards
    exps = [
        ("1. sense_environment()", CYAN, "Packages raw distance, battery %, and path status into a clean Python dictionary."),
        ("2. score_action()", GOLD_BRIGHT, "Computes U = 5·S + 3·P − 1·E. Blocks high speed if a person is near or battery < 20%."),
        ("3. choose_best_action()", EMERALD, "Scores every candidate action and returns the action with the highest utility."),
    ]
    ey = 340
    for et, ecol, edesc in exps:
        draw_card(d, [1650, ey, 2472, ey + 232], border=ecol)
        d.text((1684, ey + 26), et, font=F_MONO_BOLD(25), fill=ecol)
        draw_wrapped(d, edesc, 1684, ey + 78, F_SANS_REG(24), IVORY, 756, 8)
        ey += 256
    save_slide(img, 16)

    # ------------------------------------------------------------------
    # SLIDE 17: LIVE TERMINAL EXECUTION & SCORE CHART
    # ------------------------------------------------------------------
    img = make_luxury_canvas()
    draw_chrome(img, 17, total, "06 • Execution Output")
    d = ImageDraw.Draw(img, "RGBA")
    draw_title_block(d, "VERIFIED PYTHON EXECUTION", "LIVE TERMINAL OUTPUT ACROSS 3 SCENARIOS",
                     "Real output from running warehouse_agent_demo.py in our engineering workspace")

    # Left console output
    draw_card(d, [88, 344, 1340, 1076], fill=(8, 12, 22, 250), border=EMERALD)
    d.text((126, 376), "$ python3 warehouse_agent_demo.py", font=F_MONO_BOLD(24), fill=EMERALD)
    d.line([(126, 420), (1300, 420)], fill=(52, 211, 153, 90), width=2)
    term_lines = [
        ("Scenario 1: Open Corridor", GOLD_BRIGHT),
        ("  Sensors : dist=5.0m, battery=85%, clear=True", SLATE_LIGHT),
        ("  Scores  : STOP=29.5 | SLOW=55.5 | FAST=69.5 | CHARGE=47.0", IVORY),
        ("  Decision: -> FAST_FORWARD  (69.5 pts)", EMERALD),
        ("", IVORY),
        ("Scenario 2: Worker Nearby (1.1m)", GOLD_BRIGHT),
        ("  Sensors : dist=1.1m, battery=70%, clear=False", SLATE_LIGHT),
        ("  Scores  : STOP=49.5 | SLOW=23.0 | FAST=29.5 | CHARGE=47.0", IVORY),
        ("  Decision: -> STOP_AND_WAIT (49.5 pts - Human Safe!)", EMERALD),
        ("", IVORY),
        ("Scenario 3: Low Battery (14%)", GOLD_BRIGHT),
        ("  Sensors : dist=4.0m, battery=14%, clear=True", SLATE_LIGHT),
        ("  Scores  : STOP=29.5 | SLOW=55.5 | FAST=29.5 | CHARGE=68.0", IVORY),
        ("  Decision: -> GO_CHARGE     (68.0 pts - Dock Now!)", EMERALD),
    ]
    ty = 444
    for tl, tcol in term_lines:
        if tl:
            d.text((126, ty), tl, font=F_MONO_REG(22), fill=tcol)
        ty += 42

    # Right visual bar comparison card
    draw_card(d, [1388, 344, 2472, 1076], border=GOLD)
    d.text((1432, 384), "WINNING UTILITY SCORES BY SCENARIO", font=F_SANS_BOLD(26), fill=GOLD_BRIGHT)
    bars = [
        ("Open Corridor  >>  FAST_FORWARD", 69.5, EMERALD),
        ("Worker at 1.1m >>  STOP_AND_WAIT", 49.5, GOLD_BRIGHT),
        ("Battery 14%    >>  GO_CHARGE", 68.0, CYAN),
    ]
    by = 476
    for blabel, bval, bcol in bars:
        d.text((1432, by), blabel, font=F_SANS_SEMI(26), fill=IVORY)
        d.rounded_rectangle([1432, by + 48, 2412, by + 104], radius=14, fill=(20, 30, 52, 255))
        fill_w = int(980 * (bval / 80.0))
        d.rounded_rectangle([1432, by + 48, 1432 + fill_w, by + 104], radius=14, fill=bcol)
        d.text((1432 + fill_w - 130, by + 58), f"{bval:.1f}", font=F_MONO_BOLD(26), fill=BG_DEEP)
        by += 190
    save_slide(img, 17)

    # ------------------------------------------------------------------
    # SLIDE 18: GUIDED STUDENT LABORATORY EXERCISE
    # ------------------------------------------------------------------
    img = make_luxury_canvas()
    draw_chrome(img, 18, total, "07 • Guided Laboratory")
    d = ImageDraw.Draw(img, "RGBA")
    draw_title_block(d, "SECTION 07  •  HANDS-ON STUDENT LAB",
                     "LAB 01: SMART ROOM COOLING & CLEANING AGENT",
                     "Starter file: student_lab_01_smart_room_agent.py")
    tasks = [
        ("STEP 01", "Run & Observe Baseline", CYAN,
         "Execute student_lab_01_smart_room_agent.py and inspect how the agent chooses between COOL_HIGH, ECO_FAN, VACUUM_FLOOR, and DOCK_AND_CHARGE."),
        ("STEP 02", "Tune Priority Weights", GOLD_BRIGHT,
         "Modify w_comfort, w_clean, and w_energy inside score_room_action() so battery below 25% always prioritizes DOCK_AND_CHARGE safely."),
        ("STEP 03", "Add Quiet Study Scenario", EMERALD,
         "Add a 5th test case with temp_c = 31.0 and quiet_mode = True, and verify the agent selects quiet ECO_FAN instead of loud vacuuming."),
    ]
    tx = 88
    for st_num, st_title, col, st_desc in tasks:
        draw_card(d, [tx, 352, tx + 756, 1068], border=col, accent_top=col)
        draw_pill(d, tx + 36, 396, st_num, fg=col, border=col)
        d.text((tx + 36, 474), st_title, font=F_CINZEL_HERO(36), fill=IVORY)
        draw_wrapped(d, st_desc, tx + 36, 554, F_SANS_REG(27), SLATE_LIGHT, 684, 14)
        tx += 794
    save_slide(img, 18)

    # ------------------------------------------------------------------
    # SLIDE 19: REAL-WORLD AI APPLICATIONS
    # ------------------------------------------------------------------
    img = make_luxury_canvas()
    draw_chrome(img, 19, total, "08 • Real-World Applications")
    d = ImageDraw.Draw(img, "RGBA")
    draw_title_block(d, "SECTION 08  •  INDUSTRY IMPACT", "REAL-WORLD INTELLIGENT AGENTS TODAY",
                     "Every modern AI industry uses the exact same Sense • Think • Act architecture")
    apps = [
        ("HEALTHCARE DIAGNOSTICS", GOLD_BRIGHT,
         "Sense: Digital X-ray & MRI scans\nThink: Pattern detection neural model\nAct: Highlight early warning regions for doctors"),
        ("PRECISION AGRICULTURE", EMERALD,
         "Sense: Crop leaf cameras & soil moisture probes\nThink: Plant health & water utility model\nAct: Target-water individual plants without waste"),
        ("SMART MANUFACTURING", CYAN,
         "Sense: High-speed overhead optical cameras\nThink: Millimeter defect classification\nAct: Precision robotic arm sorts faulty circuit boards"),
        ("AUTONOMOUS LOGISTICS", TEAL,
         "Sense: 3D LiDAR, stereo vision, wheel encoders\nThink: Real-time obstacle & battery scoring\nAct: Smooth steering, braking, and auto-charging"),
    ]
    aboxes = [(88, 344, 1252, 688), (1308, 344, 2472, 688), (88, 724, 1252, 1068), (1308, 724, 2472, 1068)]
    for (atitle, col, adesc), box in zip(apps, aboxes):
        draw_card(d, box, border=col, accent_top=col)
        d.text((box[0] + 36, box[1] + 36), atitle, font=F_CINZEL_HERO(32), fill=col)
        cy = box[1] + 104
        for line in adesc.split("\n"):
            d.text((box[0] + 36, cy), line, font=F_SANS_REG(26), fill=IVORY)
            cy += 64
    save_slide(img, 19)

    # ------------------------------------------------------------------
    # SLIDE 20: COMMON MISTAKES BEGINNERS MAKE
    # ------------------------------------------------------------------
    img = make_luxury_canvas()
    draw_chrome(img, 20, total, "09 • Common Mistakes")
    d = ImageDraw.Draw(img, "RGBA")
    draw_title_block(d, "SECTION 09  •  ENGINEERING PITFALLS", "FOUR COMMON MISTAKES TO AVOID IN AI",
                     "Practical habits that separate reliable engineers from beginners")
    mistakes = [
        ("MISTAKE 01: Confusing Memorization with Intelligence",
         "Fix: Always test AI systems on brand-new real-world situations they did not memorize."),
        ("MISTAKE 02: Assuming Sensors Are Always Perfect",
         "Fix: Design agents to handle camera glare, rain, dust, and missing readings safely."),
        ("MISTAKE 03: Over-Engineering Simple Problems",
         "Fix: Never use a giant neural network when five clear rules work faster and safer."),
        ("MISTAKE 04: Forgetting Hard Physical Safety Limits",
         "Fix: Always include strict emergency stop rules whenever humans are nearby."),
    ]
    my = 344
    for mtitle, mfix in mistakes:
        draw_card(d, [88, my, 2472, my + 162], border=CORAL)
        d.text((128, my + 28), mtitle, font=F_SANS_BOLD(29), fill=CORAL)
        d.text((128, my + 86), mfix, font=F_SANS_SEMI(26), fill=EMERALD)
        my += 184
    save_slide(img, 20)

    # ------------------------------------------------------------------
    # SLIDES 21 & 22: KNOWLEDGE CHECK (QUESTIONS -> MORPH TO ANSWERS)
    # ------------------------------------------------------------------
    def render_quiz_slide(slide_idx: int, show_answers: bool):
        im = make_luxury_canvas()
        tag = "10 • Knowledge Check" if not show_answers else "10 • Verified Answers"
        draw_chrome(im, slide_idx, total, tag)
        dr = ImageDraw.Draw(im, "RGBA")
        draw_title_block(
            dr,
            "SECTION 10  •  INTERACTIVE KNOWLEDGE CHECK",
            "TEST YOUR UNDERSTANDING" if not show_answers else "KNOWLEDGE CHECK — VERIFIED ANSWERS",
            "Pause and think through each engineering question" if not show_answers else "Review how each concept works in simple words"
        )
        qas = [
            ("Q1", "Is a factory welding inspection camera an example of Narrow AI or General AI?",
             "ANSWER: Narrow AI — because it excels at one focused visual inspection job."),
            ("Q2", "In the PEAS framework, is a robot wheel motor classified as a Sensor or an Actuator?",
             "ANSWER: Actuator — because it produces physical movement in the environment."),
            ("Q3", "In U = w_s·S + w_p·P − w_e·E, what happens to U if Energy cost (E) increases?",
             "ANSWER: Utility Score U goes DOWN — because energy cost is subtracted in the formula."),
        ]
        qy = 348
        for qnum, qtext, atext in qas:
            bcol = GOLD if not show_answers else EMERALD
            draw_card(dr, [88, qy, 2472, qy + 216], border=bcol, accent_top=bcol)
            dr.rounded_rectangle([124, qy + 36, 224, qy + 124], radius=18, fill=(*bcol, 35), outline=bcol, width=2)
            dr.text((146, qy + 56), qnum, font=F_CINZEL_HERO(36), fill=bcol)
            dr.text((260, qy + 42), qtext, font=F_SANS_BOLD(29), fill=IVORY)
            if show_answers:
                dr.text((260, qy + 118), atext, font=F_SANS_BOLD(28), fill=EMERALD)
            else:
                dr.text((260, qy + 118), "Think about your answer before we reveal the solution...",
                        font=F_SANS_REG(25), fill=GOLD_BRIGHT)
            qy += 242
        save_slide(im, slide_idx)

    render_quiz_slide(21, show_answers=False)
    render_quiz_slide(22, show_answers=True)

    # ------------------------------------------------------------------
    # SLIDE 23: MODULE 01 PRACTICAL ASSIGNMENT
    # ------------------------------------------------------------------
    img = make_luxury_canvas()
    draw_chrome(img, 23, total, "11 • Module Assignment")
    d = ImageDraw.Draw(img, "RGBA")
    draw_title_block(d, "SECTION 11  •  PRACTICAL ENGINEERING ASSIGNMENT",
                     "DESIGN AN AUTONOMOUS GREENHOUSE WATERING ROBOT",
                     "Apply both the PEAS design checklist and Python utility scoring on your own")
    draw_card(d, [88, 352, 1248, 1068], border=GOLD, accent_top=GOLD)
    d.text((132, 398), "PART A  •  SYSTEM SPECIFICATION", font=F_SANS_BOLD(24), fill=GOLD_BRIGHT)
    d.text((132, 444), "Complete PEAS Table", font=F_CINZEL_HERO(38), fill=IVORY)
    pa_items = [
        "• List at least 3 Performance goals (healthy crops, water saving, safe motion)",
        "• Describe 4 Environment conditions (humidity, heat, plant rows, workers)",
        "• Specify 3 Actuators (water valve, shade roof motor, wheel drive)",
        "• Specify 4 Sensors (soil moisture probe, leaf camera, tank sensor, thermometer)",
    ]
    cy = 532
    for it in pa_items:
        cy = draw_wrapped(d, it, 132, cy, F_SANS_REG(27), SLATE_LIGHT, 1056, 10) + 18

    draw_card(d, [1312, 352, 2472, 1068], border=CYAN, accent_top=CYAN)
    d.text((1356, 398), "PART B  •  PYTHON IMPLEMENTATION", font=F_SANS_BOLD(24), fill=CYAN)
    d.text((1356, 444), "Greenhouse Utility Agent", font=F_CINZEL_HERO(38), fill=IVORY)
    pb_items = [
        "• Read 3 sensor inputs: soil_moisture, sunlight_level, and tank_level",
        "• Score 4 actions: WATER_PLANTS, OPEN_SHADE_ROOF, REFILL_TANK, STANDBY",
        "• Choose wise positive weights and print scores across 4 realistic test scenarios",
        "• Verify the robot refills its tank before running dry!",
    ]
    cy = 532
    for it in pb_items:
        cy = draw_wrapped(d, it, 1356, cy, F_SANS_REG(27), IVORY, 1056, 10) + 18
    save_slide(img, 23)

    # ------------------------------------------------------------------
    # SLIDE 24: LUXURY CLOSING COVER & MODULE SUMMARY
    # ------------------------------------------------------------------
    img = make_luxury_canvas("cover_robotics_lab.jpg", vignette_strength=0.90)
    draw_chrome(img, 24, total, "12 • Module Summary", is_cover=True)
    d = ImageDraw.Draw(img, "RGBA")
    draw_pill(d, 130, 146, "SECTION 12  •  MODULE 01 COMPLETE SUMMARY")
    d.text((130, 224), "KEY TAKEAWAYS & NEXT MODULE", font=F_CINZEL_HERO(60), fill=GOLD_BRIGHT)
    takeaways = [
        ("01", "AI Defined Clearly", "Machines that observe, score choices, learn from data, and act safely."),
        ("02", "Capabilities & Schools", "Today's real systems are Narrow AI built with Hybrid rules, probability & neural nets."),
        ("03", "Agents & PEAS", "Every intelligent system links Sensors >> Reasoning >> Actuators inside an Environment."),
        ("04", "Math to Python", "Utility equation U = w_s·S + w_p·P − w_e·E turns priorities into working robot code."),
    ]
    boxes_s = [(130, 336, 1250, 560), (1310, 336, 2430, 560), (130, 592, 1250, 816), (1310, 592, 2430, 816)]
    for (num, h_s, b_s), bx in zip(takeaways, boxes_s):
        draw_card(d, bx, fill=(10, 17, 34, 235), border=GOLD)
        d.text((bx[0] + 32, bx[1] + 28), f"{num}  •  {h_s}", font=F_SANS_BOLD(28), fill=GOLD_BRIGHT)
        draw_wrapped(d, b_s, bx[0] + 32, bx[1] + 84, F_SANS_REG(25), IVORY, 1050, 8)

    # Next Module Banner
    draw_card(d, [130, 864, 2430, 1056], fill=(16, 29, 54, 245), border=CYAN, accent_top=CYAN)
    d.text((174, 898), "COMING NEXT IN AI.101  •  MODULE 02", font=F_SANS_BOLD(23), fill=CYAN)
    d.text((174, 944), "Problem Solving & Search Algorithms: Planning Multi-Step Robot Routes",
           font=F_CINZEL_HERO(38), fill=IVORY)
    save_slide(img, 24)

    return paths


if __name__ == "__main__":
    slides = render_all_slides(".cache/slides/ai101_m01")
    print(f"Rendered {len(slides)} slides successfully.")
