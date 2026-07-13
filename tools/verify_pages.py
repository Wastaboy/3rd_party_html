"""Phase 4 scripted verification of the guide series against SPEC.md."""
import html
import re
import sys
from pathlib import Path

REPO = Path(r"C:\Users\MCPC -902\Projects\3rd_party_html")
PAGES = {
    "part1.html": {"ids": [f"a{i}" for i in range(1, 11)], "key": "bbk3pDeclareP1_v1"},
    "part2.html": {"ids": [f"b{i}" for i in range(1, 10)], "key": "bbk3pDeclareP2_v1"},
    "part3.html": {"ids": [f"c{i}" for i in range(1, 10)], "key": "bbk3pDeclareP3_v1"},
}

DIVISIONS = ["Operations & Administration", "Information Technology",
    "Financial Planning & Control", "Human Resources", "Strategy & Transformation",
    "Marketing & Communications", "Corporate & Business Development", "Remedial",
    "In - Business Risk", "Treasury & Investment", "Private Banking & Wealth Management",
    "International Banking", "Wholesale Banking", "Retail Banking", "Corporate Secretariat",
    "Information Security", "Risk Management", "Credit & Overseas Risk", "Compliance & AML",
    "Internal Audit", "Legal"]

HINTS = ["Enter the system/application name", "Enter the software vendor or service provider",
    "Enter the business owner name", "Describe the business purpose of the application",
    "Enter the responsible IT contact", "List administrator accounts used to manage the system",
    "Describe available roles and access levels",
    "Enter support email, phone number, or contact details",
    "Enter the application URL or access portal link",
    "Enter the total number of active user accounts"]

C5_COLUMNS = ["'Application Name'", "'Vendor/ Provider Name'", "'Business owner'",
    "'Application Purpose'", "'IT Custodian'", "'Admin Accounts Used'",
    "'Permissions / Access levels'", "'Support / Vendor Contact Information'",
    "'IAM Role'", "'Access Link'", "'Division '", "'Handover Status'",
    "'Number of Accounts'", "'Submission Date'", "'Responder Name'", "'Responder Email'"]

# Formulas that must appear verbatim (decoded) somewhere in the given page's .fx blocks.
SPEC_SNIPPETS = {
    "part1.html": [
        'ClearCollect(colIAMRoles, ["Manage", "Govern", "Not Involved"])',
        'ClearCollect(colStatusValues, ["Active", "Decommissioned"])',
        'ClearCollect(colHandoverValues, ["Handover Not Required", "Handed Over", "Pending Handover"])',
        "Remove(colSystems, ThisItem)",
        "Set(gblNextSeq, gblNextSeq + 1)",
        'CountRows(colSystems) & " system(s) in this declaration"',
        "Patch(colSystems, ThisItem, {AppName: Self.Text})",
        "Patch(colSystems, ThisItem, {IAMRole: Self.Selected.Value})",
        "Patch(colSystems, ThisItem, {NumAccts: Self.Text})",
    ],
    "part2.html": [
        "If(CountRows(colSystems) = 0 || gblSubmitting, DisplayMode.Disabled, DisplayMode.Edit)",
        'IsBlank(AccessLink) || !IsMatch(AccessLink, "^(https?://)?([\\w\\-]+\\.)+[\\w\\-]+(/\\S*)?$") || IsBlank(NumAccts) || !IsMatch(NumAccts, "^\\d+$")',
        "If(gblShowErrors && IsBlank(ThisItem.AppName), Color.Red, RGBA(201, 204, 213, 1))",
        "gblShowErrors && !IsBlank(Self.Text)",
        '{f: "Application Name", bad: IsBlank(ThisItem.AppName)}',
        '"Number of Accounts must be a whole number."',
        'have missing or invalid fields',
    ],
    "part3.html": [
        "Set(gblShowConfirm, false)",
        'You are about to submit " & CountRows(colSystems) & " system record(s)',
        "'Division ': row.Division,",
        "'Vendor/ Provider Name': row.Vendor,",
        "'Responder Name': User().FullName,",
        "'Responder Email': User().Email",
        'SystemDeclarationNotify.Run(User().FullName, User().Email, Text(Now(), "dd mmm yyyy hh:mm"), Text(CountRows(colSystems)))',
        'Notify("Submission failed — please try again. " & FirstError.Message, NotificationType.Error)',
        "Set(gblNextSeq, 2);",
    ],
}

fails, warns = [], []

def fail(msg): fails.append(msg)
def warn(msg): warns.append(msg)

texts = {}
for name in PAGES:
    p = REPO / name
    if not p.exists():
        fail(f"{name}: MISSING")
        continue
    texts[name] = p.read_text(encoding="utf-8")

