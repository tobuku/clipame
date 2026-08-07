# Clipame Lead-Gen & Monetization Spec

## Recommended v1 Model: Free-to-List + Featured Placement + Pay-Per-Lead

### Why This Model

- **Free listing** grows supply fast (clippers have no barrier to entry)
- **Featured placement** is low-friction revenue (clippers pay for visibility, not leads)
- **Pay-per-lead** aligns cost with value (clippers pay only when they get work)
- No escrow, no payment processing, no take-rate complexity in v1

### Phased Rollout

**Phase 1 (NOW): Directory + Affiliate**
- Free listings for all clippers/agencies/tools
- Affiliate links on tool cards (Opus Clip 25%, CapCut 35%, Descript $25/sub)
- Revenue: affiliate commissions only
- Cost: $0 (static site on GitHub Pages)

**Phase 2: Featured Placement ($19-$49/mo)**
- "Clipame Verified" badge (tied to Tier A validation)
- Top-of-category placement in search/filter results
- Profile analytics (views, click-through)
- Revenue target: 20 paying clippers x $29/mo = $580/mo

**Phase 3: Pay-Per-Qualified-Lead ($5-$15/lead)**
- Contact form on each clipper profile routes through Clipame
- Lead captured, validated, forwarded to clipper
- Clipper charged per qualified lead delivered
- Revenue target: 100 leads/mo x $10 = $1,000/mo

**Phase 4: Buyer-Side (Future)**
- Brands/creators pay for job postings or bulk outreach
- Campaign routing commissions

---

## Qualified Lead Definition

A lead counts as "qualified" (billable) when ALL of these are true:

1. **Real identity**: buyer provides real name, company/channel, and working email
2. **Specific need**: describes a concrete project (not "just browsing")
3. **Budget signal**: states a budget range or is willing to discuss pricing
4. **Platform match**: the project matches the clipper's stated services/platforms
5. **Unique**: not a duplicate of a lead submitted in the last 30 days

Leads that fail any of these are forwarded for free (goodwill) but not billed.

---

## Lead Schema

### Lead Record Fields

| Field | Type | Description |
|---|---|---|
| `lead_id` | string | Unique ID |
| `created_at` | datetime | When submitted |
| `clipper_id` | string | Target clipper's listing ID |
| `buyer_name` | string | Person submitting |
| `buyer_email` | email | Contact email |
| `buyer_company` | string | Company/channel name |
| `project_type` | enum | podcast_clipping, ugc, faceless, brand_clips, other |
| `platforms_needed` | list | TikTok, Reels, Shorts, X, etc. |
| `description` | text | Project description |
| `budget_range` | string | e.g., "$500-$1000/mo" |
| `timeline` | string | e.g., "Starting next week" |
| `status` | enum | new, delivered, opened, responded, won, lost, expired |
| `qualified` | bool | Passes qualification gates |
| `disqualify_reason` | string | If not qualified, why |
| `delivered_at` | datetime | When forwarded to clipper |
| `response_deadline` | datetime | 48h SLA from delivery |
| `outcome_date` | datetime | When won/lost recorded |

---

## Lead Handoff Flow

```
Buyer visits clipper profile on Clipame
    |
    v
Submits "Contact This Clipper" form
(name, email, company, project type, budget, description)
    |
    v
Clipame validates lead:
  - Email syntax + MX check
  - Dedupe against last 30 days
  - Required fields filled
  - Auto-qualify or flag for review
    |
    v
Lead stored in Clipame DB with status "new"
    |
    v
Forwarded to clipper's lead_routing_target
(email with lead details + "Reply within 48h" SLA)
    |
    v
Clipper responds (directly to buyer, CC Clipame relay)
    |
    v
Track: delivered -> opened -> responded -> won/lost
```

---

## Anti-Leakage Strategy

The risk: buyers see clipper profile, note their social handle, and DM them directly -- bypassing Clipame.

**Mitigation layers (progressive):**

1. **Friction reduction**: make the Clipame contact form faster/easier than finding and DMing on TikTok. Pre-fill project details, send structured brief.

2. **Value-add in the handoff**: Clipame's forwarded lead includes a structured project brief the clipper can respond to. Raw DMs don't provide this.

3. **Delayed reveal**: initially show clipper's portfolio and skills but NOT their social handles until the buyer submits a lead. (Requires testing -- may hurt trust.)

4. **Attribution tracking**: use UTM-tagged links on clipper social profiles that point back to Clipame. Track how many profile views convert to leads vs. bounce.

5. **Clipper incentive**: clippers who respond to leads within 48h get boosted in search results. Creates a flywheel where Clipame leads are higher quality than cold DMs.

**v1 approach**: layers 1, 2, and 5. Don't hide social handles (would damage trust and the "neutral directory" positioning). Accept some leakage as the cost of building supply-side trust.

---

## Lead SLA & Dispute Handling

- **Response SLA**: clippers must respond to qualified leads within 48 hours
- **Non-response penalty**: after 3 missed SLAs, clipper drops from "Featured" placement
- **Buyer complaint**: if buyer reports clipper didn't respond, lead fee is waived
- **Clipper dispute**: if clipper claims lead was unqualified, manual review within 72h
- **Refund policy**: leads proven unqualified (spam, wrong niche, fake identity) are credited back

---

## MVP Build Outline (Static Site Compatible)

Since Clipame is currently a static HTML site on GitHub Pages, the v1 lead capture can work with existing tools:

1. **Contact form per clipper**: add a "Contact This Clipper" button on each clipper card that opens a modal with Formspree form. Include a hidden field with the clipper's ID.

2. **Formspree routing**: use Formspree's `_replyto` and `_cc` fields to forward leads to the clipper's email while keeping a copy on the Clipame Formspree dashboard.

3. **Lead tracking**: Formspree submissions serve as the lead log. Export periodically to CSV for analysis.

4. **Analytics**: GA events on form opens and submissions track conversion funnel.

**When to migrate off static**: when lead volume exceeds ~50/month or when pay-per-lead billing requires automated tracking. At that point, move to a lightweight backend (Supabase + Vercel, or similar).

---

## Unit Economics

### Featured Placement (Phase 2)

| Metric | Value |
|---|---|
| Price | $29/mo |
| Target subscribers | 20 |
| Monthly revenue | $580 |
| Cost (hosting) | $0 |
| Margin | ~100% |

### Pay-Per-Lead (Phase 3)

| Metric | Value |
|---|---|
| Lead price | $10 |
| Target leads/mo | 100 |
| Monthly revenue | $1,000 |
| Qualification rate | ~60% (60 billable of 100) |
| Adjusted revenue | $600 |
| Cost (email/infra) | ~$20/mo |
| Margin | ~97% |

### Affiliate (Phase 1, ongoing)

| Tool | Commission | Est. monthly referrals | Monthly revenue |
|---|---|---|---|
| Opus Clip | 25% recurring | 5 | $24 |
| CapCut | 35% recurring | 3 | $10 |
| Descript | $25/sub | 2 | $50 |
| InVideo | 50% monthly | 1 | $15 |
| Total est. | | | ~$100 |

### Combined v1-v3 Target: $1,200-$1,500/mo

---

## Open Decisions for Neal/Paul

1. Show clipper social handles publicly, or gate behind lead form?
2. Formspree endpoint per clipper, or single endpoint with clipper ID routing?
3. Featured placement pricing: $19, $29, or $49/mo?
4. Lead price: flat $10 or tiered by project budget?
5. When to build a real backend vs. stay static?
