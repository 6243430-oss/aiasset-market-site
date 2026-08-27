# AIAsset.Market — External Release Audit

**Audit date:** 2026-08-21  
**Package:** `AIAssetMarket_REVIEW.zip`  
**Verdict:** **NO-GO for production launch in current state**

The homepage direction is good, but the archive is not a coherent production-ready site yet. The main problem is not one bug: the new homepage was placed on top of a large legacy site that still uses the old product concept, old terminology, old dark design, dead CTAs, and incomplete backend wiring.

---

# 1. Executive summary

## Critical blockers

1. **The form backend exists, but the frontend forms do not.**
   - The package contains `functions/submit.js` and `functions/api/preview-grade.js`.
   - Across the 64 HTML files there are **zero `<form>` elements**.
   - There are also **no frontend calls** to `/submit` or `/api/preview-grade`.
   - Therefore the submission flows described in `REVIEW_NOTES.md` are not actually wired in this package.

2. **Hundreds of old CTA links are dead after the homepage redesign.**
   - The new homepage contains no anchors such as `#free-audit`, `#listings`, `#request-form`, `#operator-form`, `#preview-grade`.
   - Legacy pages still contain **391 links** to those removed homepage anchors.
   - The largest group is `/#free-audit` — **298 occurrences**.

3. **A shared navigation link is broken on 49 pages.**
   - `/ai-asset-packaging-sprint/` is linked from **49 HTML pages**.
   - That route does not exist in the archive.

4. **The site is still mostly the old Pirate/Marketplace product.**
   - **59 of 64 HTML pages** visibly contain `Pirate Grade` or `Pirate Score`.
   - **51 pages** still contain `Marketplace`.
   - Only the homepage uses the approved new navigation/visual language.

5. **Cloudflare “sensitive file blocking” in `_redirects` is invalid.**
   - The file uses rules such as:
     - `/.env /404.html 404`
     - `/wrangler.toml /404.html 404`
   - Cloudflare Pages `_redirects` supports redirect status codes 301/302/303/307/308; arbitrary 404 rewrites are not supported.
   - These rules cannot be relied on to protect deployment files.
   - Production output should contain only public assets instead of trying to hide source/config with redirect rules.

6. **Apps Script is a missing security-critical component.**
   - `submit.js` forwards form data to `APPS_SCRIPT_URL`.
   - The Apps Script source is not included in the audit package.
   - Therefore storage logic, authorization, validation, spreadsheet behavior and data handling cannot be audited end-to-end.

7. **Current SSRF protection has an IPv6 bypass.**
   - `preview-grade.js` checks regexes against `URL.hostname`.
   - For IPv6 literals `URL.hostname` includes brackets, e.g. `[::1]`, so the current `^::1$`, `^fc`, `^fd` patterns do not match.
   - `fe80::/10` is also not blocked.
   - The URL-fetching code needs a proper IP/hostname validation strategy before production.

---

# 2. Architecture / functionality

## 2.1 Routes

The archive contains **64 HTML files**, not a small single-site surface.

There are three major generations of UI:

- **Homepage:** new light design.
- **48 pages:** shared old dark purple navigation/layout.
- **9 grade pages:** separate older grade-report navigation.
- Privacy/Consent/Terms have additional standalone layouts.

This means the current site is visually and structurally fragmented.

## 2.2 Broken internal routing

### Missing route
`/ai-asset-packaging-sprint/`  
Referenced from 49 pages.

**Action:** either:
- create the real page, or
- remove the service, or
- redirect to the correct replacement.

### Duplicate bounty routes
Both exist:
- `/post-a-bounty/`
- `/post-ai-bounty/`

Both are in `sitemap.xml`.

`REVIEW_NOTES.md` says a 301 redirect is needed, but `_redirects` does not contain it.

**Action:** choose one canonical route and 301 the other.

### Dead homepage fragments
Legacy routes link to removed homepage UI:

- `/#free-audit`
- `/#listings`
- `/#/listings`
- `/#request-form`
- `/#/request-form`
- `/#operator-form`
- `/#/operator-form`
- `/#preview-grade`
- `/#sell`

Total: **391 dead root-fragment links**.

This is a launch blocker.

---

# 3. Product / content consistency

## 3.1 New positioning vs old site

