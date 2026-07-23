#!/usr/bin/env python3
"""Render offline-build-guide.html to a print-clean PDF.

Why this exists: the guide's copy buttons can't work in a PDF, and its 28 steps
are collapsed <details> that headless Chrome will NOT expand for print -- so a
naive print-to-pdf silently drops 27 of 28 steps. This script fixes both:
forces every <details> open and injects a print stylesheet, then renders with a
headless Chromium.

Usage:  python tools/build_pdf.py
Output: Power-Apps-Build-Guide.pdf  (repo root)

Notes:
- Prefers Edge, then Chrome. A running Chrome with the SAME default profile will
  hijack the launch ("Opening in existing browser session") and print nothing,
  so we always pass an isolated --user-data-dir.
- Serves over http on a throwaway port because file:// print is flaky on Windows.
"""
import http.server
import pathlib
import re
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "offline-build-guide.html"
OUT = ROOT / "Power-Apps-Build-Guide.pdf"
PORT = 8791

PRINT_CSS = """<style media="print">
@page { size: A4; margin: 14mm 12mm; }
@media print {
  .sticky, .copy, #reset, nav.jump { display: none !important; }
  * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
  html, body { background:#fff !important; }
  details.step { display: block !important; }
  details.step > summary { list-style: none; cursor: default; }
  details.step > summary::-webkit-details-marker { display: none; }
  details.step > summary .chev, .chev { display: none !important; }
  .fx code { padding-right: 16px !important; }
  .fx, .do, .dot { break-inside: avoid; }
  h1,h2,h3,h4 { break-after: avoid; }
  header.mast.partsep { break-before: page; }
  a[href^="#"] { color: inherit !important; text-decoration: none !important; }
  .step { box-shadow: none !important; }
}
</style>
"""

CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def find_browser():
    for c in CANDIDATES:
        if pathlib.Path(c).exists():
            return c
    sys.exit("No Edge/Chrome found. Edit CANDIDATES in this script.")


def build_print_html(workdir):
    src = SRC.read_text(encoding="utf-8")

    def force_open(m):
        tag = m.group(0)
        return tag if re.search(r"\bopen\b", tag) else tag[:-1] + " open>"

    src = re.sub(r"<details\b[^>]*>", force_open, src)
    n = len(re.findall(r"<details\b", src))
    assert "</head>" in src, "no </head> in source"
    src = src.replace("</head>", PRINT_CSS + "</head>", 1)
    dest = workdir / "guide-print.html"
    dest.write_text(src, encoding="utf-8")
    print(f"  forced {n} <details> open, injected print CSS")
    return dest


def serve(workdir):
    handler = lambda *a, **k: http.server.SimpleHTTPRequestHandler(
        *a, directory=str(workdir), **k
    )
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def main():
    if not SRC.exists():
        sys.exit(f"Missing {SRC}. Run tools/build_offline.py first.")
    browser = find_browser()
    print(f"Browser: {browser}")
    workdir = pathlib.Path(tempfile.mkdtemp(prefix="pdfbuild_"))
    profile = workdir / "profile"
    try:
        build_print_html(workdir)
        httpd = serve(workdir)
        if OUT.exists():
            OUT.unlink()
        cmd = [
            browser, "--headless=new", "--disable-gpu", "--no-sandbox",
            f"--user-data-dir={profile}", "--no-pdf-header-footer",
            f"--print-to-pdf={OUT}",
            f"http://127.0.0.1:{PORT}/guide-print.html",
        ]
        subprocess.run(cmd, timeout=120,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        httpd.shutdown()
        if not OUT.exists() or OUT.stat().st_size < 10_000:
            sys.exit("PDF was not produced. Is a browser with the default "
                     "profile already running? See module docstring.")
        data = OUT.read_bytes()
        pages = len(re.findall(rb"/Type\s*/Page[^s]", data))
        print(f"Wrote {OUT.name}: {pages} pages, {len(data)//1024} KB")
        if pages < 40:
            print("WARNING: fewer pages than expected (~68). Steps may not have "
                  "expanded -- check the <details> forcing logic.")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    main()
