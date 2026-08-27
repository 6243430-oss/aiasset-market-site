import zipfile, os
from pathlib import Path

BASE = Path(r"C:\Users\62434\pirate_ai_assets")
OUT  = Path(r"C:\Users\62434\Downloads\AIAssetMarket_RELEASE_2026-08-25.zip")
EXCLUDE = {
    '.wrangler', 'EXTERNAL_AUDIT.md', '_build_nav.py', '_fix_ctas.py',
    '_check_links.py', '_make_zip.py', 'REVIEW_NOTES.md', '.gitignore',
    'listings.json', 'assets.json', 'listings_ru.json',
}

if OUT.exists():
    OUT.unlink()

with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(BASE):
        rp = Path(root)
        # Skip excluded top-level dirs entirely
        if rp == BASE:
            dirs[:] = [d for d in dirs if d not in EXCLUDE]
        # Skip .wrangler anywhere
        dirs[:] = [d for d in dirs if d != '.wrangler']

        for f in files:
            if f in EXCLUDE:
                continue
            fp = rp / f
            arcname = str(fp.relative_to(BASE))
            zf.write(fp, arcname)

size = round(OUT.stat().st_size / 1024 / 1024, 2)
print(f"ZIP created: {OUT} ({size} MB)")
