# Clipame.com GA4 Event Tracking

Measurement ID: `G-CVYJRDK6JZ`
Implementation: `js/main.js` (centralized, no GTM)
Deployed: 2026-10-06

## Event Taxonomy (5 events)

| Event Name | Trigger | Parameters |
|---|---|---|
| `affiliate_click` | Click on any `[data-affiliate-vendor]` link | `affiliate_vendor`, `affiliate_placement`, `affiliate_featured` |
| `search` | Search bar submit (Enter key or button click) | `search_term` |
| `directory_filter` | Click on any `.filter-btn` | `filter_value` |
| `modal_open` | Click on any `[data-modal]` trigger | `modal_id` |
| `cta_click` | Click on `.nav__cta`, `.cta-banner .btn`, or `.hero .btn` (non-affiliate) | `cta_name`, `cta_location` |

### generate_lead (not yet implemented)

All forms use native Formspree POST (`method="POST"` to `formspree.io/f/mkoldeja`), which navigates the browser away on submit. There is no client-side success signal. The `submit` event fires before navigation begins and does not confirm delivery.

To implement `generate_lead` reliably, forms must be converted to fetch-based submission with success/error handling. Until then, form submissions are not tracked in GA4. Formspree's own dashboard shows submission counts as a stopgap.

Forms that need conversion for success tracking:
- Newsletter signup (footer, all pages + index.html section)
- Submit Clipper modal (index.html, clippers.html)
- Submit Agency modal (agencies.html)
- Submit Tool modal (tools.html)
- Submit Community modal (communities.html)
- Post Job modal (jobs.html)
- Contact form (about.html, inline)
- Campaign brief (campaigns.html, multi-step)
- Clipper lead form (clippers.html)

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

## GA4 Admin Configuration Required

### 1. Key Events (Admin > Data display > Key events)

**Primary Key Event:**
- `generate_lead` — mark as Key Event when form success tracking is implemented

**Commercial measurement event (do NOT mark as Key Event yet):**
- `affiliate_click` — available for reporting and funnel analysis; promote to Key Event later if business reporting benefits from that classification

**Diagnostic engagement events:**
- `search`, `directory_filter`, `modal_open`, `cta_click`

### 2. Custom Dimensions (Admin > Data display > Custom definitions)

| Parameter | Custom Dimension Required | Scope | Business Reason |
|---|---|---|---|
| `affiliate_vendor` | Yes | Event | Revenue attribution by vendor; compare which affiliate programs convert |
| `affiliate_placement` | Yes | Event | Compare card-name clicks vs CTA clicks vs comparison-table clicks to optimize layout |
| `affiliate_featured` | No | — | Boolean; useful in Explorations filter but not worth a dimension slot. Use event parameter filter instead. |
| `filter_value` | Yes | Event | Understand which directory categories users browse; informs content investment |
| `cta_name` | Yes | Event | Track which CTAs drive engagement; compare "List Your Profile" vs "Find a Clipper" etc. |
| `search_term` | No | — | GA4 exposes `search_term` natively for the built-in `search` event name |
| `modal_id` | No | — | Low cardinality (3 unique values); viewable in event detail without a custom dimension |
| `cta_location` | No | — | Low cardinality (nav/hero/cta_banner/other); viewable in event detail without a custom dimension |

**4 custom dimensions to create:**
1. Affiliate Vendor (`affiliate_vendor`, Event scope)
2. Affiliate Placement (`affiliate_placement`, Event scope)
3. Filter Value (`filter_value`, Event scope)
4. CTA Name (`cta_name`, Event scope)

### 3. Debug View
To verify events are firing correctly:
1. Install [GA Debugger](https://chrome.google.com/webstore/detail/google-analytics-debugger/jnkmfdileelhofjcijamephohjechhna) Chrome extension
2. Or add `#gtm.debug` to any page URL
3. Check GA4 Admin > Data display > DebugView for real-time event stream

## Privacy

- No PII is collected in any event parameter
- No email addresses, names, phone numbers, or contact messages are sent
- No form field contents or Formspree payload data are captured
- `search_term` contains only user-entered directory search queries (e.g., "football clipper"), not personal data
- `cta_name` contains only button label text (e.g., "List Your Profile"), not user input
- All tracking respects browser ad blockers (gtag simply won't load; listeners still work but events are silently dropped)
- No cookies are set beyond GA4's default `_ga` and `_ga_*` cookies
