#!/usr/bin/env python3
"""Build a single self-contained offline HTML from part1/2/3.

Merges the three part pages into one portable file with:
  - one shared <head> (identical CSS across parts) + a small additive block
  - one global sticky progress bar + jump-nav (Part 1 / 2 / 3)
  - each part's original masthead reused as a full-width section divider
  - each part's step content dropped in verbatim (copy buttons intact)
  - one unified <script> (from the shared template) counting ALL steps,
    with its own localStorage key so it never clashes with the hosted pages

The copy buttons keep working offline (file://) because the script falls back
to document.execCommand("copy") when navigator.clipboard is unavailable.

Re-run after any content edit:  python tools/build_offline.py
"""
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PARTS = ["part1.html", "part2.html", "part3.html"]
OUT = ROOT / "offline-build-guide.html"

TITLE = "Third-Party Application Declaration — Complete Build Guide (Parts 1–3)"

EXTRA_CSS = """
  /* --- offline single-file additions --- */
  .jump{display:flex;flex-wrap:wrap;gap:8px;padding:6px 0 9px}
  .jump a{font-family:"IBM Plex Mono",monospace;font-size:15px;text-decoration:none;color:var(--navy);border:1px solid var(--line);border-radius:999px;padding:4px 12px;background:#fff}
  .jump a:active{background:var(--line-soft)}
  header.mast.partsep{scroll-margin-top:64px;margin-top:6px}
  section.partmain{padding-top:8px}
"""

OVERALL_MAST = """<header class="mast">
  <div class="wrap mast-inner">
    <div class="brandmark" aria-hidden="true">
      <svg viewBox="0 0 48 48" width="46" height="46" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="24" cy="24" r="16" stroke="rgba(255,255,255,.5)" stroke-width="1.8"/>
        <path d="M16 24l6 6 11-13" stroke="rgba(224,138,30,.95)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <div class="mast-copy">
      <p class="kicker">3rd-Party Declarations · Offline copy</p>
      <h1>Complete Build Guide</h1>
      <p class="sub">All three parts in one file. Works offline — copy buttons included. Your progress is saved on this device.</p>
    </div>
  </div>
</header>"""


def read(name):
    return (ROOT / name).read_text(encoding="utf-8")


def slice_between(text, start_marker, end_marker, start_from=0):
    a = text.index(start_marker, start_from)
    b = text.index(end_marker, a + len(start_marker))
    return text[a:b + len(end_marker)], b


def main():
    base = read(PARTS[0])

    # Shared head: everything up to and including </head>, retitled, +extra CSS.
    head = base[: base.index("</head>")]
    head = re.sub(r"<title>.*?</title>", f"<title>{TITLE}</title>", head, count=1, flags=re.S)
    head = head.replace("</style>", EXTRA_CSS + "</style>", 1)

    # Shared script: reuse the part's <script> block, but give it a fresh key so
    # offline progress is independent of the hosted pages.
    script, _ = slice_between(base, "<script>", "</script>")
    script = re.sub(r'var KEY="[^"]*";', 'var KEY="bbk3pDeclareOffline_v1";', script, count=1)

    sections = []
    for i, name in enumerate(PARTS, 1):
        text = read(name)
        mast, mast_end = slice_between(text, '<header class="mast">', "</header>")
        # step content = inside <main class="wrap"> up to the page footer
        main_open = text.index('<main class="wrap">') + len('<main class="wrap">')
        footer_at = text.index("<footer>", main_open)
        content = text[main_open:footer_at].strip()

        # tag the masthead as an anchor + divider
        mast = mast.replace('<header class="mast">', f'<header class="mast partsep" id="part{i}">', 1)
        sections.append(f"{mast}\n<section class=\"wrap partmain\">\n{content}\n</section>")

    body_sections = "\n\n".join(sections)

    footer = (
        '<footer class="wrap">Third-Party Application Declaration — offline build guide. '
        "Parts 1–3 combined. Formulas copy exactly as written; paste, never retype.</footer>"
    )

    html = f"""{head}</head>
<body>

{OVERALL_MAST}

<div class="sticky">
  <div class="wrap">
    <div class="progress"><i id="bar"></i></div>
    <div class="progtext"><span id="progLabel">0 steps done</span><button id="reset" type="button">Reset</button></div>
    <nav class="jump"><a href="#part1">Part 1 · Foundations</a><a href="#part2">Part 2 · Validation</a><a href="#part3">Part 3 · Submit &amp; ship</a></nav>
  </div>
</div>

{body_sections}

{footer}

<script>
{script[len("<script>"):-len("</script>")]}
</script>
</body>
</html>
"""
    OUT.write_text(html, encoding="utf-8")

    steps = html.count('<details class="step"')
    copy = html.count('class="copy"')
    chips = html.count('class="cc"')
    bars = html.count('id="bar"')
    gates = html.count('gate.js')
    print(f"wrote {OUT.name}: {len(html)//1024} KB")
    print(f"  steps (details.step): {steps}")
    print(f"  copy buttons: {copy}   tap-to-copy chips: {chips}")
    print(f"  #bar occurrences: {bars} (want 1)")
    print(f"  gate.js references: {gates} (want 0)")


if __name__ == "__main__":
    main()