Approved direction:
- AI Asset Boutique
- Acquire
- Sell & Package
- Research & Advisory
- AI Asset Score
- AI Asset Economy

But most legacy pages still say:
- Marketplace
- Weekly Drop
- Pirate Grade
- Pirate Score
- Free Grade
- Grades Database
- Operator Fit
- Bounties
- Scouts
- Drops

### Quantified
- `Pirate Grade` / `Pirate Score`: visible on **59/64 pages**
- `Marketplace`: visible on **51/64 pages**

This is not a minor copy cleanup. It is the main information architecture problem.

## 3.2 Homepage metadata contradicts homepage positioning

`index.html` visually says:
> Together, We Build the AI Asset Economy.

But `<title>` still says:
> Buy & Sell AI Assets | AI Business Marketplace

and the OG title still uses:
> AI Business Marketplace

**Action:** align SEO metadata with boutique/advisory positioning.

## 3.3 Methodology is internally inconsistent

`methodology/index.html` has been partly migrated to:
- AI Asset Score v1.0
- 5 dimensions

But the same page still contains:
- `Pirate Grade`
- `Preview Grade`
- old Grade language
- old process claims
- old CTA links
- legacy comparison claims

The page also contains unsupported-looking operational claims such as:
- `93.6% Rejected · 47 reviewed · 3 approved`
- `1–4 wks · Review time · IC of 2+`
- “No single-reviewer grades”
- specific calibration/deal claims

These must be either substantiated or removed.

## 3.4 Grade cards use the old scoring system

The static `grades/*.html` pages still use the old multi-criterion Pirate Grade model, e.g.:
- Works Without the Founder
- Customer Type
- Revenue Proof
- Operator Fit, etc.

This contradicts AI Asset Score v1.0.

If these reports are historical examples:
- clearly label them as legacy/historical,
- preferably noindex them,
- or migrate them to the new methodology.

If they are not real verified cases:
- remove them from production.

## 3.5 Unverified claims / trust risk

Several old pages contain claims that create substantial trust risk if they are not documented:

Examples:
- “Every week we review 20–40 AI projects”
- “47 reviewed · 3 approved”
- “546 operators”
- “Takes 72 hours from submit to first offer”
- “revenue and transfer notes verified”
- current active buyer requests
- specific grade reports with specific MRR and “confirmed Stripe history”

**Rule for production:** if there is no evidence behind a number, case, buyer request or verification claim, remove it.

The new boutique positioning becomes stronger when the site is smaller and factual.

---

# 4. Recommended information architecture

Do not try to redesign and maintain 60+ pages at once.

Recommended core release surface:

1. `/` — Homepage
2. `/acquire/` or repurpose `/marketplace/` into a buyer/acquisition page
3. `/sell-ai-asset/` — Seller journey
4. `/services/`
5. `/methodology/`
6. `/insights/`
7. `/academy/`
8. `/about/`
9. `/contact/`
10. `/privacy/`
11. `/terms/`
12. `/consent/`

The dozens of SEO landing pages can remain later **only if**:
- copy is accurate,
- they use the same header/footer/design,
- CTAs work,
- they are not doorway/thin pages,
- they no longer carry the old Pirate/Marketplace narrative.

For the immediate launch, reducing scope will produce a stronger site faster than repainting 60 pages.

---

# 5. Forms and real workflows

## Critical finding

There are **0 HTML forms** in the archive.

There are also no frontend `fetch()` calls to:
- `/submit`
- `/api/preview-grade`

Therefore these backend routes are currently orphaned from the supplied frontend.

`REVIEW_NOTES.md` says the following are live:
- AI Asset Score
- Submit an Asset
- Post a Bounty
- Operator Signup
- Watchlist
- Contact (pending)

That description does not match the code package.

## Required real workflows for release

### Buyer
Homepage → Acquire → buyer brief/contact → submit → success state.

### Seller
Homepage → I own an asset → seller form → validation → submit → success state.

### AI Asset Score
Methodology/score page → controlled inputs → `/api/preview-grade` → validated result → error/retry state.

### Contact
Contact page or modal → real endpoint → success/error state.

Do not publish buttons that lead to dead anchors.

---

# 6. Backend security

## 6.1 `functions/api/preview-grade.js`

### CRITICAL / HIGH

#### SSRF IPv6 bypass
Current checks:
```js
/^::1$/
/^fc|^fd/
```

