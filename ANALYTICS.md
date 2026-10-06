# Clipame.com GA4 Event Tracking

Measurement ID: `G-CVYJRDK6JZ`
Implementation: `js/main.js` (centralized, no GTM) + `thank-you.html` (generate_lead)
Deployed: 2026-10-06

## Event Taxonomy (6 events)

| Event Name | Trigger | Parameters |
|---|---|---|
| `affiliate_click` | Click on any `[data-affiliate-vendor]` link | `affiliate_vendor`, `affiliate_placement`, `affiliate_featured` |
| `generate_lead` | Thank-you page load after confirmed Formspree submission | `form_name`, `lead_type` |
| `search` | Search bar submit (Enter key or button click) | `search_term` |
| `directory_filter` | Click on any `.filter-btn` | `filter_value` |
| `modal_open` | Click on any `[data-modal]` trigger | `modal_id` |
| `cta_click` | Click on `.nav__cta`, `.cta-banner .btn`, or `.hero .btn` (non-affiliate) | `cta_name`, `cta_location` |

## generate_lead Architecture

### Conversion flow
1. User submits form (native Formspree POST)
2. Formspree receives and accepts submission
3. Formspree redirects to `thank-you.html?type=<slug>` via `_next` hidden field
4. Thank-you page validates `type` against allowlist
5. `generate_lead` fires once per type per session (sessionStorage guard)

### Success signal
The redirect to `thank-you.html` occurs ONLY after Formspree successfully processes the submission. The `_next` hidden field is a standard Formspree feature. No form architecture changes were required -- forms still use native `method="POST"`.

### Form type mapping (22 forms across 12 files)

| `?type=` slug | `form_name` | `lead_type` | Forms using it |
|---|---|---|---|
| `newsletter` | `newsletter` | `newsletter` | Footer newsletter (12 pages) + index section newsletter |
| `listing` | `directory_submission` | `directory_submission` | Submit clipper (index, clippers), submit agency, submit tool, submit community |
| `job` | `job_post` | `job_post` | Post job modal (jobs.html) |
| `contact` | `contact` | `contact_request` | Contact form (about.html) |
| `campaign` | `campaign` | `campaign_request` | Campaign brief (campaigns.html) |
| `lead` | `clipper_lead` | `clipper_lead` | Clipper lead form (clippers.html) |

If `type` is missing or not in the allowlist, a generic `generate_lead` fires with no `form_name` or `lead_type` parameters.

### Duplicate prevention
Uses `sessionStorage` to prevent repeated `generate_lead` events from page refresh. Key format: `clipame_lead_<type>`. Each form type can fire once per browser session. Different form types within one session are tracked independently.

**Limitation:** sessionStorage clears on tab close. A user who submits, closes the tab, and re-opens the thank-you URL from browser history would generate a duplicate. This is rare and acceptable. Private browsing or sessionStorage-disabled browsers fire on every load.

### Thank-you page (`thank-you.html`)
- `<meta name="robots" content="noindex, nofollow">` -- excluded from search
- Not in `sitemap.xml`
- Not linked from site navigation
- Footer omits newsletter form to avoid redirect loop
- GA4 snippet loads normally; `generate_lead` fires via inline script after `main.js`

## Initialization Architecture

Event listeners initialize regardless of GA4 availability. A lightweight helper checks `window.gtag` at event time:

```js
function trackEvent(name, params) {
  if (typeof window.gtag === 'function') {
    window.gtag('event', name, params);
  }
}
```

- Listeners always register (no early abort)
- Missing or blocked GA4 never breaks site behavior
- Events fail silently if gtag is unavailable
- No console errors, no retry loops, no blocking

Script order: GA4 gtag snippet loads in `<head>` (async). `main.js` loads at end of `<body>`. By event time, gtag is available if not blocked.

## Data Attributes on Affiliate Links

Added to all affiliate `<a>` tags on `tools.html` and `best-ai-clipping-tools.html`:

- `data-affiliate-vendor` — vendor slug: `invideo`, `flixier`, `opus-clip`, `filmora`, `descript`, `submagic`
- `data-affiliate-placement` — context:
  - `tool_directory_card` — vendor name link in tool card (tools.html)
  - `tool_directory_cta` — "Try [Vendor]" CTA in tool card pricing line (tools.html)
  - `listicle_comparison` — vendor name in comparison table (best-ai-clipping-tools.html)
  - `listicle_card` — vendor name in vendor review card heading (best-ai-clipping-tools.html)
  - `listicle_cta` — "Try [Vendor]" CTA in vendor review pricing line (best-ai-clipping-tools.html)

Featured card detection: JS checks if the link is inside `.tool-card--featured` and sets `affiliate_featured: true/false`.

## Affiliate Link Inventory

