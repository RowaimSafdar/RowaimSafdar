"""Builds dark_mode.svg and light_mode.svg from ascii-art.txt and layout.py.

Run:  python generate_svg.py
Stats values start as 0; today.py fills them in (locally or via the daily GitHub Action).
"""
from pathlib import Path
from xml.sax.saxutils import escape

from layout import (ART_LINE, ART_RAMP, ART_SIZE, ART_X, FONT, HEIGHT, LEFT_COL, LINE_CHARS, PROFILE,
                    RIGHT_COL, TEXT_LINE, TEXT_SIZE, TEXT_X, THEMES, WIDTH)

ROOT = Path(__file__).resolve().parent


def load_art(theme: str) -> list[str]:
    rows = (ROOT / "ascii-art.txt").read_text(encoding="utf-8").rstrip("\n").split("\n")
    if theme == "dark":
        return [r.rstrip() for r in rows]
    mirror = {c: ART_RAMP[len(ART_RAMP) - 1 - i] for i, c in enumerate(ART_RAMP)}
    return ["".join(mirror.get(c, c) for c in r).rstrip() for r in rows]


def kv_parts(key: str, value: str, width: int, value_id: str | None = None) -> list[tuple]:
    prefix = f". {key}:"
    dots = width - len(prefix) - len(value) - 2
    if dots < 1:
        raise ValueError(f"'{key}: {value}' is too long for {width} characters")
    return [("dots", ". "), ("key", f"{key}:"),
            ("dots", " " + "." * dots + " ", f"{value_id}_dots" if value_id else None),
            ("value", value, f"{value_id}_data" if value_id else None)]


def line_parts(item: tuple) -> list[tuple]:
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
        right = kv_parts(rkey, "0", RIGHT_COL + 2, rid)[1:]  # the right column has no leading ". "
        return left + [("dots", " | ")] + right
    raise ValueError(f"unknown line type {kind!r}")


def build(theme: str) -> str:
    c, art = THEMES[theme], load_art(theme)
    art_top = (HEIGHT - len(art) * ART_LINE) / 2 + ART_SIZE
    text_top = (HEIGHT - len(PROFILE) * TEXT_LINE) / 2 + TEXT_SIZE - 4
    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" font-family="{FONT}">',
        "<style>",
        f".key{{fill:{c['key']}}} .value{{fill:{c['value']}}} .dots{{fill:{c['dots']}}} .head{{fill:{c['head']}}}",
        "</style>",
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="15" fill="{c["bg"]}" stroke="{c["border"]}"/>',
        f'<text x="{ART_X}" y="{art_top:.1f}" font-size="{ART_SIZE}" fill="{c["art"]}">',
    ]
    for i, row in enumerate(art):
        # Non-breaking spaces: browsers collapse ordinary leading spaces in SVG text, which skews the portrait.
        o.append(f'<tspan x="{ART_X}" y="{art_top + i * ART_LINE:.1f}">{escape(row).replace(" ", "&#160;")}</tspan>')
    o.append("</text>")
    o.append(f'<text x="{TEXT_X}" y="{text_top:.1f}" font-size="{TEXT_SIZE}">')
    for i, item in enumerate(PROFILE):
        parts, spans = line_parts(item), []
        for j, part in enumerate(parts):
            cls, text = part[0], part[1]
            pid = f' id="{part[2]}"' if len(part) > 2 and part[2] else ""
            if pid and part[2].endswith("_dots"):
                # Fixed width of dots + value, so today.py can re-pad the line as numbers change.
                pid += f' data-w="{len(text) + len(parts[j + 1][1])}"'
            spans.append(f'<tspan class="{cls}"{pid}>{escape(text)}</tspan>')
        o.append(f'<tspan x="{TEXT_X}" y="{text_top + i * TEXT_LINE:.1f}">{"".join(spans)}</tspan>')
    o += ["</text>", "</svg>", ""]
    return "\n".join(o)


def main() -> None:
    for theme in ("dark", "light"):
        (ROOT / f"{theme}_mode.svg").write_text(build(theme), encoding="utf-8")
        print(f"wrote {theme}_mode.svg")


if __name__ == "__main__":
    main()