But WHATWG URL parsing returns IPv6 hostnames with brackets such as:
```text
[::1]
[fd00::1]
```

The regexes therefore do not block these forms.

Also add:
- `fe80::/10`
- IPv4-mapped IPv6
- other non-public address classes as appropriate.

**Best approach:** reject IP literals entirely unless there is a real requirement to score raw IP URLs, and implement robust public-host validation.

#### DNS rebinding / hostname resolution
The code only checks the literal hostname string. A public-looking hostname can resolve to a private address.

The protection should not be described as complete SSRF protection until hostname resolution/public-address enforcement is solved.

#### Unlimited response body read
The code does:
```js
const html = await res.text();
```
and truncates only afterwards.

A server can return a very large response and force the Worker to read it into memory.

Add:
- Content-Type allowlist (`text/html`, `text/plain`, etc.)
- Content-Length upper bound where available
- streamed body read with a hard byte cap
- timeout
- redirect limit / current no-follow behavior

#### Weak backend input validation
Only `url` and `pitch` lengths are checked.

Not properly type/range checked:
- `asset_type`
- `mrr`
- `revenue`
- `contracts`
- `assets_included`
- `users`

A direct caller can submit strings/objects instead of numeric values and inject content into the prompt.

Add strict schema validation.

#### LLM output is trusted blindly
The server parses JSON but does not validate:
- ranges,
- required fields,
- dimensions sum,
- band values,
- value ranges,
- string lengths.

Add a server-side schema and clamp/reject invalid results.

#### Provider error leakage
The endpoint returns:
```js
detail: errText.slice(0, 200)
```

Do not expose raw OpenRouter errors to public clients. Log them server-side and return a generic request ID/error.

#### OpenRouter privacy is not enforced in code
The Privacy Policy says Preview Grade data is not stored.

The request code does not enforce:
- Zero Data Retention
- `data_collection: deny`
- provider restrictions

If the product wants to promise non-retention, enforce it in OpenRouter workspace/request settings and document the actual behavior.

Also note that the LLM receives more than “URL”:
- revenue,
- MRR,
- contracts,
- assets included,
- users,
- pitch,
- scraped page content.

Privacy wording must reflect this.

## 6.2 `functions/submit.js`

### CRITICAL / HIGH

#### Unknown `sheet` values are accepted
```js
const required = REQUIRED[sheet] || [];
```

If `sheet` is not recognized, required fields become empty and the payload is still forwarded.

Reject every sheet/form type outside a strict allowlist.

#### Arbitrary payload fields are forwarded
There is no per-form field allowlist.

Use explicit schemas per form and discard/reject unknown fields.

#### Type crash
This line assumes required fields are strings:
```js
payload[f].trim()
```

A malicious JSON value can be an object or number and cause an exception.

Validate types before using values.

#### Apps Script errors are swallowed
The code catches network errors and still returns:
```json
{"ok": true}
```

It also does not check `response.ok`.

Result: the user can see success while the lead was never stored.

This is a release blocker for forms.

Required:
- `const res = await fetch(...)`
- check status
- parse/validate expected response
- return failure to frontend when storage fails
- optionally retry safely/idempotently

#### Telegram notification is not awaited
The Telegram fetch is started and abandoned.

Use `context.waitUntil()` for non-critical notification work or await it where required.

#### Bot protection is weak
Honeypot + 3-second load field is easy to bypass.

Add Cloudflare Turnstile to public submission and AI-score endpoints, especially because OpenRouter calls cost money.

#### KV rate limit is non-atomic
KV read-modify-write is eventually consistent and not an atomic counter.

This is acceptable only as a basic abuse throttle, not a strong billing/security boundary.

Use Cloudflare's rate limiting/WAF/Turnstile or another atomic mechanism for expensive endpoints.

---

# 7. Missing Apps Script audit

The source code behind `APPS_SCRIPT_URL` is missing.

This prevents verification of:

- which sheets can be selected,
- whether arbitrary worksheet names are accepted,
- server-side sanitization,
- formula execution behavior,
- authorization,
- replay handling,
- data retention,
- response status semantics,
- logging,
- access permissions,
- cross-border storage behavior.

**Before final security approval, include the Apps Script source.**

---

# 8. Cloudflare configuration

## 8.1 `_redirects` cannot provide the 404 blocking currently assumed

