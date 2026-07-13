# SPEC — Third-Party Application Declaration Build Guide Series

**This file is the single source of truth.** Every guide page (part1/part2/part3) copies names,
formulas, and texts from here VERBATIM. Never re-derive or paraphrase a formula. If a formula
must change, change it here first.

The solution being taught: a Power Apps (Canvas) app + Power Automate flow where business users
declare one or more third-party applications; records are written to the **existing** SharePoint
list `3rd party inventory`; an email notifies the IAM team.

---

## 1. Placeholder tokens

These appear in guide text and copy-paste boxes as literal tokens the reader substitutes:

| Token | Meaning |
|---|---|
| `<YOUR-SITE-URL>` | The SharePoint site URL hosting the `3rd party inventory` list |
| `<IAM-DL-EMAIL>` | The IAM distribution list email address |

Every page carries a top note: "Wherever you see `<YOUR-SITE-URL>` or `<IAM-DL-EMAIL>`, substitute your own values."

---

## 2. SharePoint list — expected columns (step A1 verification)

List name: `3rd party inventory`. The 21 columns below must exist with these EXACT display names.
Four have quirks (marked ⚠) — in formulas, always accept IntelliSense autocomplete, never hand-type.

| # | Display name | Expected type | Filled by form? |
|---|---|---|---|
| 1 | `Application Name` | Text (likely the renamed Title) | Yes |
| 2 | ⚠ `Vendor/ Provider Name` (space after `/`) | Text | Yes |
| 3 | ⚠ `Business owner` (lowercase o) | Text | Yes |
| 4 | `Application Purpose` | Multiline text | Yes |
| 5 | `IT Custodian` | Text | Yes |
| 6 | `Admin Accounts Used` | Text | Yes |
| 7 | ⚠ `Permissions / Access levels` (lowercase l) | Multiline text | Yes |
| 8 | `Support / Vendor Contact Information` | Text | Yes |
| 9 | `IAM Role` | Text or Choice — record on worksheet | Yes |
| 10 | `Access Link` | Text | Yes |
| 11 | ⚠ `Division ` (TRAILING SPACE) | Text or Choice — record on worksheet | Yes |
| 12 | `Status` | Text or Choice — record on worksheet | Yes |
| 13 | `Submission Date` | Text or Date/Time — record on worksheet | Yes (auto) |
| 14 | `IAM Notes` | Text | No |
| 15 | `Submission Cycle` | Text | No |
| 16 | `Handover Status` | Text or Choice — record on worksheet | Yes |
| 17 | `Number of Accounts` | Text or Number — record on worksheet | Yes |
| 18 | `Report Export` | Yes/No | No |
| 19 | `Onboarded to IAM Platform` | Yes/No | No |
| 20 | `Access Review Status` | Text | No |
| 21 | `Review Frequency` | Text | No |

**Column worksheet (A1):** the reader records the ACTUAL type of: `IAM Role`, `Division `,
`Status`, `Handover Status`, `Number of Accounts`, `Submission Date`. Consumed at step C5.
CSV evidence (`"Not involved"` lowercase in live data) suggests the choice-like columns are
plain **text** — the primary C5 formula assumes text; a variant note covers Choice/Number/Date.

**A1 also:** (a) confirm `Application Name` is the renamed Title column and that no separate
*required* Title column exists; (b) **add two Single line of text columns if absent** —
`Responder Name` and `Responder Email` (the only permitted list change; required for the audit trail).

---

## 3. App shell

- Canvas app, **Tablet** format, 1366×768, single screen.
- Settings to change at creation (A2): **disable** "Modern controls and themes"; **enable**
  "Formula-level error management"; rename `Screen1` → `scrMain`.
- Classic controls only. Property names in this spec are classic (`HintText`, `Default`, `BorderColor`).
- Flow name (frozen, created in C2 BEFORE adding to the app): `SystemDeclarationNotify`.
  Renaming it after adding breaks `SystemDeclarationNotify.Run(...)`.

## 4. Control naming registry

**Collections / variables** (created in App.OnStart):
`colSystems`, `colIAMRoles`, `colStatusValues`, `colHandoverValues`, `colDivisions`,
`gblShowErrors`, `gblShowConfirm`, `gblShowSuccess`, `gblSubmitting`, `gblNextSeq`,
`gblColorBrand`, `gblColorInk`, `gblColorPaper`.

