-- Clipame Directory Schema v2
-- SQLite / PostgreSQL compatible DDL

CREATE TABLE IF NOT EXISTS listings (
    -- Identity & Presence
    id                      TEXT PRIMARY KEY,
    listing_type            TEXT NOT NULL CHECK (listing_type IN ('clipper', 'agency', 'tool')),
    display_name            TEXT NOT NULL,
    real_name               TEXT,
    handle                  TEXT,
    canonical_presence_url  TEXT NOT NULL,
    portfolio_url           TEXT,
    sample_clip_urls        TEXT,       -- pipe-delimited URLs
    personal_site_url       TEXT,

    -- Platforms & Social Proof
    platforms_clipped        TEXT,       -- pipe-delimited: TikTok|Reels|Shorts|X
    youtube_url              TEXT,
    tiktok_url               TEXT,
    instagram_url            TEXT,
    x_url                    TEXT,
    linkedin_url             TEXT,
    linktree_url             TEXT,
    fiverr_url               TEXT,
    upwork_url               TEXT,
    contra_url               TEXT,
    notable_clients          TEXT,

    -- Commercial
    services                 TEXT,       -- pipe-delimited
    published_rate           TEXT,
    pricing_model            TEXT CHECK (pricing_model IS NULL OR pricing_model IN (
                                'per_clip', 'monthly', 'per_view', 'cpm', 'project', 'hourly', 'custom'
                             )),
    availability_status      TEXT CHECK (availability_status IS NULL OR availability_status IN (
                                'available', 'limited', 'unavailable', 'unknown'
                             )),
    turnaround               TEXT,

    -- Contact & Lead Routing
    business_email           TEXT,
    contact_form_url         TEXT,
    preferred_contact_method TEXT,
    lead_routing_target      TEXT,

    -- Location
    country                  TEXT,
    state_province           TEXT,
    city                     TEXT,
    timezone                 TEXT,

    -- Provenance & QA
    source_url_1             TEXT NOT NULL,
    source_url_2             TEXT,
    evidence_notes           TEXT,
    gate_presence_live       INTEGER NOT NULL DEFAULT 0,  -- 0=FALSE, 1=TRUE
    gate_proof_of_work       INTEGER NOT NULL DEFAULT 0,
    gate_contact             INTEGER NOT NULL DEFAULT 0,
    gate_recent              INTEGER NOT NULL DEFAULT 0,
    gate_identity            INTEGER NOT NULL DEFAULT 0,
    gate_niche               INTEGER NOT NULL DEFAULT 0,
    tier                     TEXT NOT NULL CHECK (tier IN ('A', 'B', 'reject')),
    reject_reason            TEXT,
    confidence_score         INTEGER NOT NULL CHECK (confidence_score BETWEEN 1 AND 5),
    validation_date          TEXT NOT NULL,  -- YYYY-MM-DD
    last_active_date         TEXT,           -- YYYY-MM-DD
    consent_status           TEXT DEFAULT 'none' CHECK (consent_status IN (
                                'none', 'requested', 'confirmed', 'declined'
                             )),

    -- Constraints
    CHECK (tier != 'reject' OR reject_reason IS NOT NULL)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_listing_type ON listings(listing_type);
CREATE INDEX IF NOT EXISTS idx_tier ON listings(tier);
CREATE INDEX IF NOT EXISTS idx_country ON listings(country);
CREATE INDEX IF NOT EXISTS idx_display_name ON listings(display_name);
CREATE INDEX IF NOT EXISTS idx_handle ON listings(handle);
CREATE INDEX IF NOT EXISTS idx_validation_date ON listings(validation_date);

-- De-duplication helper view
CREATE VIEW IF NOT EXISTS potential_dupes AS
SELECT a.id AS id_a, b.id AS id_b, a.display_name, a.handle
FROM listings a
JOIN listings b ON a.id < b.id
    AND (
        (a.handle IS NOT NULL AND LOWER(a.handle) = LOWER(b.handle))
        OR LOWER(a.display_name) = LOWER(b.display_name)
        OR (a.canonical_presence_url IS NOT NULL
            AND a.canonical_presence_url = b.canonical_presence_url)
    );
