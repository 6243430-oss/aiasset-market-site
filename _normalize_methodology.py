"""Normalize public copy to AI Asset Score v1.0's five fixed dimensions."""

from pathlib import Path


PUBLIC = Path(__file__).resolve().parent / "public"

REPLACEMENTS = {
    "8 dimensions": "5 dimensions",
    "7-dimension": "5-dimension",
    "7 categories": "5 dimensions",
    "utility, transferability, operator fit, proof, monetization, demand, automation depth, and risk":
        "traction, revenue, transferability, automation, and risk",
    "Utility · Monetization · Transferability · Operator Fit · Demand · Proof · Risk":
        "Traction · Revenue · Transferability · Automation · Risk",
    "Utility (0–15), Monetization (0–15), Transferability (0–15), Operator Fit (0–15), Demand (0–15), Proof (0–15), and Risk (0–10)":
        "Traction (0–25), Revenue (0–25), Transferability (0–20), Automation (0–20), and Risk (0–10)",
    "Utility, Monetization, Transferability, Operator Fit, Demand, Proof, Risk":
        "Traction, Revenue, Transferability, Automation, Risk",
    "all seven have to clear a minimum threshold":
        "the combined score must clear the relevant band threshold",
    "transferability, documentation, revenue proof, niche clarity, and more":
        "traction, revenue, transferability, automation, and risk",
    "each worth 0–15 points (with one risk criterion worth up to -10)":
        "weighted as Traction 25, Revenue 25, Transferability 20, Automation 20, and Risk 10",
    "Score across all 7 dimensions. We check docs, setup complexity, customer type, usage proof, and market context.":
        "Score across all 5 dimensions. We check traction, revenue, transferability, automation, and risk.",
    "AI Asset Score — 5-dimension scorecard + price range estimate. Drop #2 opens July 28.":
        "AI Asset Score — 5-dimension scorecard with an indicative price range.",
    "A AI Asset Score is a structured 5-dimension audit":
        "An AI Asset Score is a structured 5-dimension audit",
}


def main() -> None:
    files_changed = 0
    replacements_made = 0
    for path in PUBLIC.rglob("*.html"):
        content = path.read_text(encoding="utf-8")
        updated = content
        for old, new in REPLACEMENTS.items():
            count = updated.count(old)
            if count:
                updated = updated.replace(old, new)
                replacements_made += count
        if updated != content:
            path.write_text(updated, encoding="utf-8")
            files_changed += 1
    print(f"Normalized {replacements_made} phrases across {files_changed} files.")


if __name__ == "__main__":
    main()