**colSystems schema** (all text except SeqNo): `RowID` (GUID), `SeqNo` (number), `AppName`,
`Vendor`, `BizOwner`, `Purpose`, `Custodian`, `AdminAccts`, `Permissions`, `SupportContact`,
`IAMRole`, `AccessLink`, `Division`, `Status`, `Handover`, `NumAccts` (text; converted at Patch if needed).

**Header (A5):** `recHeader`, `lblAppTitle`, `lblAppSubtitle`, `lblUserBadge`.

**Gallery (A6):** `galSystems` (blank **vertical** gallery, `Items: colSystems`,
`TemplateSize: 600`, never flexible-height). Template contains: `recRowCard`, `lblRowNum`,
`btnDeleteRow`, `lblRowError`, plus 14 label/input pairs:

| Field | Label | Input | SharePoint display name (exact) |
|---|---|---|---|
| Application Name | `lblAppName` | `txtAppName` | `Application Name` |
| Vendor/Provider Name | `lblVendor` | `txtVendor` | `Vendor/ Provider Name` |
| Business Owner | `lblOwner` | `txtOwner` | `Business owner` |
| Application Purpose | `lblPurpose` | `txtPurpose` (MultiLine) | `Application Purpose` |
| IT Custodian | `lblCustodian` | `txtCustodian` | `IT Custodian` |
| Admin Accounts Used | `lblAdminAccts` | `txtAdminAccts` | `Admin Accounts Used` |
| Permissions / Access Levels | `lblPermissions` | `txtPermissions` (MultiLine) | `Permissions / Access levels` |
| Support / Vendor Contact | `lblSupport` | `txtSupport` | `Support / Vendor Contact Information` |
| IAM Role | `lblIAMRole` | `drpIAMRole` | `IAM Role` |
| Access Link | `lblAccessLink` | `txtAccessLink` | `Access Link` |
| Division | `lblDivision` | `drpDivision` | `Division ` ← trailing space |
| Status | `lblStatus` | `drpStatus` | `Status` |
| Handover Status | `lblHandover` | `drpHandover` | `Handover Status` |
| Number of Accounts | `lblNumAccts` | `txtNumAccts` (Format: Number) | `Number of Accounts` |

**Footer (A9/B4):** `recFooter`, `btnAddSystem`, `lblSystemCount`, `btnSubmit`, `lblFormError`.

**Confirmation popup (C1):** `recOverlay`, `recConfirmCard`, `lblConfirmTitle`, `lblConfirmMsg`,
`btnConfirmYes` (text "Submit"), `btnConfirmNo` (text "Cancel"). All `Visible: gblShowConfirm`.

**Success panel (C6):** `recSuccessOverlay`, `recSuccessCard`, `lblSuccessTitle`, `lblSuccessMsg`,
`btnNewDeclaration` (text "Start a new declaration"). All `Visible: gblShowSuccess`.

## 5. Template geometry (inside galSystems template)

- `recRowCard`: X 8, Y 8, Width 1318, Height 584.
- Left column: labels/inputs X **16**, Width **630**. Right column: X **676**, Width **630**.
- Field row *i* (1..7 per column): label Y = `48 + (i−1)·72`, height 20; input Y = label Y + 24, height 40.
- Left column order (A7): AppName, Vendor, BizOwner, Purpose (ML), Custodian, AdminAccts, Permissions (ML).
- Right column order (A8): SupportContact, IAMRole, AccessLink, Division, Status, Handover, NumAccts.
- `lblRowNum`: X 16, Y 14, Width 200 — `Text: "System " & ThisItem.SeqNo`, bold.
- `btnDeleteRow`: X 1180, Y 14, Width 130, Height 32, text "Delete Row".
- `lblRowError`: X 16, Y 552, Width 1294, Height 40, red text, `AutoHeight` off (fixed template).
- Multiline inputs: same 40 height, `Mode: TextMode.MultiLine` (scrollable) — keeps the grid uniform.

---

## 6. Canonical Power Fx formulas (copy VERBATIM into guide copy-boxes)

### 6.1 App.OnStart (A4)

