"""
_check_links.py — scan all HTML for internal hrefs that don't resolve to a file in public/.
Reports: dead internal links, remaining /#preview-grade "Submit/Browse/Apply" mismatches.
"""

import re
from pathlib import Path
from urllib.parse import urlparse

PUB = Path(r"C:\Users\62434\pirate_ai_assets\public")

HREF_RE = re.compile(r'href="(/[^"#?]*)', re.IGNORECASE)
BAD_CTA_RE = re.compile(r'href="(?:https://aiasset\.market)?/#preview-grade"[^>]*>(Submit Similar|Browse Assets|Apply as Operator|Submit Your Asset)', re.IGNORECASE)

# Paths that are valid even without a file (external redirect targets handled by _redirects)
SKIP = {'/'}


def path_exists(slug: str) -> bool:
    if slug in SKIP:
        return True
    # Normalise: strip trailing slash, strip leading slash
    slug = slug.strip('/')
    # Try as directory with index.html
    if (PUB / slug / 'index.html').exists():
        return True
    # Try as file
    if (PUB / slug).exists():
        return True
    return False


def main():
    dead = []
    bad_ctas = []
    checked = set()

    for fpath in sorted(PUB.rglob('*.html')):
        content = fpath.read_text(encoding='utf-8')
        rel = str(fpath.relative_to(PUB))

        # Bad CTAs
        for m in BAD_CTA_RE.finditer(content):
            bad_ctas.append((rel, m.group(0)[:80]))

        # Internal hrefs
        for m in HREF_RE.finditer(content):
            href = m.group(1).rstrip('/')
            if href in checked:
                continue
            checked.add(href)
            if not path_exists(href):
                dead.append((rel, href))

    print("=== BAD CTAs (still pointing to /#preview-grade with wrong text) ===")
    if bad_ctas:
        for f, snippet in bad_ctas:
            print(f"  {f}: {snippet}")
    else:
        print("  NONE OK")

    print(f"\n=== DEAD INTERNAL LINKS ({len(dead)} unique slugs) ===")
    if dead:
        for f, href in sorted(dead, key=lambda x: x[1]):
            print(f"  {href}  (found in {f})")
    else:
        print("  NONE OK")

    print(f"\nChecked {len(checked)} unique internal hrefs across {sum(1 for _ in PUB.rglob('*.html'))} HTML files.")


if __name__ == '__main__':
    main()