### tools.html (12 links, 6 vendors)
| Vendor | Network | Links |
|---|---|---|
| InVideo AI | Impact (sjv.io) | card name + pricing CTA |
| Flixier | FirstPromoter (fpr=) | card name + pricing CTA |
| Opus Clip | Direct (via=aj) | card name + pricing CTA |
| Filmora | LinkSynergy | card name + pricing CTA |
| Descript | PartnerStack | card name + pricing CTA |
| Submagic | Direct (via=aj-8f1d06) | card name + pricing CTA |

### best-ai-clipping-tools.html (12 links, 4 vendors)
| Vendor | Links |
|---|---|
| Opus Clip | comparison table + vendor card title + pricing CTA |
| Descript | comparison table + vendor card title + pricing CTA |
| Submagic | comparison table + vendor card title + pricing CTA |
| Flixier | comparison table + vendor card title + pricing CTA |

## Duplicate Event Prevention

### affiliate_click vs cta_click
The CTA click handler explicitly checks `if (cta.dataset.affiliateVendor) return;` before firing. Affiliate links match the affiliate handler only. CTA buttons (nav, hero, banner) match the CTA handler only. No affiliate link uses `.nav__cta`, `.cta-banner .btn`, or `.hero .btn` classes. One click = one event.

### generate_lead refresh guard
sessionStorage key per form type prevents duplicate firing on page refresh. See "Duplicate prevention" above.

## GA4 Admin Configuration Required

### 1. Key Events (Admin > Data display > Key events)

**Primary Key Event:**
- `generate_lead` -- mark as Key Event (confirmed submission success via Formspree redirect)

**Commercial measurement event (do NOT mark as Key Event yet):**
- `affiliate_click` -- available for reporting and funnel analysis; promote to Key Event later if business reporting benefits from that classification

**Diagnostic engagement events:**
- `search`, `directory_filter`, `modal_open`, `cta_click`

### 2. Custom Dimensions (Admin > Data display > Custom definitions)

| Parameter | Custom Dimension Required | Scope | Business Reason |
|---|---|---|---|
| `affiliate_vendor` | Yes | Event | Revenue attribution by vendor; compare which affiliate programs convert |
| `affiliate_placement` | Yes | Event | Compare card-name clicks vs CTA clicks vs comparison-table clicks to optimize layout |
| `form_name` | Yes | Event | Identify which form types generate leads; compare newsletter vs listing vs lead volume |
| `lead_type` | Yes | Event | Group forms by business category for funnel analysis |
| `filter_value` | Yes | Event | Understand which directory categories users browse; informs content investment |
| `cta_name` | Yes | Event | Track which CTAs drive engagement; compare "List Your Profile" vs "Find a Clipper" etc. |
| `affiliate_featured` | No | -- | Boolean; useful in Explorations filter but not worth a dimension slot |
| `search_term` | No | -- | GA4 exposes `search_term` natively for the built-in `search` event name |
| `modal_id` | No | -- | Low cardinality (3 unique values); viewable in event detail without a custom dimension |
| `cta_location` | No | -- | Low cardinality (nav/hero/cta_banner/other); viewable in event detail without a custom dimension |

**6 custom dimensions to create:**
1. Affiliate Vendor (`affiliate_vendor`, Event scope)
2. Affiliate Placement (`affiliate_placement`, Event scope)
3. Form Name (`form_name`, Event scope)
4. Lead Type (`lead_type`, Event scope)
5. Filter Value (`filter_value`, Event scope)
6. CTA Name (`cta_name`, Event scope)

### 3. Debug View
To verify events are firing correctly:
1. Install GA Debugger Chrome extension
2. Or add `#gtm.debug` to any page URL
3. Check GA4 Admin > Data display > DebugView for real-time event stream

## Formspree Configuration

No Formspree dashboard changes are required. The `_next` hidden field is an HTML-level feature that works on all plans. Each form specifies its own redirect URL via:

```html
<input type="hidden" name="_next" value="https://clipame.com/thank-you.html?type=<slug>">
```

**Optional dashboard backup:** In Formspree dashboard > Form Settings > Custom Redirect, you can set a default redirect URL of `https://clipame.com/thank-you.html` as a fallback. This would catch any form that somehow lacks a `_next` field. The HTML `_next` field takes precedence over the dashboard setting when present.

**Plan note:** On Formspree's free plan, a reCAPTCHA interstitial may appear between submission and redirect. The `_next` redirect still occurs after the CAPTCHA clears. On paid plans, CAPTCHA can be disabled for a direct redirect.

## Privacy

- No PII is collected in any event parameter
- No email addresses, names, phone numbers, or contact messages are sent
- No form field contents or Formspree payload data are captured
- `search_term` contains only user-entered directory search queries (e.g., "football clipper"), not personal data
- `cta_name` contains only button label text (e.g., "List Your Profile"), not user input
- `form_name` and `lead_type` contain only predefined slugs from a hardcoded allowlist, not user input
- The `?type=` query parameter on `thank-you.html` is validated against an allowlist before use; malformed values are silently dropped
- All tracking respects browser ad blockers (gtag simply won't load; listeners still work but events are silently dropped)
- No cookies are set beyond GA4's default `_ga` and `_ga_*` cookies