The file contains rules with `404` status codes.

Cloudflare Pages `_redirects` only supports redirect status codes:
- 301
- 302
- 303
- 307
- 308

Do not rely on these rules to hide:
- `.env`
- `wrangler.toml`
- backup files
- source files

### Correct architecture
Use a separate deploy/public directory containing only assets intended to be public.

Do not deploy the repository root as the public directory.

## 8.2 `_headers` does not apply to Pages Functions

Cloudflare explicitly documents that `_headers` applies to static asset responses, not Pages Functions responses.

If API responses need custom security headers, attach them in the Functions themselves.

## 8.3 CSP is weakened by `unsafe-inline`

Current CSP contains:
```text
script-src 'self' 'unsafe-inline'
style-src 'self' 'unsafe-inline'
```

The site currently relies heavily on inline scripts/event handlers.

For stronger XSS protection:
- move scripts to static JS files,
- remove inline `onclick`,
- remove `unsafe-inline` from `script-src`,
- use hashes/nonces only if necessary.

## 8.4 Production output separation

Current configuration says:
```toml
pages_build_output_dir = "."
```

This makes source-vs-public separation too easy to get wrong.

Recommended:
```text
/public
/functions
wrangler.toml
```

and deploy only the intended static output.

---

# 9. Privacy / legal consistency

Not legal advice; these are implementation mismatches.

## 9.1 Cloudflare analytics contradiction
`REVIEW_NOTES.md` says Cloudflare Web Analytics is used.

24 HTML files explicitly contain the Cloudflare beacon.

Privacy English text says:
> No third-party analytics.

That is factually inconsistent.

## 9.2 Cookie banner is inaccurate / ineffective
Homepage says:
> We use cookies...

But implementation stores a `cookie_consent` value in `localStorage`.

Accept/Reject does not actually enable or disable analytics or another service.

Either:
- remove the fake consent banner and accurately describe required storage, or
- implement real consent gating.

## 9.3 YouTube missing from privacy processor disclosure
Homepage embeds YouTube on click.

Privacy processor list should reflect actual YouTube/Google embed behavior, especially if standard `youtube.com` rather than privacy-enhanced embed is used.

## 9.4 OpenRouter disclosure is incomplete
Privacy describes OpenRouter as processing the asset URL.

Code sends all of:
- URL
- MRR/profit
- annual revenue
- contract backlog
- included assets/IP
- users
- pitch
- scraped site content

This needs to be disclosed.

## 9.5 Operator name transliteration is inconsistent
Terms:
- `Maxim Napoikin`

Privacy:
- `Maxim Napoykin`

Russian:
- `Напойкин Максим`

Choose one official English transliteration everywhere.

---

# 10. Homepage UX / accessibility

The new homepage is the strongest part of the package.

However:

## Video duration
UI says:
> Watch 1:35

The supplied English video is approximately **1:16**.

Update the label.

## Video trigger is not keyboard accessible
The clickable video is a `div role="button"` without `tabindex`.

Use a real `<button>` or add full keyboard support.

## Modal lacks dialog semantics
Missing:
- `role="dialog"`
- `aria-modal="true"`
- accessible close label
- focus trap
- focus return after close

## Escape handler is broken
Current code calls:
```js
closeModal({})
```

`closeModal()` then accesses `e.target.classList`, which can throw because `target` is undefined.

Fix Escape handling explicitly.

## Language video mapping
No real locale system exists in this package.

EN/RU mapping still needs implementation.

The English YouTube ID currently used is:
`VZ09NYqBjdI`

Russian ID can be added when uploaded.

---

# 11. Accessibility

Basic static markup is generally simple, which is good, but release still needs:

- consistent keyboard navigation
- correct focus states
- modal focus trap
- Escape close
- real buttons for button behavior
- skip-link
- consistent landmarks
- accessible menu state (`aria-expanded`)
- reduced-motion support
- contrast check on all legacy pages
- accessible form error summaries once forms are rebuilt

A full WCAG pixel/runtime pass should be done after the pages are unified.

---

# 12. Design consistency

This is currently a release blocker for brand quality.

Detected design generations:
- new light homepage
- large old dark/purple site
- old grade report pages
- separate legal page styling

48 pages share the old dark navigation.

9 grade pages have a completely separate old grade-report design.

