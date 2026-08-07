"""
De-duplication module for Clipame directory records.

Detects potential duplicates by:
1. Normalized handle matching
2. Normalized display name matching
3. Canonical URL matching
4. Domain extraction + comparison
"""

import re
from urllib.parse import urlparse


def normalize_handle(handle):
    """Normalize a social handle for comparison."""
    if not handle:
        return None
    handle = handle.strip().lower()
    handle = handle.lstrip("@")
    # Remove common suffixes
    handle = re.sub(r"[._-]+$", "", handle)
    return handle if handle else None


def normalize_name(name):
    """Normalize a display name for comparison."""
    if not name:
        return None
    name = name.strip().lower()
    # Remove non-alphanumeric chars
    name = re.sub(r"[^a-z0-9\s]", "", name)
    # Collapse whitespace
    name = re.sub(r"\s+", " ", name).strip()
    return name if name else None


def extract_domain(url):
    """Extract domain from URL for comparison."""
    if not url:
        return None
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Strip www.
        domain = re.sub(r"^www\.", "", domain)
        return domain if domain else None
    except Exception:
        return None


def find_duplicates(records):
    """
    Find potential duplicate pairs in a list of record dicts.
    Returns list of (id_a, id_b) tuples.
    """
    dupes = set()
    n = len(records)

    for i in range(n):
        for j in range(i + 1, n):
            a = records[i]
            b = records[j]
            id_a = a.get("id", f"row_{i}")
            id_b = b.get("id", f"row_{j}")

            # Check handle match
            h_a = normalize_handle(a.get("handle", ""))
            h_b = normalize_handle(b.get("handle", ""))
            if h_a and h_b and h_a == h_b:
                dupes.add((id_a, id_b))
                continue

            # Check name match
            n_a = normalize_name(a.get("display_name", ""))
            n_b = normalize_name(b.get("display_name", ""))
            if n_a and n_b and n_a == n_b:
                dupes.add((id_a, id_b))
                continue

            # Check canonical URL match
            url_a = a.get("canonical_presence_url", "").strip()
            url_b = b.get("canonical_presence_url", "").strip()
            if url_a and url_b and url_a == url_b:
                dupes.add((id_a, id_b))
                continue

            # Check domain match (weaker signal -- only flag if names also similar)
            d_a = extract_domain(url_a)
            d_b = extract_domain(url_b)
            if d_a and d_b and d_a == d_b and d_a not in (
                "fiverr.com", "upwork.com", "contra.com", "tiktok.com",
                "instagram.com", "youtube.com", "twitter.com", "x.com",
                "linkedin.com", "behance.net", "dribbble.com"
            ):
                dupes.add((id_a, id_b))

    return sorted(dupes)


if __name__ == "__main__":
    # Quick self-test
    test_records = [
        {"id": "1", "display_name": "John Doe", "handle": "johndoe",
         "canonical_presence_url": "https://fiverr.com/johndoe"},
        {"id": "2", "display_name": "john doe", "handle": "JohnDoe",
         "canonical_presence_url": "https://upwork.com/johndoe"},
        {"id": "3", "display_name": "Jane Smith", "handle": "janesmith",
         "canonical_presence_url": "https://janesmith.com"},
    ]
    dupes = find_duplicates(test_records)
    print(f"Found {len(dupes)} duplicate pair(s):")
    for a, b in dupes:
        print(f"  {a} <-> {b}")
