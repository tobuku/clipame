# Clipame Clipper Sourcing Plan

## Priority Order (richest data sources first)

### Tier 1: Freelance Marketplaces (highest proof-of-work density)

**Fiverr** -- search queries:
- "podcast clipping" "short form video editing" "tiktok editor"
- "youtube shorts editor" "reels editor" "clip editor"
- Filter: video editing category, 4+ star rating, portfolio visible
- Data yield: handle, portfolio, pricing, reviews, response time, sample work

**Upwork** -- search queries:
- "short form video editor" "podcast clipper" "reels editor"
- "tiktok content creator" "youtube shorts"
- Filter: 90%+ job success, has portfolio
- Data yield: handle, hourly rate, job history, skills, portfolio

**Contra** -- search queries:
- "video editor" "content creator" "short form"
- Data yield: portfolio, rate, skills, social links

**Note**: These platforms require browser automation (JS-rendered pages).
Use Playwright or Puppeteer for scraping. Respect rate limits and ToS.

### Tier 2: Social/Creator Platforms

**TikTok** -- search:
- Hashtags: #clipper #clippingtok #podcastclips #editortok #clippingcommunity
- Bio keywords: "clipper" "editor for hire" "DM for edits"
- Data yield: handle, follower count, sample clips, bio (contact info sometimes)

**YouTube** -- search:
- "podcast clips" channels, "highlights" channels
- Clipper showcase/portfolio channels
- Data yield: channel URL, subscriber count, upload frequency, sample clips

**Instagram** -- search:
- Hashtags: #clipper #videoeditor #shortformeditor #podcastclipper
- Bio: "editor" "clipper" "DM for rates"
- Data yield: handle, bio, portfolio highlights, contact button

**X/Twitter** -- search:
- "clipper available" "looking for clipping work" "hiring clippers"
- Clipping community accounts
- Data yield: handle, bio, pinned portfolio, DM availability

### Tier 3: Clipping Community Ecosystems

**Whop** -- communities:
- Clipping Culture, Clip Flow, ClipAffiliates communities
- Member directories within these communities (if public)
- Data yield: handle, community membership, skill level

**Discord** -- servers:
- Clipping-focused servers (found via Disboard, Discord.me)
- Freelance editor servers
- Data yield: handle, portfolio links shared in channels

**Reddit** -- subreddits:
- r/CreatorServices, r/forhire, r/VideoEditing
- Search: "clipper" "short form editor" "podcast clips"
- Data yield: handle, portfolio link, rate, availability

### Tier 4: Portfolio Networks

**Behance** -- search:
- "video editing" "motion graphics" "short form content"
- Data yield: portfolio, real name, social links, location

**Dribbble** -- search:
- "video" "motion" (limited video editor presence)

**Personal sites** -- found via:
- Linktree/Carrd links from social bios
- Google: "clipper portfolio" "short form editor portfolio"

### Tier 5: Agency/Directory Cross-References

**Existing directories**: Jorgovan, Quill, Overlap, Increditors
- Re-screen the 49 unverified candidates from v1 harvest
- Extract individual clippers (not agencies) for the clipper directory

---

## Batch Workflow

Each sourcing batch follows this pipeline:

```
1. DISCOVER
   - Run search queries on target platform
   - Capture: name, handle, profile URL, visible data
   - Raw output: candidates_batch_YYYYMMDD.csv

2. ENRICH
   - Visit each candidate's profile
   - Capture: portfolio links, social links, pricing, services
   - Cross-reference handle across platforms (identity gate)
   - Find published contact info (never guess)

3. VALIDATE
   - Run python validate.py on the batch
   - HTTP liveness check on all URLs
   - Email MX check on all emails
   - De-duplicate against existing records

4. TIER
   - Tier A -> merge into main clippers_screened.csv
   - Tier B -> enrichment queue (try to fill the one missing gate)
   - Reject -> log with reason, never silently drop

5. REPORT
   - Batch summary: records added, tier breakdown, sources, countries
   - Updated confidence assessment
```

---

## Volume Targets

| Milestone | Tier A Clippers | Timeline |
|---|---|---|
| Seed | 10 | Week 1 |
| Foundation | 50 | Week 4 |
| Credible | 200 | Month 2-3 |
| Authority | 500 | Month 4-6 |

## Consent Strategy

**Approach: public-data listing with opt-out**

- List clippers based on publicly available information
- Each listing includes a "Claim This Profile" and "Request Removal" link
- Clippers who claim their profile get consent_status = confirmed
- Removal requests honored within 48h, consent_status = declined
- This mirrors how G2, Clutch, and Crunchbase operate

**Why not opt-in only**: would limit growth to only clippers who find and submit to Clipame. At scale, most directory sites list first and let people claim. Legal basis: publicly available information, legitimate interest, with easy opt-out.