**Action:** establish shared design tokens/components:
- header
- footer
- typography
- buttons
- cards
- forms
- alerts
- modal
- grid
- spacing
- responsive breakpoints

Then migrate only the pages that survive the route cleanup.

Do not spend time polishing dead legacy routes before deciding whether they should remain.

---

# 13. SEO

## Findings

- Homepage title/OG still says Marketplace.
- `methodology/` is missing from `sitemap.xml`.
- both bounty routes are in sitemap.
- only `privacy/` has hreflang declarations.
- there is no functioning EN/RU routing system across the site.
- 26 pages have incomplete Open Graph/Twitter metadata.
- `robots.txt` allows everything, including legacy grade/demo pages.
- old Pirate pages remain indexable.
- legacy fragment CTAs are broken.

## Recommendation

First fix IA/content/routing, then regenerate:
- sitemap
- canonical map
- redirects
- title/description
- OG/Twitter
- hreflang
- noindex rules

Do not optimize 60 outdated pages before deciding which pages are part of the product.

---

# 14. Public/private data model

There is no authentication system.

Therefore every deployed HTML/JSON file should be treated as public.

If future private deal pages contain:
- seller identity
- financial evidence
- buyer notes
- diligence memos
- contact details

they must not be shipped as static HTML/JSON and merely hidden from navigation.

Private deal flow will require server-side authorization/access control.

---

# 15. Other cleanup

- 59 `target="_blank"` links lack `rel="noopener noreferrer"`.
- comments at top of `preview-grade.js` still describe the old 7-criteria output.
- `listings.json` / `listings_ru.json` use legacy score structure and are currently orphaned.
- `assets.json` is also not consumed by the supplied frontend.
- `wrangler.toml` uses the same KV namespace ID for production and preview.
- compatibility date is old (`2024-09-23`); update and test intentionally.
- Contact in homepage is currently `mailto:` rather than a site workflow.
- `About` links to Methodology rather than a real About page.

---

# 16. Recommended execution order for Claude

## Phase 1 — stop the bleeding
1. Decide the final route list.
2. Remove/redirect dead legacy routes.
3. Fix all dead fragment CTAs.
4. Remove Pirate terminology globally.
5. Remove unsupported/fake claims.
6. Choose Marketplace vs Boutique language; use Boutique/Acquire consistently.
7. Fix duplicate bounty route.
8. Fix missing Packaging Sprint route/link.

## Phase 2 — make workflows real
9. Build real Buyer form.
10. Build real Seller form.
11. Build real Contact form.
12. Reconnect AI Asset Score frontend.
13. Add success/error/loading states.
14. Include Apps Script source and fix storage response handling.

## Phase 3 — secure backend
15. Fix SSRF validation.
16. Add strict input schemas.
17. Add response schema validation for LLM.
18. Add body/content size limits.
19. Add Turnstile / real abuse protection.
20. Enforce OpenRouter ZDR/data-collection policy if promised.
21. Stop exposing provider errors.
22. Fix Apps Script forwarding reliability.

## Phase 4 — unify product
23. Apply approved light design to surviving routes.
24. Build shared header/footer.
25. Implement real EN/RU architecture.
26. Add locale video mapping.
27. Update Privacy/Terms factual consistency.
28. Fix accessibility.

## Phase 5 — release engineering
29. Separate source and deploy/public output.
30. Replace invalid `_redirects` security assumptions.
31. Regenerate sitemap/robots/canonicals.
32. Complete SEO metadata.
33. Run link checker.
34. Run responsive screenshots.
35. Run Lighthouse/accessibility.
36. Re-package `AIAssetMarket_FINAL_REVIEW.zip`.

---

# 17. Release verdict

## Current package
**NO-GO**

## Why
The new homepage is usable as a visual direction, but the rest of the site is still a different product and many user actions are currently dead. The backend also has security and reliability issues that need correction before collecting real seller/buyer data.

## What is good
- New homepage positioning is much clearer.
- Terms are closer to the new boutique/advisory role.
- Five-dimension AI Asset Score is a better direction.
- Secrets are not present in frontend code.
- Basic rate limiting and server-side endpoints exist.
- Formula and Telegram escaping were considered.
- Security headers exist for static pages.

The project does not need another conceptual redesign. It needs **scope reduction, migration, wiring and hardening**.
