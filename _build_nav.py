"""
_build_nav.py — inject canonical nav v2 + footer v2 into all production pages.

Run:  python _build_nav.py
Safe to re-run: skips pages that already have nav-pill.

LANGUAGE ARCHITECTURE (decided 2026-08-22)
─────────────────────────────────────────
Production language: English only.
No /ru/ routes, no JS language toggle, no hreflang — until a full
original RU content set exists and there is a real SEO reason.

Russian audience → Telegram @Pirate_AI until then.

FUTURE /ru/ ROUTE READINESS
────────────────────────────
When adding /ru/, this script should be extended to:
  1. Read a TRANSLATIONS dict (slug → {en: str, ru: str}) for nav labels.
  2. Write /ru/<slug>/index.html using a RU nav variant (NAV_HTML_RU).
  3. Add hreflang to both EN and RU pages pointing at each other.
  4. Add lang="ru" to the RU html element.

The nav/footer HTML is already separated from page content — each page
only needs its <header>/<footer> replaced. Adding /ru/ does NOT require
rewriting page templates; only this script needs a new RU pass.

DO NOT show a language switcher in the nav until /ru/ routes exist.
"""

import re
from pathlib import Path

BASE = Path(r"C:\Users\62434\pirate_ai_assets\public")

# Pages that have their own special nav (legal docs with nav-back)
SKIP_DIRS = {"privacy", "consent", "terms"}

# ─────────────────────────── CSS ───────────────────────────
NAV_CSS = """
/* ─── Canonical Nav v2 (injected by _build_nav.py) ─── */
.site-header{padding:20px 40px;position:sticky;top:0;z-index:200;background:#F7F8FC}
.nav-pill{max-width:1280px;margin:0 auto;background:#fff;border:1px solid #E4E8F2;border-radius:100px;padding:10px 16px 10px 24px;display:flex;align-items:center;box-shadow:0 2px 16px rgba(29,35,64,.06)}
.nav-logo{font-size:16px;font-weight:600;color:#1D2340;letter-spacing:-.3px;margin-right:auto;white-space:nowrap;text-decoration:none}
.nav-logo .ai{color:#5B76FF}
.nav-links{display:flex;align-items:center;gap:2px;margin:0 16px}
.nav-links a{font-size:14px;color:#6E758C;padding:8px 14px;border-radius:100px;transition:all .18s;text-decoration:none}
.nav-links a:hover{color:#1D2340;background:#F7F8FC}
.nav-cta-link{background:#5B76FF;color:#fff!important;border-radius:100px;padding:10px 22px;font-size:14px;font-weight:500;transition:all .2s;white-space:nowrap;text-decoration:none;display:inline-flex;align-items:center}
.nav-cta-link:hover{background:#4A65EE;box-shadow:0 4px 16px rgba(91,118,255,.4)}
.mob-toggle{display:none;align-items:center;gap:6px;font-size:14px;font-weight:500;color:#1D2340;padding:8px 14px;border-radius:100px;background:none;border:none;cursor:pointer;font-family:inherit}
.mob-toggle:hover{background:#F7F8FC}
.mob-nav{display:none;background:#fff;border:1px solid #E4E8F2;border-radius:20px;margin:8px 24px;padding:12px}
.mob-nav.open{display:block}
.mob-nav a{display:block;padding:12px 16px;font-size:15px;color:#1D2340;border-radius:10px;text-decoration:none}
.mob-nav a:hover{background:#F7F8FC}
.mob-nav .nav-cta-link{display:block;text-align:center;margin-top:8px;border-radius:12px;padding:12px}
@media(max-width:768px){.site-header{padding:16px}.nav-links,.nav-pill>.nav-cta-link{display:none}.mob-toggle{display:flex}}
/* ─── Canonical Footer v2 ─── */
.site-footer-v2{background:#1D2340;border-top:1px solid rgba(255,255,255,.07);padding:28px 40px}
.site-footer-v2 .foot-inner{max-width:1280px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;gap:24px;flex-wrap:wrap}
.site-footer-v2 .foot-logo{font-size:14px;font-weight:600;color:rgba(255,255,255,.6);text-decoration:none}
.site-footer-v2 .foot-logo .ai{color:#5B76FF}
.site-footer-v2 .foot-links{display:flex;gap:20px;flex-wrap:wrap}
.site-footer-v2 .foot-links a{font-size:12px;color:rgba(255,255,255,.45);transition:color .18s;text-decoration:none}
.site-footer-v2 .foot-links a:hover{color:rgba(255,255,255,.9)}
.site-footer-v2 .foot-copy{font-size:12px;color:rgba(255,255,255,.3)}
@media(max-width:640px){.site-footer-v2 .foot-inner{flex-direction:column;align-items:flex-start}.site-footer-v2{padding:24px}}
"""

