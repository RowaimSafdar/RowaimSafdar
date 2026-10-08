"""Builds dark_mode.svg and light_mode.svg: ASCII portrait (from photo.png) + neofetch-style info.

Edit PROFILE / STATS below, then run:  python build_cards.py [--photo photo.png]
Stats numbers start as 0; update_stats.py fills them in (locally or via the GitHub Action).
"""
import argparse
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageOps

LINE_CHARS = 64  # every info line is exactly this many characters, so values share one right edge

PROFILE = [
    ("header", "rowaim@safdar"),
    ("kv", "OS", "Windows, Linux Ubuntu, CentOS"),
    ("kv", "Host", "Nysonian Inc."),
    ("kv", "Kernel", "AI Automation Engineer"),
    ("kv", "IDE", "VS Code, Claude Code, Cursor, Antigravity"),
    ("blank",),
    ("kv", "Languages.Programming", "Python, SQL, Bash"),
    ("kv", "Languages.Computer", "JSON, YAML, Markdown"),
    ("kv", "Languages.Real", "English, Urdu, Pashto"),
    ("blank",),
    ("kv", "Hobbies.Software", "AI Agents, Automation"),
    ("kv", "Hobbies.Hardware", "Football, Bike Travel, Nature Exploring"),
    ("blank",),
    ("section", "Contact"),
    ("kv", "Email", "rowaimsafdar@gmail.com"),
    ("kv", "LinkedIn", "rowaimsafdar"),
    ("kv", "GitHub", "RowaimSafdar"),
    ("kv", "Location", "Islamabad, Pakistan"),
    # GitHub stats are off for now. To bring them back, restore these lines and rebuild;
    # update_stats.py and the workflow pick them up automatically.
    # ("blank",),
    # ("section", "GitHub Stats"),
    # ("stats", ("repos", "Repos"), ("contributed", "Contributed")),
    # ("stats", ("stars", "Stars"), ("followers", "Followers")),
    # ("stats", ("commits", "Commits (1y)"), ("contributions", "Contributions (1y)")),
]

THEMES = {
    "dark": dict(bg="#06111D", border="#1B2A3A", key="#7BE0B8", value="#4CB8F5",
                 dots="#3A4B5C", head="#E8F1F6", art="#98ABBB"),
    "light": dict(bg="#F6F8FA", border="#D0D7DE", key="#0E7A5A", value="#1A78B8",
                  dots="#9AA7B3", head="#1F2328", art="#57606A"),
}

WIDTH, HEIGHT = 985, 530
FONT = "ConsolasFallback, Consolas, 'Courier New', monospace"
TEXT_SIZE, TEXT_LINE = 15, 20.5
ART_SIZE, ART_LINE = 10, 12
ART_COLS = 48
RAMP = " .:-=+*#%@"  # light -> dense
TEXT_X = 345
LEFT_COL, RIGHT_COL = 30, 31  # stats columns: LEFT_COL + " | " + RIGHT_COL == LINE_CHARS


def portrait_rows(photo: Path | None, dense_is_bright: bool, crop: tuple | None = None) -> list[str]:
    img = ImageOps.exif_transpose(Image.open(photo) if photo else _placeholder()).convert("RGBA")
    if crop:
        img = img.crop(crop)
    img = ImageOps.fit(img, (600, 800), centering=(0.5, 0.35))  # 3:4, biased to the face
    # characters are ~0.6 wide per 1.18 tall, so squash rows to keep the face's proportions
    rows = round(ART_COLS * (800 / 600) * (0.6 * ART_SIZE / ART_LINE))
    # Transparent pixels (a background-removed PNG) become blank in both themes;
    # without this, inverting the ramp for light mode turns a dark background into a solid block.
    alpha = img.getchannel("A")
    # Stretch contrast using only the upper part of the subject (the head), so the face gets the
    # full character range instead of sharing it with clothing.
    head = alpha.point(lambda a: 255 if a > 127 else 0)
    head.paste(0, (0, int(img.height * 0.6), img.width, img.height))
    gray = ImageOps.autocontrast(img.convert("L"), cutoff=1, mask=head)
    gray = gray.resize((ART_COLS, rows), Image.LANCZOS)
    alpha = alpha.resize((ART_COLS, rows), Image.LANCZOS)
    out = []
    for y in range(rows):
        line = ""
        for x in range(ART_COLS):
            if alpha.getpixel((x, y)) < 128:
                line += " "
                continue
            b = gray.getpixel((x, y)) / 255
            level = b if dense_is_bright else 1 - b
            ramp = RAMP[1:]  # never a space on the subject, so dark clothing still shows its outline
            line += ramp[min(int(level * len(ramp)), len(ramp) - 1)]
        out.append(line.rstrip())
    return out