```
Set(gblColorBrand, ColorValue("#C8102E"));
Set(gblColorInk, ColorValue("#1B2436"));
Set(gblColorPaper, ColorValue("#F4F5F8"));
ClearCollect(colIAMRoles, ["Manage", "Govern", "Not Involved"]);
ClearCollect(colStatusValues, ["Active", "Decommissioned"]);
ClearCollect(colHandoverValues, ["Handover Not Required", "Handed Over", "Pending Handover"]);
ClearCollect(colDivisions, ["Operations & Administration", "Information Technology", "Financial Planning & Control", "Human Resources", "Strategy & Transformation", "Marketing & Communications", "Corporate & Business Development", "Remedial", "In - Business Risk", "Treasury & Investment", "Private Banking & Wealth Management", "International Banking", "Wholesale Banking", "Retail Banking", "Corporate Secretariat", "Information Security", "Risk Management", "Credit & Overseas Risk", "Compliance & AML", "Internal Audit", "Legal"]);
Set(gblShowErrors, false);
Set(gblShowConfirm, false);
Set(gblShowSuccess, false);
Set(gblSubmitting, false);
Set(gblNextSeq, 2);
ClearCollect(colSystems, {RowID: GUID(), SeqNo: 1, AppName: "", Vendor: "", BizOwner: "", Purpose: "", Custodian: "", AdminAccts: "", Permissions: "", SupportContact: "", IAMRole: "", AccessLink: "", Division: "", Status: "", Handover: "", NumAccts: ""})
```

