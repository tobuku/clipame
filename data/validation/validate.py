"""
Clipame Directory Validation Module

Runs the 6-gate validation checks on clipper records:
1. Presence live (HTTP 200)
2. Proof of work (3+ sample clips or portfolio URL live)
3. Contact path exists (email MX + syntax, or contact form URL)
4. Recent activity (last_active_date within 12 months)
5. Identity consistency (2+ independent source URLs)
6. Niche match (manual flag -- script checks field is set)

Usage:
    python validate.py input.csv output.csv [--reject-log rejects.csv]
"""

import csv
import sys
import argparse
from datetime import datetime, timedelta
from url_check import check_url_live
from email_check import check_email_valid
from dedup import find_duplicates


def parse_args():
    parser = argparse.ArgumentParser(description="Validate Clipame directory records")
    parser.add_argument("input_csv", help="Input CSV file path")
    parser.add_argument("output_csv", help="Output CSV file path (validated)")
    parser.add_argument("--reject-log", default="rejects.csv",
                        help="Reject log CSV path (default: rejects.csv)")
    parser.add_argument("--skip-http", action="store_true",
                        help="Skip HTTP liveness checks (for offline testing)")
    parser.add_argument("--recency-months", type=int, default=12,
                        help="Max months since last activity (default: 12)")
    return parser.parse_args()


def gate_presence_live(row, skip_http=False):
    """Gate 1: canonical_presence_url returns HTTP 200."""
    url = row.get("canonical_presence_url", "").strip()
    if not url:
        return False
    if skip_http:
        return bool(url)
    return check_url_live(url)


def gate_proof_of_work(row, skip_http=False):
    """Gate 2: 3+ sample clips OR a live portfolio URL."""
    clips = row.get("sample_clip_urls", "").strip()
    portfolio = row.get("portfolio_url", "").strip()

    if clips:
        clip_list = [u.strip() for u in clips.split("|") if u.strip()]
        if len(clip_list) >= 3:
            return True

    if portfolio:
        if skip_http:
            return True
        return check_url_live(portfolio)

    return False


def gate_contact(row):
    """Gate 3: working email (syntax + MX) OR contact form URL."""
    email = row.get("business_email", "").strip()
    form_url = row.get("contact_form_url", "").strip()

    if email and check_email_valid(email):
        return True
    if form_url:
        return True
    # Check if any platform DM is viable (has a social URL)
    for field in ["tiktok_url", "instagram_url", "x_url", "linkedin_url",
                  "fiverr_url", "upwork_url", "contra_url"]:
        if row.get(field, "").strip():
            return True
    return False


def gate_recent(row, max_months=12):
    """Gate 4: last_active_date within max_months."""
    last_active = row.get("last_active_date", "").strip()
    if not last_active:
        return False
    try:
        active_date = datetime.strptime(last_active, "%Y-%m-%d")
        cutoff = datetime.now() - timedelta(days=max_months * 30)
        return active_date >= cutoff
    except ValueError:
        return False


def gate_identity(row):
    """Gate 5: 2+ independent source URLs."""
    s1 = row.get("source_url_1", "").strip()
    s2 = row.get("source_url_2", "").strip()
    return bool(s1) and bool(s2)


def gate_niche(row):
    """Gate 6: niche match flag -- checks services or evidence_notes mention clipping."""
    services = row.get("services", "").strip().lower()
    evidence = row.get("evidence_notes", "").strip().lower()
    niche_flag = row.get("gate_niche", "").strip().upper()

    # If manually set, trust it
    if niche_flag in ("TRUE", "1"):
        return True

    # Auto-detect from services/evidence
    clipping_keywords = [
        "clip", "short-form", "shortform", "short form", "reels", "shorts",
        "tiktok edit", "podcast clip", "repurpos", "faceless", "ugc"
    ]
    text = f"{services} {evidence}"
    return any(kw in text for kw in clipping_keywords)


def compute_tier(gates):
    """Compute tier from gate results."""
    false_count = sum(1 for v in gates.values() if not v)
    if false_count == 0:
        return "A"
    elif false_count == 1:
        return "B"
    else:
        return "reject"


def build_reject_reason(gates):
    """Build human-readable reject reason from failed gates."""
    failed = [name for name, passed in gates.items() if not passed]
    if not failed:
        return ""
    return "Failed gates: " + ", ".join(failed)


def validate_record(row, skip_http=False, recency_months=12):
    """Run all 6 gates on a single record. Returns updated row dict.

    If a gate is already set to TRUE in the input (manually verified),
    trust it and skip recomputation for that gate.
    """
    gate_checks = {
        "gate_presence_live": lambda: gate_presence_live(row, skip_http),
        "gate_proof_of_work": lambda: gate_proof_of_work(row, skip_http),
        "gate_contact": lambda: gate_contact(row),
        "gate_recent": lambda: gate_recent(row, recency_months),
        "gate_identity": lambda: gate_identity(row),
        "gate_niche": lambda: gate_niche(row),
    }

    gates = {}
    for gate_name, check_fn in gate_checks.items():
        existing = row.get(gate_name, "").strip().upper()
        if existing == "TRUE":
            gates[gate_name] = True  # trust manual verification
        else:
            gates[gate_name] = check_fn()

    tier = compute_tier(gates)
    reject_reason = build_reject_reason(gates) if tier == "reject" else ""

    # Update row
    for gate_name, passed in gates.items():
        row[gate_name] = "TRUE" if passed else "FALSE"
    row["tier"] = tier
    row["reject_reason"] = reject_reason
    row["validation_date"] = datetime.now().strftime("%Y-%m-%d")

    # Set confidence score based on tier + data completeness
    filled = sum(1 for v in row.values() if v and str(v).strip())
    total = len(row)
    fill_ratio = filled / total if total > 0 else 0
    if tier == "A":
        row["confidence_score"] = "5" if fill_ratio > 0.7 else "4"
    elif tier == "B":
        row["confidence_score"] = "3"
    else:
        row["confidence_score"] = "2" if fill_ratio > 0.3 else "1"

    return row


def main():
    args = parse_args()

    with open(args.input_csv, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    if not rows:
        print("No records found in input CSV.")
        sys.exit(0)

    print(f"Loaded {len(rows)} records from {args.input_csv}")

    # Validate each record
    validated = []
    rejects = []
    for i, row in enumerate(rows):
        row = validate_record(row, args.skip_http, args.recency_months)
        if row["tier"] == "reject":
            rejects.append(row)
        validated.append(row)
        tier_label = row["tier"]
        print(f"  [{i+1}/{len(rows)}] {row.get('display_name', '?')} -> Tier {tier_label}")

    # De-duplicate
    dupes = find_duplicates(validated)
    if dupes:
        print(f"\nWARNING: {len(dupes)} potential duplicate pair(s) found:")
        for a, b in dupes:
            print(f"  - {a} <-> {b}")

    # Write output
    with open(args.output_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(validated)

    print(f"\nWrote {len(validated)} records to {args.output_csv}")

    # Write reject log
    if rejects:
        with open(args.reject_log, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rejects)
        print(f"Wrote {len(rejects)} rejects to {args.reject_log}")

    # Summary
    tier_a = sum(1 for r in validated if r["tier"] == "A")
    tier_b = sum(1 for r in validated if r["tier"] == "B")
    tier_r = sum(1 for r in validated if r["tier"] == "reject")
    print(f"\nSummary: {tier_a} Tier A, {tier_b} Tier B, {tier_r} Rejected")


if __name__ == "__main__":
    main()
