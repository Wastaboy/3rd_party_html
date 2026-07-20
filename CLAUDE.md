# Project rules

- **No password gate:** pages in this repo must NOT load `gate.js`. The
  password curtain plus this guide's account/bank/O365 vocabulary got the site
  classified as phishing by Zscaler (2026-07-20) — see
  `docs/superpowers/specs/2026-07-20-zscaler-deflag-design.md`. `gate.js`
  stays on disk, dormant, for possible re-use after recategorization clears;
  do not re-add it to any page without rewording its curtain constants first.
  Verify with: `grep -c 'gate.js' *.html` (exactly 0 per file).
- **Content changes:** edit `SPEC.md` first (single source of truth for control
  names/formulas), then propagate to pages; run `python tools/verify_pages.py`
  after any page edit.
- Test over `http://` (`python -m http.server`), never `file://` (matches how
  GitHub Pages serves the site; `file://` differs on WebCrypto and relative-path
  behavior).