Note: 21 division values, trimmed (the requirement doc's trailing spaces are formatting artifacts).

### 6.2 Add / delete rows

`btnAddSystem.OnSelect` (A9):
```
Collect(colSystems, {RowID: GUID(), SeqNo: gblNextSeq, AppName: "", Vendor: "", BizOwner: "", Purpose: "", Custodian: "", AdminAccts: "", Permissions: "", SupportContact: "", IAMRole: "", AccessLink: "", Division: "", Status: "", Handover: "", NumAccts: ""});
Set(gblNextSeq, gblNextSeq + 1)
```

`btnDeleteRow.OnSelect` (A6):
```
Remove(colSystems, ThisItem)
```

`lblSystemCount.Text` (A9):
```
CountRows(colSystems) & " system(s) in this declaration"
```

### 6.3 Input write-back pattern (A7/A8) — THE architecture

Every text input gets exactly this pair (swap the field name only):
```
Default:  ThisItem.AppName
OnChange: Patch(colSystems, ThisItem, {AppName: Self.Text})
```

Every dropdown gets (swap items collection + field name only):
```
Items:               colIAMRoles
AllowEmptySelection: true
Default:             ThisItem.IAMRole
OnChange:            Patch(colSystems, ThisItem, {IAMRole: Self.Selected.Value})
```

Dropdown → items mapping: `drpIAMRole: colIAMRoles`, `drpDivision: colDivisions`,
`drpStatus: colStatusValues`, `drpHandover: colHandoverValues`.
`txtNumAccts` additionally: `Format: TextFormat.Number`.
`txtPurpose` / `txtPermissions` additionally: `Mode: TextMode.MultiLine`.

**Rule taught by A10:** validation/submit read ONLY `colSystems`, never control state — immune
to gallery scroll-reset and delete-row state-shift.

### 6.4 Canonical row-invalid predicate

Two variants, same logic. URL regex is deliberately lenient (live data has bare domains like
`stc.com.bh`). `IsMatch` requires a LITERAL pattern string — the regex is inlined, never a variable.

**Bare-field variant** (inside `Filter(colSystems, ...)`):
```
IsBlank(AppName) || IsBlank(Vendor) || IsBlank(BizOwner) || IsBlank(Purpose) || IsBlank(Custodian) || IsBlank(AdminAccts) || IsBlank(Permissions) || IsBlank(SupportContact) || IsBlank(IAMRole) || IsBlank(Division) || IsBlank(Status) || IsBlank(Handover) || IsBlank(AccessLink) || !IsMatch(AccessLink, "^(https?://)?([\w\-]+\.)+[\w\-]+(/\S*)?$") || IsBlank(NumAccts) || !IsMatch(NumAccts, "^\d+$")
```

**ThisItem variant** (inside the gallery template): identical with `ThisItem.` prefixed to every field.

### 6.5 Submit gate (B5)

`btnSubmit.OnSelect`:
```
Set(gblShowErrors, true);
If(
    CountRows(colSystems) > 0 && CountRows(Filter(colSystems, IsBlank(AppName) || IsBlank(Vendor) || IsBlank(BizOwner) || IsBlank(Purpose) || IsBlank(Custodian) || IsBlank(AdminAccts) || IsBlank(Permissions) || IsBlank(SupportContact) || IsBlank(IAMRole) || IsBlank(Division) || IsBlank(Status) || IsBlank(Handover) || IsBlank(AccessLink) || !IsMatch(AccessLink, "^(https?://)?([\w\-]+\.)+[\w\-]+(/\S*)?$") || IsBlank(NumAccts) || !IsMatch(NumAccts, "^\d+$"))) = 0,
    Set(gblShowConfirm, true)
)
```

`btnSubmit.DisplayMode` (B4):
```
If(CountRows(colSystems) = 0 || gblSubmitting, DisplayMode.Disabled, DisplayMode.Edit)
```

### 6.6 Error signalling (B6/B7/B8)

**Red border pattern (B6)** — plain fields (12 of them; swap field name):
```
If(gblShowErrors && IsBlank(ThisItem.AppName), Color.Red, RGBA(201, 204, 213, 1))
```
`txtAccessLink.BorderColor`:
```
If(gblShowErrors && (IsBlank(ThisItem.AccessLink) || !IsMatch(ThisItem.AccessLink, "^(https?://)?([\w\-]+\.)+[\w\-]+(/\S*)?$")), Color.Red, RGBA(201, 204, 213, 1))
```
`txtNumAccts.BorderColor`:
```
If(gblShowErrors && (IsBlank(ThisItem.NumAccts) || !IsMatch(ThisItem.NumAccts, "^\d+$")), Color.Red, RGBA(201, 204, 213, 1))
```

**`lblRowError.Text` (B7):**
```
If(!gblShowErrors, "",
With({missing:
    Concat(
        Filter(
            Table(
                {f: "Application Name", bad: IsBlank(ThisItem.AppName)},
                {f: "Vendor/Provider Name", bad: IsBlank(ThisItem.Vendor)},
                {f: "Business Owner", bad: IsBlank(ThisItem.BizOwner)},
                {f: "Application Purpose", bad: IsBlank(ThisItem.Purpose)},
                {f: "IT Custodian", bad: IsBlank(ThisItem.Custodian)},
                {f: "Admin Accounts Used", bad: IsBlank(ThisItem.AdminAccts)},
                {f: "Permissions/Access Levels", bad: IsBlank(ThisItem.Permissions)},
                {f: "Support/Vendor Contact", bad: IsBlank(ThisItem.SupportContact)},
                {f: "IAM Role", bad: IsBlank(ThisItem.IAMRole)},
                {f: "Access Link", bad: IsBlank(ThisItem.AccessLink)},
                {f: "Division", bad: IsBlank(ThisItem.Division)},
                {f: "Status", bad: IsBlank(ThisItem.Status)},
                {f: "Handover Status", bad: IsBlank(ThisItem.Handover)},
                {f: "Number of Accounts", bad: IsBlank(ThisItem.NumAccts)}
            ), bad), f, ", ")},
    If(missing <> "", "Missing: " & missing & ". ", "") &
    If(!IsBlank(ThisItem.AccessLink) && !IsMatch(ThisItem.AccessLink, "^(https?://)?([\w\-]+\.)+[\w\-]+(/\S*)?$"),
        "Access Link must be a valid URL (e.g. https://portal.vendor.com). ", "") &
    If(!IsBlank(ThisItem.NumAccts) && !IsMatch(ThisItem.NumAccts, "^\d+$"),
        "Number of Accounts must be a whole number.", "")
))
```
`lblRowError.Visible`:
```
gblShowErrors && !IsBlank(Self.Text)
```

**`lblFormError.Text` (B8):**
```
If(!gblShowErrors, "",
With({bad: CountRows(Filter(colSystems, IsBlank(AppName) || IsBlank(Vendor) || IsBlank(BizOwner) || IsBlank(Purpose) || IsBlank(Custodian) || IsBlank(AdminAccts) || IsBlank(Permissions) || IsBlank(SupportContact) || IsBlank(IAMRole) || IsBlank(Division) || IsBlank(Status) || IsBlank(Handover) || IsBlank(AccessLink) || !IsMatch(AccessLink, "^(https?://)?([\w\-]+\.)+[\w\-]+(/\S*)?$") || IsBlank(NumAccts) || !IsMatch(NumAccts, "^\d+$")))},
    If(bad > 0, bad & " system record(s) have missing or invalid fields — fix the highlighted rows above.", "")
))
```
`lblFormError.Visible`:
```
gblShowErrors && !IsBlank(Self.Text)
```

Errors live-clear as the user fixes fields (everything is driven off `colSystems`, which the
write-back pattern keeps current on every change).

**B8 polish:** `DelayOutput: true` on all text inputs; `btnDeleteRow.DisplayMode:`
```
If(gblSubmitting, DisplayMode.Disabled, DisplayMode.Edit)
```

### 6.7 Confirmation popup (C1)

All popup controls `Visible: gblShowConfirm`.

`lblConfirmTitle.Text`: `"Confirm submission"`

`lblConfirmMsg.Text`:
```
"You are about to submit " & CountRows(colSystems) & " system record(s) to the 3rd party inventory. The IAM team will be notified by email. Do you want to proceed?"
```

`btnConfirmNo.OnSelect`:
```
Set(gblShowConfirm, false)
```

### 6.8 Submit — write to SharePoint + notify (C5)

`btnConfirmYes.OnSelect` — PRIMARY variant (all quirky columns are TEXT type; adapt per the
A1 worksheet — see variants below). Requires "Formula-level error management" ON.

```
Set(gblSubmitting, true);
IfError(
    ForAll(colSystems As row,
        Patch('3rd party inventory', Defaults('3rd party inventory'),
            {
                'Application Name': row.AppName,
                'Vendor/ Provider Name': row.Vendor,
                'Business owner': row.BizOwner,
                'Application Purpose': row.Purpose,
                'IT Custodian': row.Custodian,
                'Admin Accounts Used': row.AdminAccts,
                'Permissions / Access levels': row.Permissions,
                'Support / Vendor Contact Information': row.SupportContact,
                'IAM Role': row.IAMRole,
                'Access Link': row.AccessLink,
                'Division ': row.Division,
                Status: row.Status,
                'Handover Status': row.Handover,
                'Number of Accounts': row.NumAccts,
                'Submission Date': Now(),
                'Responder Name': User().FullName,
                'Responder Email': User().Email
            }
        )
    ),
    Set(gblSubmitting, false);
    Notify("Submission failed — please try again. " & FirstError.Message, NotificationType.Error),
    SystemDeclarationNotify.Run(User().FullName, User().Email, Text(Now(), "dd mmm yyyy hh:mm"), Text(CountRows(colSystems)));
    Set(gblShowConfirm, false);
    Set(gblShowErrors, false);
    Set(gblSubmitting, false);
    Set(gblShowSuccess, true)
)
```

**C5 adaptation warn-note (keyed to A1 worksheet):**
- Column is **Choice** → wrap in a record: `'IAM Role': {Value: row.IAMRole}` (same for `'Division '`, `Status`, `'Handover Status'`).
- `Number of Accounts` is **Number** → `'Number of Accounts': Value(row.NumAccts)`.
- `Submission Date` is **Text** → `'Submission Date': Text(Now(), "yyyy-mm-dd hh:mm")`.
- Wrong-guess symptom: "expected record value, found text" (or the reverse) on that line.
- The quirky names (`'Division '` etc.): accept IntelliSense — a hand-typed `'Division'` will not resolve.

### 6.9 Success + reset (C6)

All success controls `Visible: gblShowSuccess`.

`lblSuccessTitle.Text`: `"Declaration submitted 🎉"`

`lblSuccessMsg.Text`:
```
"Your system records have been added to the 3rd party inventory and the IAM team has been notified. You can close the app or start a new declaration."
```

`btnNewDeclaration.OnSelect` (fresh GUIDs force new gallery items — discards any residual control state, no Reset() calls needed):
```
Set(gblNextSeq, 2);
ClearCollect(colSystems, {RowID: GUID(), SeqNo: 1, AppName: "", Vendor: "", BizOwner: "", Purpose: "", Custodian: "", AdminAccts: "", Permissions: "", SupportContact: "", IAMRole: "", AccessLink: "", Division: "", Status: "", Handover: "", NumAccts: ""});
Set(gblShowSuccess, false)
```

---

## 7. Hint texts (B1) — verbatim from requirements

| Input | HintText |
|---|---|
| `txtAppName` | `Enter the system/application name` |
| `txtVendor` | `Enter the software vendor or service provider` |
| `txtOwner` | `Enter the business owner name` |
| `txtPurpose` | `Describe the business purpose of the application` |
| `txtCustodian` | `Enter the responsible IT contact` |
| `txtAdminAccts` | `List administrator accounts used to manage the system` |
| `txtPermissions` | `Describe available roles and access levels` |
| `txtSupport` | `Enter support email, phone number, or contact details` |
| `txtAccessLink` | `Enter the application URL or access portal link` |
| `txtNumAccts` | `Enter the total number of active user accounts` |

Dropdown guidance via `Tooltip` (classic dropdowns have no placeholder) (B2):

| Dropdown | Tooltip |
|---|---|
| `drpIAMRole` | `Select IAM involvement level` |
| `drpDivision` | `Select the applicable division` |
| `drpStatus` | `Select the application status` |
| `drpHandover` | `Select the handover status` |

Required-field convention (B3): append ` *` to every field label; asterisk in brand red.

---

## 8. Power Automate flow — `SystemDeclarationNotify` (C2/C3)

- **Trigger:** PowerApps (V2). Four **Text** inputs created in THIS exact order (order defines
  the `.Run()` signature): `ResponderName`, `ResponderEmail`, `SubmissionDate`, `SystemCount`.
  Date/count arrive pre-formatted as text (sidesteps timezone/locale conversion).
- **Action:** Office 365 Outlook — **Send an email (V2)**:
  - To: `<IAM-DL-EMAIL>`
  - CC (optional tip): `ResponderEmail` dynamic content
  - Subject: `New Third-Party Application Submission Received`
  - Body (HTML):
    ```
    <p>A new third-party application declaration has been submitted.</p>
    <ul>
      <li><b>Responder:</b> @{triggerBody()['text']}</li>
      <li><b>Submission date:</b> @{triggerBody()['text_2']}</li>
      <li><b>Number of declared systems:</b> @{triggerBody()['text_3']}</li>
    </ul>
    <p><a href="<YOUR-SITE-URL>/Lists/3rd%20party%20inventory/AllItems.aspx">Open the 3rd party inventory list</a></p>
    ```
    (In the flow editor the reader inserts dynamic content chips `ResponderName`,
    `SubmissionDate`, `SystemCount` rather than typing the `@{...}` expressions.)
- Save the flow with its final name BEFORE C4 (adding to the app). Renaming afterwards breaks
  `.Run` — fix is remove + re-add in the Power Automate pane.

---

## 9. Guide page metadata

Shared shell: `template.html` (CSS/JS lifted verbatim from the html_hustle example guide).
Fonts: IBM Plex Sans/Serif/Mono via Google Fonts. Progress state in localStorage — KEY IS
UNIQUE PER PAGE. Step anatomy: `<details class="step" id="a1">` → summary (dot / num / stitle /
chevron) → body (`p.do` instructions, `ol.steps2` numbered sub-steps, `.fxlabel` + `.fx` dark
copy boxes, `code.cc` tap-to-copy chips, `.note.why|warn|tip|check` callouts) → "Check before
moving on" `.note.check` → `button.done`.

| Page | Title | Kicker | Steps | localStorage KEY |
|---|---|---|---|---|
| `part1.html` | Foundations: the list, the app, and the multi-row form | 3rd-Party Declarations · Part 1 of 3 | A1–A10 | `bbk3pDeclareP1_v1` |
| `part2.html` | Guidance, validation, and error messaging | 3rd-Party Declarations · Part 2 of 3 | B1–B9 | `bbk3pDeclareP2_v1` |
| `part3.html` | Confirm, submit, notify, and ship | 3rd-Party Declarations · Part 3 of 3 | C1–C9 | `bbk3pDeclareP3_v1` |

Footer cross-links on every page (relative hrefs):
`index.html` (Series home) · `part1.html` (Part 1 — Foundations) · `part2.html` (Part 2 — Validation) · `part3.html` (Part 3 — Submit & ship)` — current page shown bold, not linked.

### Step outline (authoritative)

**part1.html — A1–A10**
- A1 Verify the `3rd party inventory` list — 21-column checkpoint table (§2), column worksheet, Title check, add `Responder Name`/`Responder Email` if absent.
- A2 Create blank tablet app; Settings (disable modern controls, enable formula-level error management); rename screen `scrMain`.
- A3 Add the SharePoint data connection to `3rd party inventory` at `<YOUR-SITE-URL>`.
- A4 App.OnStart (§6.1) + Run OnStart. Checkpoint: 5 collections in Variables pane, `colSystems` = 1 row. Note: re-running OnStart wipes in-progress rows (expected while building).
- A5 Header band (§4 header controls, brand colors via `gblColor*` vars).
- A6 Blank vertical gallery `galSystems` (§5 geometry) + `recRowCard`, `lblRowNum`, `btnDeleteRow` wired (§6.2).
- A7 Left column — 7 fields (labels + inputs + write-back §6.3; 2 multiline).
- A8 Right column — 3 text fields + 4 dropdowns (§6.3 dropdown pattern, `AllowEmptySelection`) + `txtNumAccts` Format Number.
- A9 Footer bar: `recFooter`, `btnAddSystem` (§6.2), `lblSystemCount` (§6.2).
- A10 Architecture smoke test: add 3 rows, fill distinct values, scroll away/back (values persist), delete the MIDDLE row (values stay with correct rows), watch Variables pane mirror keystrokes. Why-note: this is why we never read control values at submit.

**part2.html — B1–B9**
- B1 HintText on all 10 text inputs (§7, 10 copy chips/boxes).
- B2 Dropdown tooltips (§7) + verify blank-until-chosen behavior (`AllowEmptySelection` checkpoint).
- B3 Required-field labels: append ` *` (§7 convention).
- B4 Insert `btnSubmit` + `lblFormError` in footer; `btnSubmit.DisplayMode` (§6.5).
- B5 `btnSubmit.OnSelect` validation gate (§6.5). Note: a fully valid click sets `gblShowConfirm` — nothing visible until Part 3; expected.
- B6 Red `BorderColor` on all 14 inputs (§6.6 — 12 plain + URL + number variants).
- B7 `lblRowError` Text + Visible (§6.6).
- B8 `lblFormError` Text + Visible (§6.6) + polish: `DelayOutput`, `btnDeleteRow.DisplayMode`, tab order.
- B9 Validation test script: empty submit → borders + row messages + form count; `not a link` in Access Link and letters in Number of Accounts → specific messages; fix all → errors clear live; valid click passes silently.

**part3.html — C1–C9**
- C1 Confirmation popup (§6.7): overlay, card, title, message, Submit/Cancel; Cancel wired.
- C2 Create flow `SystemDeclarationNotify` (§8): trigger + 4 text inputs in exact order.
- C3 Send an email (V2) action (§8) with placeholders; save; rename warning.
- C4 Add flow to the app (Power Automate pane). Checkpoint: `SystemDeclarationNotify.Run` autocompletes.
- C5 `btnConfirmYes.OnSelect` (§6.8) + column-type adaptation warn-note.
- C6 Success overlay + `btnNewDeclaration` reset (§6.9).
- C7 Audit verification: submit one test record; list item shows `Responder Name`/`Responder Email`/`Submission Date`; `Created By`/`Created` corroborate.
- C8 End-to-end test script: 3-row declaration → cancel → confirm → all rows in SharePoint (spot-check `Division ` landed correctly) → email arrives with correct count + working link → success panel → reset to one blank row.
- C9 Publish & share: publish version; share app; users need CONTRIBUTE on the list; flow connections/run-only users; delegation blue-underlines are expected and harmless (all reads are local collections).

---

## 10. Authoring rules (context-rot defenses)

1. One authoring pass per page; each pass reads ONLY this SPEC + `template.html` — never sibling pages.
2. Formulas copy-pasted from §6 verbatim — never re-derived, never "improved" in place.
3. HTML-escaping in code boxes: `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;` in source, so the
   rendered/copied text is the exact formula. Placeholder tokens render as literal `<YOUR-SITE-URL>`.
4. Every step ends with a `.note.check` "Check before moving on" + `button.done`.
5. localStorage KEY unique per page (§9 table) so progress never bleeds across pages.
6. Tone matches the example guide: imperative, reassuring, tap-to-copy chips for every control
   name and property value ("Paste, never retype").