def _placeholder() -> Image.Image:
    from PIL import ImageDraw, ImageFilter
    shade = Image.new("L", (600, 800), 0)
    d = ImageDraw.Draw(shade)
    d.ellipse((170, 120, 430, 460), fill=220)
    d.rectangle((255, 430, 345, 540), fill=170)
    d.ellipse((40, 500, 560, 1000), fill=130)
    shade = shade.filter(ImageFilter.GaussianBlur(14))
    img = Image.merge("RGBA", (shade, shade, shade, shade.point(lambda v: 255 if v > 40 else 0)))
    return img


def kv_parts(key: str, value: str, width: int, value_id: str | None = None):
    prefix = f". {key}:"
    dots = width - len(prefix) - len(value) - 2
    if dots < 1:
        raise ValueError(f"'{key}: {value}' is too long for {width} chars")
    parts = [("dots", ". "), ("key", f"{key}:"), ("dots", " " + "." * dots + " ", f"{value_id}_dots" if value_id else None),
             ("value", value, f"{value_id}_data" if value_id else None)]
    return parts


def line_parts(item):
    kind = item[0]
    if kind == "header":
        return [("head", item[1]), ("dots", " " + "-" * (LINE_CHARS - len(item[1]) - 1))]
    if kind == "section":
        return [("dots", "- "), ("head", item[1]), ("dots", " " + "-" * (LINE_CHARS - len(item[1]) - 3))]
    if kind == "blank":
        return [("dots", ".")]
    if kind == "kv":
        return kv_parts(item[1], item[2], LINE_CHARS)
    if kind == "stats":
        (lid, lkey), (rid, rkey) = item[1], item[2]
        left = kv_parts(lkey, "0", LEFT_COL, lid)
        right = kv_parts(rkey, "0", RIGHT_COL + 2, rid)[1:]  # drop the leading ". " for the right column
        return left + [("dots", " | ")] + right
    raise ValueError(kind)


def build(theme: str, art: list[str]) -> str:
    c = THEMES[theme]
    art_top = (HEIGHT - len(art) * ART_LINE) / 2 + ART_SIZE
    text_top = (HEIGHT - len(PROFILE) * TEXT_LINE) / 2 + TEXT_SIZE - 4
    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" font-family="{FONT}">',
        "<style>",
        f".key{{fill:{c['key']}}} .value{{fill:{c['value']}}} .dots{{fill:{c['dots']}}} .head{{fill:{c['head']}}}",
        "</style>",
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="15" fill="{c["bg"]}" stroke="{c["border"]}"/>',
        f'<text x="25" y="{art_top:.1f}" font-size="{ART_SIZE}" fill="{c["art"]}">',
    ]
    for i, row in enumerate(art):
        # non-breaking spaces: browsers collapse ordinary leading spaces in SVG text, which skews the portrait
        o.append(f'<tspan x="25" y="{art_top + i * ART_LINE:.1f}">{escape(row).replace(" ", "&#160;")}</tspan>')
    o.append("</text>")
    o.append(f'<text x="{TEXT_X}" y="{text_top:.1f}" font-size="{TEXT_SIZE}">')
    for i, item in enumerate(PROFILE):
        spans = []
        parts = line_parts(item)
        for j, part in enumerate(parts):
            cls, text = part[0], part[1]
            pid = f' id="{part[2]}"' if len(part) > 2 and part[2] else ""
            if pid and part[2].endswith("_dots"):
                # fixed width of dots + value, so update_stats.py can re-pad as numbers change
                pid += f' data-w="{len(text) + len(parts[j + 1][1])}"'
            spans.append(f'<tspan class="{cls}"{pid}>{escape(text)}</tspan>')
        o.append(f'<tspan x="{TEXT_X}" y="{text_top + i * TEXT_LINE:.1f}">{"".join(spans)}</tspan>')
    o += ["</text>", "</svg>", ""]
    return "\n".join(o)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--photo", default="photo.png", help="ideally a background-removed PNG")
    ap.add_argument("--crop", help="left,top,right,bottom in pixels, to frame head and shoulders")
    args = ap.parse_args()
    photo = Path(args.photo)
    if not photo.exists():
        print(f"{photo} not found, using a placeholder silhouette")
        photo = None
    crop = tuple(int(v) for v in args.crop.split(",")) if args.crop else None
    for theme, dense_is_bright in (("dark", True), ("light", False)):
        art = portrait_rows(photo, dense_is_bright, crop)
        Path(f"{theme}_mode.svg").write_text(build(theme, art), encoding="utf-8")
        print(f"wrote {theme}_mode.svg ({len(art)} portrait rows)")


if __name__ == "__main__":
    main()
