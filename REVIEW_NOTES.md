# AIAsset.Market — Review Notes for External Audit

**Date:** 2026-08-21  
**Live site:** https://aiasset.market  
**Last deployment preview:** https://98aece03.aiasset-market.pages.dev

---

## 1. Stack

- **Frontend:** Static HTML/CSS/JS — no framework, no build step
- **Hosting/CDN:** Cloudflare Pages
- **Serverless API:** Cloudflare Pages Functions (Workers runtime)
- **AI:** OpenRouter API → `meta-llama/llama-3.3-70b-instruct`
- **Form submissions:** Google Apps Script → Google Sheets
- **Notifications:** Telegram Bot API
- **Rate limiting:** Cloudflare KV (namespace: `RATE_LIMIT`)
- **Analytics:** Cloudflare Web Analytics (script injected by CF Pages)

---

## 2. How to Run Locally

```bash
# Install Wrangler
npm install -g wrangler

# Login to Cloudflare
npx wrangler login

# Run local dev server (serves functions + static files)
npx wrangler pages dev . --port 8788

# Set local secrets (for functions to work)
# Create a .dev.vars file (NOT committed) with the variables from .env.example
```

No npm install needed — no node_modules, no build step.

---

## 3. How to Build for Production

No build step. The repository root IS the production output.

Deploy:
```bash
npx wrangler pages deploy .
```

Or via CF Pages GitHub integration (not currently configured — manual deploys only).

---

## 4. Deployment

- **Platform:** Cloudflare Pages (project: `aiasset-market`)
- **Deploy command:** `npx wrangler pages deploy . --project-name aiasset-market`
- **Config file:** `wrangler.toml`
- **Routing:** `_redirects` file (Cloudflare Pages routing syntax)
- **Headers:** `_headers` file (Cloudflare Pages headers syntax)
- **KV binding:** `RATE_KV` → namespace `RATE_LIMIT` (ID: `6ee5535ef5d544689fa3c231da5128ba`)  
  Must be configured in CF Dashboard → Pages → aiasset-market → Settings → Functions → KV namespace bindings

---

## 5. Frontend Structure

All frontend is at the repository root (`pirate_ai_assets/`).

| Path | Description |
|------|-------------|
| `index.html` | Homepage (hero, AI Asset Score widget, video, CTA) |
| `methodology/index.html` | AI Asset Score v1.0 methodology (5 dimensions) |
| `blog/` | 3 articles: how-to-buy, valuation, ai-vs-traditional |
| `marketplace/index.html` | Marketplace hub (minimal, boutique positioning) |
| `services/index.html` | Services hub |
| `academy/index.html` | Academy hub |
| `insights/index.html` | Research & Intelligence hub |
| `community/index.html` | Community page |
| `operator-course/index.html` | Operator Course sales page |
| `terms/index.html` | Terms of Service |
| `privacy/index.html` | Privacy Policy (152-ФЗ + GDPR) |
| `consent/index.html` | Cross-border data transfer consent |
| `404.html` | 404 error page |
| `sitemap.xml` | Sitemap |
| `robots.txt` | Robots rules |
| `_headers` | Security headers (CSP, HSTS, X-Frame-Options, etc.) |
| `_redirects` | URL routing & redirects |

**SEO landing pages** (thin pages targeting long-tail keywords):
`sell-ai-tool/`, `sell-ai-agent/`, `sell-ai-asset/`, `sell-ai-saas/`, `sell-ai-automation/`,
`ai-assets-for-sale/`, `ai-agents-for-sale/`, `ai-business-for-sale/`,
`ai-tool-valuation/`, `ai-asset-operator/`, `ai-asset-audit/`, etc.

**Grade cards** (`grades/`): 9 HTML files with individual AI asset evaluation summaries.  
⚠️ Known issue: nav in these files is outdated (not updated by `_apply_nav.py` script — excluded via SKIP_DIRS).

---

## 6. Backend / API

| File | Endpoint | Description |
|------|----------|-------------|
| `functions/api/preview-grade.js` | `POST /api/preview-grade` | AI Asset Score — fetches URL, sends to LLM, returns score |
| `functions/submit.js` | `POST /submit` | Form submissions → Google Sheets + Telegram notification |

---

## 7. Forms

| Form | Endpoint | Destination | Status |
|------|----------|-------------|--------|
| AI Asset Score widget | `/api/preview-grade` | OpenRouter LLM | ✅ Live |
| Submit an Asset | `/submit` (sheet=Assets) | Google Sheets | ✅ Live |
| Post a Bounty | `/submit` (sheet=Bounties) | Google Sheets | ✅ Live |
| Operator Signup | `/submit` (sheet=Operators) | Google Sheets | ✅ Live |
| Watchlist / Newsletter | `/submit` (sheet=Watchlist) | Google Sheets + Telegram | ✅ Live |
| Contact | Not yet connected | — | ⚠️ Pending |

---

## 8. AI Calls

**File:** `functions/api/preview-grade.js`

Flow:
1. Receives POST with `{url, asset_type, mrr, revenue, contracts, assets_included, users, pitch}`
2. Fetches the asset URL (first 4KB of text content) — with SSRF protection
3. Sanitizes snippet against prompt injection
4. Sends to OpenRouter (`meta-llama/llama-3.3-70b-instruct`)
5. Returns JSON: `{total, dimensions, band, one_liner, next_step, operator_value, strategic_value, value_note}`

**Cost:** ~$0.005 per call  
**Rate limit:** 10 requests / IP / 24h (via CF KV)

---

