"""Everything shown on the profile card, in one place: text, colors and geometry.

Edit this file, then run `python generate_svg.py` to rebuild dark_mode.svg and light_mode.svg.
"""

PROFILE = [
    ("header", "rowaim@safdar"),
    ("kv", "OS", "Windows, Linux Ubuntu"),
    ("kv", "Host", "Nysonian Inc."),
    ("kv", "Kernel", "AI Automation Engineer"),
    ("kv", "IDE", "Claude Code, Cursor"),
    ("blank",),
    ("kv", "Languages.Programming", "Python, SQL, Bash"),
    ("kv", "Languages.Computer", "JSON, YAML, Markdown"),
    ("kv", "Languages.Real", "English, Urdu"),
    ("blank",),
    ("kv", "Hobbies.Software", "AI Agents, Automation"),
    ("kv", "Hobbies.Hardware", "Bike Travel, Nature Exploring"),
    ("blank",),
    ("section", "Contact"),
    ("kv", "Email", "rowaimsafdar@gmail.com"),
    ("kv", "Website", "rowaimsafdar.vercel.app"),
    ("kv", "LinkedIn", "rowaimsafdar"),
    ("kv", "GitHub", "RowaimSafdar"),
    ("kv", "Location", "Islamabad, Pakistan"),
    # GitHub stats are off for now. To bring them back, uncomment these lines and run
    # generate_svg.py; today.py and the daily workflow then fill in the numbers.
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

# Geometry (Consolas with size-adjust 109%: a character is 0.55 * 1.09 * font-size wide)
WIDTH, HEIGHT = 985, 530
FONT = "ConsolasFallback, Consolas, 'Courier New', monospace"
LINE_CHARS = 64            # every info line is exactly this many characters, so values share one right edge
TEXT_X = 390               # 64 chars at 15px is ~576px, so lines end at ~966
TEXT_SIZE, TEXT_LINE = 15, 20.5
ART_X = 15
ART_SIZE, ART_LINE = 6, 7.5  # ~3.6px wide characters: 100 columns fill the 360px left panel
ART_ROWS, ART_COLS = 62, 100  # the portrait is resampled to exactly this many characters
LEFT_COL, RIGHT_COL = 30, 31  # stats columns: LEFT_COL + " | " + RIGHT_COL == LINE_CHARS

# ascii-art.txt holds a high-resolution dark-mode portrait (dense characters = bright pixels,
# space = background); generate_svg.py zooms it to ART_ROWS and centre-crops it to ART_COLS.
# The light card mirrors this ramp so the face still reads correctly on a light background.
ART_RAMP = " .:-=+*#%@"