for name, spec in PAGES.items():
    if name not in texts: continue
    t = texts[name]
    # step ids in order, exactly once
    ids = re.findall(r'<details class="step[^"]*" id="([a-z0-9]+)"', t)
    if ids != spec["ids"]:
        fail(f"{name}: step ids {ids} != expected {spec['ids']}")
    opens = re.findall(r'<details class="step[^"]*" id="([a-z0-9]+)"[^>]*\bopen\b', t)
    if len(opens) != 1:
        fail(f"{name}: expected exactly 1 open step, got {opens}")
    # storage key
    m = re.search(r'var KEY="([^"]+)"', t)
    if not m or m.group(1) != spec["key"]:
        fail(f"{name}: storage KEY = {m.group(1) if m else None}, expected {spec['key']}")
    # no template tokens
    toks = set(re.findall(r"__[A-Z_]+__", t))
    if toks:
        fail(f"{name}: leftover template tokens {toks}")
    # every .fx has a copy button
    fx_blocks = re.findall(r'<div class="fx">(.*?)</div>', t, re.S)
    for i, b in enumerate(fx_blocks):
        if '<button class="copy"' not in b:
            fail(f"{name}: .fx block #{i+1} missing Copy button")
    # done buttons and check-notes per step
    n_steps = len(spec["ids"])
    n_done = t.count('class="done"')
    n_check = t.count('note check')
    if n_done < n_steps: fail(f"{name}: {n_done} done buttons < {n_steps} steps")
    if n_check < n_steps: fail(f"{name}: {n_check} check notes < {n_steps} steps")
    # raw ampersand inside <code> (should be &amp;)
    for cm in re.finditer(r"<code[^>]*>(.*?)</code>", t, re.S):
        seg = cm.group(1)
        bad = re.findall(r"&(?!amp;|lt;|gt;|quot;|#\d+;|#x[0-9a-fA-F]+;)", seg)
        if bad:
            fail(f"{name}: raw '&' inside <code> near: {seg[:60]!r}")
            break
    # series footer links
    for other in PAGES:
        if other != name and f'href="{other}"' not in t:
            fail(f"{name}: footer missing link to {other}")
    if 'href="index.html"' not in t:
        warn(f"{name}: no link to index.html")

    # decoded .fx code content for verbatim checks
    codes = [html.unescape(re.sub(r"<[^>]+>", "", c))
             for c in re.findall(r'<div class="fx"><button class="copy"[^>]*>Copy</button><code>(.*?)</code></div>', t, re.S)]
    joined = "\n\x00\n".join(codes)
    for snip in SPEC_SNIPPETS.get(name, []):
        if snip not in joined:
            fail(f"{name}: SPEC snippet not found verbatim in any .fx box: {snip[:80]!r}")

# unique keys
keys = [PAGES[n]["key"] for n in PAGES]
if len(set(keys)) != 3: fail(f"storage keys not unique: {keys}")

# part1: divisions exactly once each in the OnStart box
if "part1.html" in texts:
    t1 = html.unescape(texts["part1.html"])
    dz_missing = [d for d in DIVISIONS if f'"{d}"' not in t1]
    if dz_missing: fail(f"part1: divisions missing from OnStart: {dz_missing}")
    multi = [d for d in DIVISIONS if t1.count(f'"{d}"') > 1]
    if multi: warn(f"part1: divisions appearing more than once (quoted): {multi}")

# part2: all 10 hint texts
if "part2.html" in texts:
    t2 = html.unescape(texts["part2.html"])
    h_missing = [h for h in HINTS if h not in t2]
    if h_missing: fail(f"part2: hint texts missing: {h_missing}")

# part3: all C5 columns + placeholders escaped
if "part3.html" in texts:
    t3raw = texts["part3.html"]
    t3 = html.unescape(t3raw)
    c_missing = [c for c in C5_COLUMNS if c not in t3]
    if c_missing: fail(f"part3: C5 columns missing: {c_missing}")
    if "Status: row.Status" not in t3: fail("part3: C5 missing 'Status: row.Status'")
    for tok in ("&lt;YOUR-SITE-URL&gt;", "&lt;IAM-DL-EMAIL&gt;"):
        if tok not in t3raw: fail(f"part3: escaped placeholder {tok} not found")
    # raw unescaped placeholder tokens must not exist in source
    if re.search(r"<YOUR-SITE-URL>|<IAM-DL-EMAIL>", t3raw): fail("part3: RAW (unescaped) placeholder token in source")

# index links
idx = (REPO / "index.html").read_text(encoding="utf-8")
for n in PAGES:
    if f'href="{n}"' not in idx: fail(f"index.html: missing link to {n}")

print("=== FAILURES ===" if fails else "=== ALL CHECKS PASSED ===")
for f in fails: print("FAIL:", f)
for w in warns: print("warn:", w)
sys.exit(1 if fails else 0)
