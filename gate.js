/* DORMANT in this repo: deliberately not loaded by any page. A password
   curtain plus this guide's account/bank/O365 vocabulary got the site
   classified as phishing by Zscaler (2026-07-20). Kept on disk for possible
   re-use after recategorization clears — reword KICKER/TITLE/SUBTITLE away
   from official-document framing before re-adding, and expect to re-submit
   at sitereview.zscaler.com. See docs/superpowers/specs/2026-07-20-zscaler-deflag-design.md.

   Password gate for static sites — curtain, not a vault.
   Fill the constants below when installing. To change the password:
   printf '%s' 'newpassword' | sha256sum  → paste the hex into HASH.
   Bump KEY (e.g. _v2) to force every device to re-enter the password. */
(function () {
  "use strict";
  var KEY = "pwGate_v1";
  var HASH = "b882fb2c7381a3f81f1a4060d364d9232d0dd7006c0b72385aff41e12c6fce4e";
  var KICKER = "3rd-Party Declarations";
  var TITLE = "Third-Party Application Declaration";
  var SUBTITLE = "Enter the password to continue.";

  try { if (localStorage.getItem(KEY) === HASH) return; } catch (e) {}

  /* No WebCrypto (old browser / some file:// contexts): fail open rather than brick the page. */
  if (!(window.crypto && crypto.subtle && window.TextEncoder)) return;

  /* Hide the page before first paint — this script must be loaded synchronously in <head>. */
  var st = document.createElement("style");
  st.id = "pwGateStyle";
  st.textContent = "body > *:not(#pwGate){display:none !important}";
  document.head.appendChild(st);

  function sha256hex(text) {
    return crypto.subtle.digest("SHA-256", new TextEncoder().encode(text)).then(function (buf) {
      return Array.prototype.map.call(new Uint8Array(buf), function (b) {
        return ("0" + b.toString(16)).slice(-2);
      }).join("");
    });
  }

  function build() {
    var w = document.createElement("div");
    w.id = "pwGate";
    w.setAttribute("style",
      "position:fixed;inset:0;z-index:99999;display:flex;align-items:center;justify-content:center;" +
      "padding:24px;box-sizing:border-box;" +
      "background:radial-gradient(120% 140% at 100% 0%, rgba(224,138,30,.22), transparent 55%)," +
      "linear-gradient(160deg,#1F3B6E 0%,#142a52 100%);");
    w.innerHTML =
      '<div style="width:100%;max-width:380px;text-align:center;color:#fff;font-family:\'IBM Plex Sans\',system-ui,sans-serif">' +
        '<div style="width:60px;height:60px;margin:0 auto 16px;border-radius:15px;background:linear-gradient(160deg,#274982,#1a345f);border:1px solid rgba(255,255,255,.18);display:flex;align-items:center;justify-content:center;box-shadow:0 8px 22px -10px rgba(0,0,0,.6)">' +
          '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="rgba(224,138,30,.95)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="10" width="16" height="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></svg>' +
        '</div>' +
        '<p id="pwGateKicker" style="font-family:\'IBM Plex Mono\',monospace;font-size:14px;letter-spacing:.22em;text-transform:uppercase;color:#E08A1E;font-weight:500;margin:0 0 8px"></p>' +
        '<h1 id="pwGateTitle" style="font-family:\'IBM Plex Serif\',Georgia,serif;font-weight:600;font-size:30px;line-height:1.15;margin:0 0 6px"></h1>' +
        '<p id="pwGateSub" style="margin:0 0 20px;color:#c7d2e8;font-size:17px"></p>' +
        '<input id="pwGateInput" type="password" autocomplete="current-password" inputmode="text" placeholder="Password" ' +
          'style="width:100%;box-sizing:border-box;font-family:\'IBM Plex Mono\',monospace;font-size:20px;text-align:center;padding:13px 14px;border:1.5px solid rgba(255,255,255,.25);border-radius:11px;background:rgba(255,255,255,.08);color:#fff;outline:none">' +
        '<button id="pwGateBtn" type="button" ' +
          'style="width:100%;margin-top:12px;min-height:46px;border:none;border-radius:11px;background:rgba(224,138,30,.95);color:#1b1206;font-family:\'IBM Plex Sans\',system-ui,sans-serif;font-size:19px;font-weight:600;cursor:pointer">Unlock</button>' +
        '<p id="pwGateErr" style="min-height:24px;margin:12px 0 0;color:#ffb4a8;font-size:16px;visibility:hidden">Wrong password — try again.</p>' +
      '</div>';
    document.body.appendChild(w);

    /* textContent, not innerHTML interpolation — titles render literally whatever they contain */
    document.getElementById("pwGateKicker").textContent = KICKER;
    document.getElementById("pwGateTitle").textContent = TITLE;
    document.getElementById("pwGateSub").textContent = SUBTITLE;

    var input = document.getElementById("pwGateInput");
    var btn = document.getElementById("pwGateBtn");
    var err = document.getElementById("pwGateErr");
    var busy = false;

    function unlock() {
      try { localStorage.setItem(KEY, HASH); } catch (e) {}
      w.remove();
      st.remove();
    }
    function attempt() {
      if (busy) return;
      var v = input.value;
      if (!v) { input.focus(); return; }
      busy = true;
      sha256hex(v).then(function (hex) {
        busy = false;
        if (hex === HASH) { unlock(); return; }
        err.style.visibility = "visible";
        input.value = "";
        input.focus();
      }, function () { busy = false; });
    }

    btn.addEventListener("click", attempt);
    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter") attempt();
      else err.style.visibility = "hidden";
    });
    input.focus();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", build);
  } else {
    build();
  }
})();
