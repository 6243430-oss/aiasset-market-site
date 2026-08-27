"""
_fix_ctas.py — replace /#preview-grade hrefs where anchor text is wrong.

"Submit Similar"  → /sell-ai-asset/
"Browse Assets"   → /marketplace/
"Apply as Operator" → /community/
"Submit Your Asset" → /sell-ai-asset/

CTAs that remain on /#preview-grade:
  "Get * AI Asset Score", "Grade my asset", "try the AI Asset Score widget"
  (these correctly scroll to the score widget on homepage)
"""

import re
from pathlib import Path

BASE = Path(__file__).resolve().parent / "public"

ANCHOR_RE = re.compile(
    r'(<a\s[^>]*href="(?:https://aiasset\.market)?/#preview-grade"[^>]*>)([\s\S]*?)(</a>)',
    re.DOTALL
)

REDIRECTS = [
    ('Submit Similar',     '/sell-ai-asset/'),
    ('Browse Assets',      '/marketplace/'),
    ('Apply as Operator',  '/community/'),
    ('Submit Your Asset',  '/sell-ai-asset/'),
]


def fix_href(tag_open: str, inner_text: str) -> str:
    stripped = inner_text.strip()
    for keyword, dest in REDIRECTS:
        if keyword in stripped:
            tag_open = re.sub(
                r'href="(?:https://aiasset\.market)?/#preview-grade"',
                f'href="{dest}"',
                tag_open,
                count=1
            )
            return tag_open
    return tag_open  # keep /#preview-grade


def process(fpath: Path) -> int:
    content = fpath.read_text(encoding='utf-8')
    replaced = [0]

    def repl(m):
        new_open = fix_href(m.group(1), m.group(2))
        if new_open != m.group(1):
            replaced[0] += 1
        return new_open + m.group(2) + m.group(3)

    new_content = ANCHOR_RE.sub(repl, content)
    if replaced[0]:
        fpath.write_text(new_content, encoding='utf-8')
    return replaced[0]


def main():
    total = 0
    for fpath in sorted(BASE.rglob('*.html')):
        n = process(fpath)
        if n:
            print(f"  {fpath.relative_to(BASE)}: {n} replaced")
            total += n
    print(f"\nDone — {total} CTA hrefs fixed.")


if __name__ == '__main__':
    main()
