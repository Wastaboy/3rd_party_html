# Third-Party Application Declaration — Build Guide Series

An interactive, three-part build runbook for creating a **third-party application declaration
solution** in Microsoft Power Apps (Canvas), writing to an existing SharePoint list, with an
IAM email notification via Power Automate.

**Live guide:** https://wastaboy.github.io/3rd_party_html/

| Part | Steps | Covers |
|---|---|---|
| [Part 1 — Foundations](https://wastaboy.github.io/3rd_party_html/part1.html) | A1–A10 | Verify the SharePoint list, create the app, build the add/delete multi-row form (collection write-back architecture), smoke test |
| [Part 2 — Validation](https://wastaboy.github.io/3rd_party_html/part2.html) | B1–B9 | Placeholder help text, mandatory-field validation gate, red-border + per-row error messaging, test script |
| [Part 3 — Submit & ship](https://wastaboy.github.io/3rd_party_html/part3.html) | C1–C9 | Confirmation popup, one-transaction submit with audit stamping, notification flow, end-to-end test, publish |

Every step is self-contained: exact click paths, copy buttons on every formula, tap-to-copy
chips (⧉) on every name and value, and a verification checkpoint before moving on. Progress is
tracked per part in the browser (localStorage).

Pages use a uniform click-vs-enter visual language: **navy button chips** (`kbd.ui`) mark
anything you click in Power Apps / SharePoint / Power Automate, **amber chips** (`code.cc`)
mark values you enter (tap to copy), and **key caps** (`kbd.key`) mark keyboard presses.
Bold is reserved for emphasis. See SPEC.md §9 for the full convention.

## Repo layout

- `part1.html` / `part2.html` / `part3.html` — the guide pages (self-contained; only the IBM Plex fonts load externally)
- `index.html` — series landing page
- `SPEC.md` — the frozen source of truth: control naming registry, every Power Fx formula verbatim, SharePoint column mappings, page metadata. **Edit here first**, then propagate to pages.
- `template.html` — the reusable page shell (CSS/JS with `__TOKEN__` slots)
- `tools/verify_pages.py` — structural verifier (step IDs, storage keys, verbatim formulas, HTML escaping); run after any page edit

## Placeholders

The guides use `<YOUR-SITE-URL>` (SharePoint site) and `<IAM-DL-EMAIL>` (IAM distribution
list) — readers substitute their own values.
