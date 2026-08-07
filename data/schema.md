# Clipame Directory Schema v2

## Overview

This schema defines the data model for all Clipame directory listings. Every record represents one entity (clipper, agency, or tool) and carries full provenance and validation metadata.

## Listing Types

- `clipper` -- Individual short-form video editors / podcast clippers
- `agency` -- Clipping agencies and managed distribution networks
- `tool` -- AI clipping tools and SaaS platforms

---

## Field Reference

### Identity & Presence

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Unique identifier (slug: lowercase, hyphens) |
| `listing_type` | enum | yes | `clipper` \| `agency` \| `tool` |
| `display_name` | string | yes | Public-facing name |
| `real_name` | string | no | Legal/real name (only if publicly stated) |
| `handle` | string | no | Primary social handle (without @) |
| `canonical_presence_url` | url | yes | The primary link posted on their listing |
| `portfolio_url` | url | no | Dedicated portfolio page |
| `sample_clip_urls` | list[url] | no | Direct links to sample clips (pipe-delimited in CSV) |
| `personal_site_url` | url | no | Personal website |

### Platforms & Social Proof

| Field | Type | Required | Description |
|---|---|---|---|
| `platforms_clipped` | list[string] | no | Platforms they create content for: TikTok, Reels, Shorts, X, etc. (pipe-delimited) |
| `youtube_url` | url | no | YouTube channel or profile |
| `tiktok_url` | url | no | TikTok profile |
| `instagram_url` | url | no | Instagram profile |
| `x_url` | url | no | X/Twitter profile |
| `linkedin_url` | url | no | LinkedIn profile |
| `linktree_url` | url | no | Linktree or similar link hub |
| `fiverr_url` | url | no | Fiverr gig page |
| `upwork_url` | url | no | Upwork profile |
| `contra_url` | url | no | Contra profile |
| `notable_clients` | string | no | Publicly stated clients or accolades |

### Commercial

| Field | Type | Required | Description |
|---|---|---|---|
| `services` | list[string] | no | e.g., podcast clipping, faceless editing, UGC (pipe-delimited) |
| `published_rate` | string | no | As published: "$50/clip", "$500/mo", "from $3 CPM" |
| `pricing_model` | enum | no | `per_clip` \| `monthly` \| `per_view` \| `cpm` \| `project` \| `hourly` \| `custom` |
| `availability_status` | enum | no | `available` \| `limited` \| `unavailable` \| `unknown` |
| `turnaround` | string | no | Stated turnaround time: "24h", "2-3 days" |

### Contact & Lead Routing

| Field | Type | Required | Description |
|---|---|---|---|
| `business_email` | email | no | Published email only -- never guessed |
| `contact_form_url` | url | no | URL of their contact form |
| `preferred_contact_method` | string | no | email, DM, form, etc. |
| `lead_routing_target` | string | no | Where Clipame forwards leads (email/form/DM handle) |

### Location

| Field | Type | Required | Description |
|---|---|---|---|
| `country` | string | no | Country (ISO 3166 name or code) |
| `state_province` | string | no | State or province |
| `city` | string | no | City |
| `timezone` | string | no | IANA timezone if public |

### Provenance & QA

| Field | Type | Required | Description |
|---|---|---|---|
| `source_url_1` | url | yes | Primary source where we found/verified this entity |
| `source_url_2` | url | no | Second independent source for identity confirmation |
| `evidence_notes` | string | no | What we actually saw/verified (free text) |
| `gate_presence_live` | bool | yes | Canonical URL returns HTTP 200 |
| `gate_proof_of_work` | bool | yes | 3+ public sample clips or portfolio page viewed |
| `gate_contact` | bool | yes | Working email, DM, or contact form exists |
| `gate_recent` | bool | yes | Activity within last 6-12 months |
| `gate_identity` | bool | yes | Same name/handle confirmed across 2+ sources |
| `gate_niche` | bool | yes | Genuinely does clipping/short-form (confirmed) |
| `tier` | enum | yes | `A` (all 6 gates pass) \| `B` (missing 1) \| `reject` (missing 2+) |
| `reject_reason` | string | no | Why rejected (required if tier = reject) |
| `confidence_score` | int | yes | 1-5 scale |
| `validation_date` | date | yes | YYYY-MM-DD of last validation |
| `last_active_date` | date | no | Approximate date of last observed activity |
| `consent_status` | enum | no | `none` \| `requested` \| `confirmed` \| `declined` |

---

## Tiering Logic

- **Tier A**: All 6 gate booleans are TRUE. Eligible to publish on Clipame.
- **Tier B**: Exactly 1 gate is FALSE. Goes to enrichment queue.
- **Reject**: 2+ gates are FALSE. Logged to reject list with reason. Never silently dropped.

## CSV Conventions

- Encoding: UTF-8 with BOM
- Delimiter: comma
- Quoting: double-quote fields containing commas or newlines
- List fields (sample_clip_urls, platforms_clipped, services): pipe-delimited within the field
- Boolean fields: `TRUE` / `FALSE`
- Dates: `YYYY-MM-DD`
- Sort: by `display_name` ascending
- One record per entity, de-duplicated by normalized handle + domain + display name
