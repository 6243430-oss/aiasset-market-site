# AIAsset.Market — Developer Handoff

## Codex update — 2026-08-27

- Fixed the recursive CORS bug that made `/submit` fail, request-size handling, and form timing logic.
- Fixed mobile navigation across generated pages with `public/site-nav.js`.
- Standardized AI Asset Score v1.0 to five dimensions: Traction 25, Revenue 25, Transferability 20, Automation 20, Risk 10.
- Removed unsupported traction, deal-flow, buyer, timing and paid-product claims.
- Added honest localized overview routes `/ru/`, `/es/`, `/zh/`, language navigation and hreflang on the homepage. Deep content remains English.
- Corrected privacy/consent disclosures; RKN filing and provider-retention status are no longer claimed as completed without confirmation.
- Course and community pages now use waitlists and no longer imply that payment or paid access is live.
- Static checks pass: JavaScript syntax, internal links, sitemap XML and `git diff --check`.
- Still requires a Cloudflare preview deployment and one real submission per form to verify deployed secrets and the Google Sheets contract. No production deployment was performed.

**Branch:** `claude-latest`  
**Last deploy:** `https://bbba7c26.aiasset-market.pages.dev` (2026-08-27)  
**Production:** https://aiasset.market  
**CF Pages project:** `aiasset-market`

---

## What's Done

### Audit Phases 1–5 (external audit → NO-GO → fixed)

**Phase 1 — Content & Branding**
- 391 dead `/#` anchor links replaced with real page links
- "Pirate Grade/Score" → "AI Asset Score" across 59 files
- Nav "Marketplace" → "Acquire", meta/brand updated
- Unverified claims removed (546 subscribers figure, 72h promise, 20-40 projects, 7 criteria→5 dimensions)
- `_redirects`: `/post-a-bounty/` → 301 redirect, 404 → 301 fix
- `/ai-asset-packaging-sprint/` → 301 → `/services/`
- Homepage title/OG → "AI Asset Boutique & Advisory"
- `/methodology/` cleaned: removed 93.6%/47 reviewed/72-hour/Free Audit form

**Phase 2 — Forms & Backend**
- AI Asset Score widget on homepage: form (url/type/mrr/users/pitch) + `/api/preview-grade` + result render (score, band, dimensions bars, valuation, next_step)
- Buyer form `/post-ai-bounty/` → POST `/submit` sheet:Bounties
- Seller form `/sell-ai-asset/` → POST `/submit` sheet:Assets
- Watchlist form `/community/` → POST `/submit` sheet:Watchlist
- `submit.js`: Apps Script errors surfaced to client (was always `{ok:true}`)
- `submit.js`: ALLOWED_SHEETS allowlist — rejects unknown sheet names
- `submit.js`: ALLOWED_FIELDS per sheet — filtered payload forwarded to Apps Script
- `submit.js`: type-safe `String(payload[f] ?? '').trim()` on all fields
- `submit.js`: `context.waitUntil(tgFetch)` — all sheets get Telegram notifications