## 9. URL Fetching / Audit Logic

**File:** `functions/api/preview-grade.js` — function `fetchSnippet(url)`

Security controls implemented:
- `isSafeUrl()`: validates scheme (http/https only), blocks localhost, blocks private IP ranges (127.x, 10.x, 172.16-31.x, 192.168.x, 169.254.x, IPv6 loopback/ULA)
- `redirect: 'error'` — does NOT follow redirects (prevents redirect-based SSRF)
- Content truncated to 4000 chars before sending to LLM
- `sanitizeSnippet()` strips obvious prompt injection patterns before LLM call

---

## 10. Data Storage

| Data | Where |
|------|-------|
| Form submissions | Google Sheets (via Apps Script) |
| Rate limit counters | Cloudflare KV (`RATE_LIMIT` namespace) |
| Demo listings | `listings.json`, `listings_ru.json` (static files, `is_demo: true` only) |
| Grade cards | `grades/*.html` (static HTML, manually created) |
| No user database | — |
| No auth system | — |
| No cookies (first-party) | — |

---

## 11. External Services

| Service | Purpose | Secret |
|---------|---------|--------|
| OpenRouter | LLM for AI Asset Score | `OPENROUTER_API_KEY` |
| Cloudflare Pages | Hosting, CDN, Workers | Account-level (wrangler login) |
| Cloudflare KV | Rate limiting | KV binding `RATE_KV` |
| Cloudflare Analytics | Web analytics | Auto-injected by CF Pages |
| Google Apps Script | Form → Sheets relay | `APPS_SCRIPT_URL` |
| Telegram Bot API | Watchlist notifications | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` |
| YouTube | Hero video embed (lazy load) | None (public embed) |
| Google Fonts | Typography (Playfair Display, Inter) | None (public CDN) |

---

## 12. Environment Variables

See `.env.example` for all required variables.

| Variable | Used in | Required |
|----------|---------|---------|
| `OPENROUTER_API_KEY` | `functions/api/preview-grade.js` | Yes |
| `TELEGRAM_BOT_TOKEN` | `functions/submit.js` | Optional (Watchlist notifications) |
| `TELEGRAM_CHAT_ID` | `functions/submit.js` | Optional (default: @Pirate_AI) |
| `APPS_SCRIPT_URL` | `functions/submit.js` | Yes (forms won't save without it) |
| `RATE_KV` | Both functions | KV binding (not a secret, set in wrangler.toml) |

---

## 13. Security — What Has Been Done

**Implemented 2026-08-21:**

- **SSRF protection** (`preview-grade.js`): `isSafeUrl()` validates scheme + blocks private IPs + `redirect:'error'`
- **Rate limiting via CF KV** (both functions): replaces in-memory `ipLog = {}` which doesn't work across CF Worker isolates. KV namespace `RATE_LIMIT` (ID: `6ee5535ef5d544689fa3c231da5128ba`), binding `RATE_KV`
- **Prompt injection protection** (`preview-grade.js`): `sanitizeSnippet()` strips injection patterns; system prompt includes explicit instruction to ignore page content instructions
- **Formula injection protection** (`submit.js`): `sanitizeForSheets()` prefixes fields starting with `=`, `+`, `-`, `@`, `\t`, `\r` with tab character
- **XSS in Telegram messages** (`submit.js`): `escapeHtml()` on all user-supplied fields before HTML parse_mode
- **AI Asset Score system prompt**: Updated to v1.0 — 5 dimensions (Traction/Revenue/Transferability/Automation/Risk), JSON key `"dimensions"` (was `"criteria"`)
- **Security headers** (`_headers`): CSP, HSTS, X-Frame-Options: DENY, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, COOP
- **CSP `frame-src https://www.youtube.com`**: added for YouTube embed
- **`.env` moved** out of deploy directory (was leaked 2026-08-14, rotated)
- **`_redirects`** blocks direct access to `.env`, `.git/*`, `wrangler.toml`

**Previously implemented:**
- CORS: ALLOWED_ORIGINS whitelist in both functions
- Input validation: max field length, required fields check
- No secrets in frontend code

---

## 14. Known Issues

| Issue | Severity | Notes |
|-------|----------|-------|
| `grades/*.html` — outdated nav | Medium | 9 grade card files excluded from `_apply_nav.py` script |
| `/post-a-bounty/` duplicate | Low | Same as `/post-ai-bounty/` — needs 301 redirect |
| `listings.json` scores format | Low | Still uses old 7-criteria format (traffic/revenue/etc) instead of 5-dimension v1.0 |
| X/Twitter agent — 402 | External | developer.twitter.com account needs balance top-up |
| Contact form | Medium | Not connected to any endpoint |
| Hero video locale mapping | Medium | Currently single video ID (VZ09NYqBjdI, RU Shorts). No EN/RU switching yet |
| `target="_blank"` links | Low | Not all have `rel="noopener noreferrer"` |

---

## 15. Incomplete / Pending Parts

- **Operator Course content**: sales page exists (`/operator-course/`), 18 lessons not written. Payment (Stripe/Gumroad) not connected.
- **Locale EN/RU switching**: UI exists (language selector), but hero video doesn't switch by locale. No separate EN video yet.
- **Marketplace listings**: `listings.json` has demo data only (`is_demo: true`). No real listings.
- **Contact form**: present in UI, not wired to any backend.
- **Analytics events**: no custom event tracking (only CF Web Analytics pageviews).
- **RKN notification** (Russian data regulator): pending — waiting on founder's TIN + SMZ/FL status.
