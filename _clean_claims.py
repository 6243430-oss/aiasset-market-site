"""Remove unsupported traction, deal, and availability claims from public copy."""

from pathlib import Path


PUBLIC = Path(__file__).resolve().parent / "public"

REPLACEMENTS = {
    "47 AI projects graded.<br>3 passed. We know what works.": "A practical framework for evaluating, operating, and transferring AI assets.",
    "This course is built from real deal flow — not theory. Every lesson is based on patterns we've seen across hundreds of AI asset reviews on AIAsset.Market.": "The curriculum is based on the published AI Asset Score methodology and practical operating checklists. Course access is not open yet.",
    "Written from real deal flow.": "Written from the published methodology and public market research.",
    "47 AI projects reviewed. 3 qualified. Here's what separated them — and what killed the other 44.": "What separates a transferable AI asset from a demo — and which gaps matter most.",
    "Based on 47 AI projects reviewed.": "Based on the AI Asset Score methodology.",
    "We reviewed 47 AI projects in our last batch. Three qualified as real assets. The other 44 were, in various ways, demos with a price tag. Here's the fastest way to tell them apart.": "Many projects advertised as assets are still demos with a price tag. Here's the fastest way to tell the difference.",
    "After reviewing 47 projects, we've catalogued the patterns.": "The same failure patterns appear repeatedly in public AI-project listings.",
    "from the team that reviewed 47 AI projects": "using the AI Asset Score methodology",
    "From the team that reviewed 47 projects.": "Built around the AI Asset Score methodology.",
    "We wrote the rules — based on 47 AI projects reviewed, 3 approved, and real deals closed.": "We assembled a consistent framework for screening, packaging, and transferring AI-native projects.",
    "Real playbooks from real deal flow — not theory.": "Practical playbooks based on the published methodology.",
    "Written from real deal flow — 47 projects reviewed, 3 approved.": "Built around the published AI Asset Score methodology.",
    "From the team that graded 47 AI projects.": "Built around the AI Asset Score methodology.",
    "Written by the team that graded 47 AI projects — and approved only 3.": "Practical guides built around one consistent AI Asset Score methodology.",
    "We reviewed 47 AI projects in Drop #2. Three qualified as assets. Here's what separated them — and what killed the other 44.": "What separates a transferable AI asset from a demo — and which gaps matter most.",
    "Get a free AI Asset Score (0–100 score) across 5 dimensions. We've reviewed 47 projects. Spots are limited.": "Get an instant AI Asset Score across 5 dimensions. Automated results are indicative and do not guarantee manual review.",
    "We've reviewed 47 AI projects on AIAsset.Market. Only a fraction were chatbot businesses with meaningful valuation. Here's exactly how buyers assess them — and what moves the number up or down by 3–5×.": "Chatbot valuations depend on revenue quality, transferability, automation, and risk. Here's how to examine those factors without inventing a multiple.",
    "We reviewed 47 AI projects in Drop #2. Three qualified as assets. This is what separated the three from the forty-four — and why the difference matters more than the quality of the AI itself.": "The difference between a demo and a transferable asset matters more than the novelty of the AI itself.",
    "In Drop #2, we reviewed 47 submissions from AI builders across X, Telegram, and Lovable communities. Only 3 received a AI Asset Score of B or above — qualifying for the asset marketplace. Here's the breakdown of why the others failed:": "Projects usually fail the asset test for a small set of repeatable reasons:",
    "One of our approved Drop #2 assets spent two weeks converting from toy to asset before submitting. The founder rewrote nothing. They documented everything. The AI Asset Score went from 41 (rejected) to 74 (approved as Grade B).": "A project can improve its score without rebuilding the product when the main gaps are documentation, access separation, operating procedures, and evidence.",
    "Every week we grade new AI projects, list the ones that qualify, and match them with buyers, operators, or investors.": "We are building a process to evaluate AI projects and connect credible opportunities with buyers or operators.",
    "What active buyers are searching for right now. If you have an asset that matches, skip the listing queue — we'll intro you directly.": "Example acquisition criteria and submitted buyer briefs. Availability and introductions are verified case by case.",
    "Top-scoring tools get introduced to active buyers. Free grade for every submission.": "Automated scoring is available; buyer introductions are not guaranteed.",
    "We'll review it, score it across 5 dimensions, and contact you with next steps — usually within 2 business days.": "We'll receive the submission and contact you if it is selected for manual review.",
    "We'll review your submission and get back to you within 2 business days.": "We'll contact you if the submission is selected for manual review.",
    "Submit for a free AI Asset Score first. If you qualify, we list it in the next Drop. We have active buyers specifically looking for graded AI assets.": "Start with an AI Asset Score, then prepare evidence and a transfer package before seeking buyers.",
    "Active buyers in our network have capital ready and specific criteria. If your AI project matches any of these, submit it for a free review — we'll make the intro.": "The briefs below describe acquisition criteria submitted to the project or used as illustrative examples. Any buyer status and introduction must be verified case by case.",
    "Weekly Drop #1 closes July 27. 10 slots. Submit for a free AI Asset Score — A and B-grade tools get direct buyer introductions.": "Submit for an AI Asset Score. Scoring does not guarantee acceptance, an introduction, or a transaction.",
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
    print(f"Cleaned {replacements_made} unsupported claims across {files_changed} files.")


if __name__ == "__main__":
    main()