**Phase 3 — Backend Security (3.1–3.9 done; 3.10 Turnstile pending)**
- KV rate limiting (CF KV namespace RATE_KV, 5 req/h per IP)
- SSRF protection in `/api/preview-grade`: private IP block, IPv6 brackets, `::ffff:`, `fe80`, redirect:'error'
- Prompt injection: `sanitizeSnippet()` + system prompt instruction
- Formula injection: `sanitizeForSheets()` on all GAS-bound fields
- Body 200KB cap, Content-Type allowlist, input schema validation
- LLM response validation, no error leakage
- Security headers: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` on all responses
- CORS: `isAllowedOrigin()` checks both production origins and `*.aiasset-market.pages.dev` preview regex

**Phase 4 — Nav/Footer & i18n**
- `_build_nav.py`: idempotent script, applies nav v2 pill-style + footer v2 to 44 production pages
- English-only: no `/ru/` routes, no JS language toggle — see "Language Mechanism" section below
- Modal accessibility: `role="dialog"`, `aria-modal`, focus trap, Escape key fix
- Privacy/Consent pages: YouTube, CF Analytics, OpenRouter detailed

**Phase 5 — SEO & Config**
- `rel="noopener noreferrer"` on all 35 files with `target="_blank"`
- Sitemap: `/methodology/` added; `/post-a-bounty/` + `/grades/` removed
- `robots.txt`: `Disallow /grades/`, `/weekly-drop/`, `/weekly-drop-2/`
- `wrangler.toml`: `compatibility_date = "2025-04-01"`

### Release Blocker — Fixed (2026-08-27)
The `submit.js` → Google Apps Script payload contract was broken. Fixed:
- **Payload shape**: `{sheet, ...flat}` → `{sheet, data: {...fields}}`
- **Field name**: `asset_type` → `type` in Bounties (both submit.js and post-ai-bounty/index.html)
- **Unused sheet**: "Operators" removed from ALLOWED_SHEETS
- **Response parsing**: Worker now reads `parsedBody.ok` (was always returning success)

### Turnstile Setup (2026-08-27)
- Site key `0x4AAAAAAEcgS-PvWORBBpaP` in all 4 HTML files (index, community, sell-ai-asset, post-ai-bounty)
- Production secret set via `wrangler pages secret put TURNSTILE_SECRET`
- Preview secret set via `wrangler pages secret put TURNSTILE_SECRET --env preview`
- `verifyTurnstile()` wrapped in try/catch (prevents "Network error" on CF transient failures)
- Wildcard `*.aiasset-market.pages.dev` added to Turnstile site's allowed hostnames

### CORS Fix (2026-08-27)
- `isAllowedOrigin()` added to both `submit.js` and `api/preview-grade.js`
- Regex: `/^https:\/\/[a-f0-9]+\.aiasset-market\.pages\.dev$/`
- Allows preview hash-subdomain URLs without hardcoding each deploy

---

## What's NOT Finished

| Item | Status | Blocker |
|------|--------|---------|
| **Real form submission test** | ⏳ Pending | User needs to test on preview URL and verify Google Sheets rows |
| **v5 ZIP for auditor** | ⏳ Pending | Do after tests pass |
| **4.3 Locale video mapping** | ⏳ Pending | No RU video content yet |
| **4.6 Napoykin spelling** | ⏳ Pending | Max's decision (Napoikin vs Napoykin) |
| **Stripe/Gumroad** | ❌ Blocked | Operator Course content blocked — no payment integration |
| **X/Twitter posting** | ❌ Blocked | 402 CreditsDepleted — needs developer.twitter.com top-up |
| **Instagram pipeline** | ⏳ Not started | sessionid stored in `instagram_state.json`; pipeline exists in `pirate_ai/visual_agent.py` |

---

## How GitHub Connects to Cloudflare Pages

**Currently: Direct Wrangler Deploy (NOT GitHub integration)**

Deploys are triggered manually:
```bash
cd pirate_ai_assets
npx wrangler pages deploy public --project-name aiasset-market
```

CF Pages project `aiasset-market` reads from the `public/` folder and `functions/` at root.

**To switch to GitHub auto-deploy:**
1. Push this repo to GitHub
2. CF Dashboard → Pages → `aiasset-market` → Settings → Builds & deployments → Connect to Git
3. Point it at the `main` branch, build output dir: `public`
4. No build command needed (site is pre-built HTML)

**After connecting GitHub**, every push to `main` triggers a production deploy.  
Pushes to non-main branches create preview URLs automatically (hash-subdomain).

**Environment secrets** are set separately from GitHub — they live in CF Dashboard or via `wrangler pages secret put`. GitHub connection does NOT give CF access to any secrets; they must be set in CF.

---

## Language Mechanism

**Decision (2026-08-22): English-only. No `/ru/` routes yet.**

`_build_nav.py` is the single source of nav/footer truth. It contains a full docstring explaining the future `/ru/` architecture. Key points:

- **No JS language toggle** — there is no `lang` cookie, no `navigator.language` detection, no i18n library.
- **No hreflang** — confirmed unnecessary for single-language site.
- **Russian audience** → directed to Telegram @Pirate_AI until RU content is ready.
- **Future `/ru/` path**: extend `_build_nav.py` to write `/ru/<slug>/index.html` with a RU nav variant and add hreflang to both copies. The script's comment block in the file docstring is the spec.

`_build_nav.py` skips `privacy/`, `consent/`, `terms/` (they have their own nav-back design).

---

## Key Files

| File | Purpose |
|------|---------|
| `public/` | All 44 production HTML pages |
| `functions/submit.js` | Form submissions → Google Apps Script → Sheets |
| `functions/api/preview-grade.js` | AI Asset Score widget → OpenRouter LLM |
| `apps-script/submit-handler.gs` | Google Apps Script source (deploy separately in GAS editor) |
| `_build_nav.py` | Injects shared nav v2 + footer v2 into all pages |
| `wrangler.toml` | CF Pages config (KV namespaces, compat date, build dir) |
| `public/_redirects` | All 301 redirects (deleted pages → live pages) |
| `public/_headers` | Security headers for static assets |
| `public/sitemap.xml` | SEO sitemap |

## Encoding Rule (CRITICAL)

**NEVER use PowerShell `Get-Content`/`Set-Content` on HTML files.**  
They corrupt UTF-8 multi-byte characters (em dash → `вЂ"`, arrows → `вт'`, © → `В©`).

**Always use .NET methods:**
```powershell
$text = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))
$text = $text.Replace($old, $new)
[System.IO.File]::WriteAllText($path, $text, [System.Text.UTF8Encoding]::new($false))
```

The last clean ZIP backup: `C:\Users\62434\Downloads\AIAssetMarket_RELEASE_v2_2026-08-25.zip`  
v3 and v4 ZIPs have encoding corruption — do not use as source.