# ─────────────────────────── HTML ───────────────────────────
NAV_HTML = """\
<header class="site-header">
  <nav class="nav-pill" aria-label="Main navigation">
    <a class="nav-logo" href="/"><span class="ai">AI</span>Asset.Market</a>
    <div class="nav-links">
      <a href="/marketplace/">Deals</a>
      <a href="/services/">Services</a>
      <a href="/insights/">Research</a>
      <a href="/academy/">Academy</a>
      <a href="/methodology/">About</a>
    </div>
    <a class="nav-cta-link" href="mailto:hi@aiasset.market">Contact</a>
    <button class="mob-toggle" onclick="toggleMob()" aria-label="Menu">
      <svg width="18" height="14" viewBox="0 0 18 14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
        <line x1="0" y1="1" x2="18" y2="1"/><line x1="0" y1="7" x2="18" y2="7"/><line x1="0" y1="13" x2="18" y2="13"/>
      </svg>
      Menu
    </button>
  </nav>
  <nav class="mob-nav" id="mob-nav" aria-label="Mobile navigation">
    <a href="/marketplace/">Deals</a>
    <a href="/services/">Services</a>
    <a href="/insights/">Research</a>
    <a href="/academy/">Academy</a>
    <a href="/methodology/">About</a>
    <a class="nav-cta-link" href="mailto:hi@aiasset.market">Contact</a>
  </nav>
</header>"""

FOOTER_HTML = """\
<footer class="site-footer-v2">
  <div class="foot-inner">
    <a class="foot-logo" href="/"><span class="ai">AI</span>Asset.Market</a>
    <div class="foot-links">
      <a href="/marketplace/">Deals</a>
      <a href="/services/">Services</a>
      <a href="/insights/">Research</a>
      <a href="/academy/">Academy</a>
      <a href="/methodology/">Methodology</a>
      <a href="/privacy/">Privacy Policy</a>
      <a href="/terms/">Terms of Use</a>
      <a href="/consent/">Data Consent</a>
      <a href="mailto:hi@aiasset.market">hi@aiasset.market</a>
    </div>
    <span class="foot-copy">© 2026 AIAsset.Market</span>
  </div>
</footer>"""

TOGGLE_MOB_JS = "function toggleMob(){document.getElementById('mob-nav').classList.toggle('open')}"

# Patterns to match the old nav block
OLD_NAV_RE = re.compile(r'<nav class="site-nav"[\s\S]*?</nav>', re.DOTALL)
FOOTER_RE   = re.compile(r'<footer[\s\S]*?</footer>', re.DOTALL)


def process(fpath: Path) -> str:
    content = fpath.read_text(encoding="utf-8")

    # Already updated
    if "nav-pill" in content:
        return "skip (already v2)"

    # Old site-nav not present — nothing to replace
    if '<nav class="site-nav"' not in content:
        return "skip (no site-nav)"

    changed = False

    # 1. Inject nav + footer CSS before first </style>
    if "Canonical Nav v2" not in content:
        content = content.replace("</style>", NAV_CSS + "</style>", 1)
        changed = True

    # 2. Replace old nav block
    if OLD_NAV_RE.search(content):
        content = OLD_NAV_RE.sub(NAV_HTML, content, count=1)
        changed = True

    # 3. Replace footer
    if FOOTER_RE.search(content):
        content = FOOTER_RE.sub(FOOTER_HTML, content, count=1)
        changed = True

    # 4. Ensure toggleMob JS exists
    if "toggleMob" not in content:
        content = content.replace("</script>", TOGGLE_MOB_JS + "\n</script>", 1)
        changed = True

    if changed:
        fpath.write_text(content, encoding="utf-8")
        return "updated"
    return "no changes"


def collect_targets():
    targets = []

    for d in sorted(BASE.iterdir()):
        if not d.is_dir():
            continue
        name = d.name
        if name in SKIP_DIRS or name.startswith(("_", ".", "function")):
            continue
        # blog/ and learn/ — handle index.html here, subdirs separately
        idx = d / "index.html"
        if idx.exists():
            targets.append(idx)
        # recurse one level for blog/* and learn/*
        if name in ("blog", "learn"):
            for sub in sorted(d.iterdir()):
                if sub.is_dir():
                    sub_idx = sub / "index.html"
                    if sub_idx.exists():
                        targets.append(sub_idx)

    return targets


def main():
    targets = collect_targets()
    updated = skipped = 0
    for fpath in targets:
        rel = fpath.relative_to(BASE)
        result = process(fpath)
        print(f"  {rel}: {result}")
        if result == "updated":
            updated += 1
        else:
            skipped += 1
    print(f"\nDone — {updated} updated, {skipped} skipped.")


if __name__ == "__main__":
    main()
