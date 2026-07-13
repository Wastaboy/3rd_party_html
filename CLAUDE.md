# Project rules

- **Password gate:** every `.html` page in this repo must include
  `<script src="gate.js"></script>` on its own line immediately after
  `<meta charset="UTF-8">` (synchronous, in `<head>` — never `defer`/`async` or
  end-of-body, or content flashes before the lock). `template.html` already
  carries the tag, so pages generated from it inherit it. Verify with:
  `grep -c 'gate.js' *.html` (exactly 1 per file).
  The gate is a curtain, not a vault — page source stays readable in this public
  repo. To change the password: `printf '%s' 'new' | sha256sum` → paste into
  `HASH` in `gate.js`; bump `KEY` (`pwGate_v2`) to force all devices to re-enter.
- **Content changes:** edit `SPEC.md` first (single source of truth for control
  names/formulas), then propagate to pages; run `python tools/verify_pages.py`
  after any page edit.
- Test over `http://` (`python -m http.server`), never `file://` (no WebCrypto —
  the gate fails open and looks absent).
