# Design: De-flag the hosted site from Zscaler phishing classification

**Date:** 2026-07-20
**Status:** Approved

## Problem

`https://wastaboy.github.io/3rd_party_html/` (and every `.html` under it) is
blocked at the user's workplace by Zscaler, classified as **phishing**. Other
guide sites by the same author — carrying the *same* `gate.js` password gate —
are not blocked. The user needs to read this guide at work to build the app it
documents.

## Diagnosis

The block is a false positive triggered by this repo's specific combination of
signals, not by the gate mechanism alone (other gated guides pass):

1. **Curtain framing:** the gate presents "Third-Party Application Declaration —
   Enter the password to continue" with a lock icon and corporate navy/amber
   branding. "Official document is password-protected, enter password to view"
   is the most common phishing lure pattern.
2. **Content vocabulary** (hidden behind the curtain, visible to crawlers in
   source): Account (×24), Declaration (×40), SharePoint (×18), Bank (×5),
   Verify, Sign in, Office 365, Outlook — the guide documents an app that
   collects account/bank/declaration details in the Microsoft ecosystem.
3. **Hosting:** free `github.io` subdomain, credential-type input
   (`type="password"`, `autocomplete="current-password"`), all page content
   hidden until unlock.

Once a URL is categorized, every path under it inherits the block — hence the
individual `.html` files being blocked too.

## Decision

Remove the password gate **from this repo only** (the repo source is public
anyway, so the gate provided curtain-privacy, not secrecy). Keep `gate.js` on
disk, untagged, in case the user wants to re-add it after recategorization
clears. Other guide repos keep their gates — they passed classification.

## Changes

1. **Pages:** delete the `<script src="gate.js"></script>` line from
   `index.html`, `part1.html`, `part2.html`, `part3.html`, and `template.html`
   (template included so future generated pages don't re-add it).
2. **Keep `gate.js`** on disk, unreferenced. Add a header comment noting it is
   deliberately not loaded by any page in this repo and why.
3. **`CLAUDE.md` (project):** replace the "Password gate" rule with the
   inverse: this repo must NOT load `gate.js` — a password curtain plus this
   guide's account/bank/O365 vocabulary got the site classified as phishing by
   Zscaler on 2026-07-20. Verification: `grep -c 'gate.js' *.html` → 0 for
   every page. Note that `gate.js` stays on disk for possible re-use after
   recategorization clears.
4. **Verify:** run `python tools/verify_pages.py` after the page edits.
5. **Publish:** commit and push; GitHub Pages redeploys within minutes.

## User actions (outside the repo)

- **Recategorize:** after the push, submit
  `https://wastaboy.github.io/3rd_party_html/` at `sitereview.zscaler.com`
  with a note such as: "Static instructional build guide (Power Apps tutorial),
  no forms, no credential collection — false positive." Typical turnaround
  1–3 business days.
- **Fallback:** ask workplace IT to whitelist the URL if review does not clear.
- **Meanwhile, at work** (github.com is reachable there):
  `git clone https://github.com/Wastaboy/3rd_party_html.git`, then
  `python -m http.server` in the folder and browse `http://localhost:8000`.
  Zscaler does not sit between the browser and localhost. Never open the pages
  via `file://` (repo rule — and irrelevant to the gate now, but WebCrypto-free
  contexts still differ from production).

## Risks

- Recategorization is likely but not guaranteed: the account/bank/O365
  vocabulary remains because it is the subject matter. With content visible
  and no credential form, classifiers normally read it as instructional; the
  IT whitelist is the fallback.
- Re-adding the gate later may re-trigger classification. If re-added, reword
  the curtain constants (KICKER/TITLE/SUBTITLE) away from official-document
  framing first, and expect to re-submit for review.

## Out of scope

- No changes to page content, SPEC.md formulas, or the other guide repos.
- No changes to `tools/verify_pages.py` (it has no gate check).
