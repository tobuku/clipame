"""
URL liveness checker for Clipame validation.

Checks if a URL returns HTTP 200 (or redirect to 200).
Uses a browser-like User-Agent to avoid bot blocks.
"""

import urllib.request
import urllib.error
import ssl


# Timeout in seconds per request
TIMEOUT = 15

# User-Agent to avoid bot blocks
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def check_url_live(url, timeout=TIMEOUT):
    """
    Check if a URL is live (returns 2xx status).
    Returns True if live, False otherwise.
    """
    if not url or not url.startswith(("http://", "https://")):
        return False

    try:
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", USER_AGENT)
        # Allow self-signed certs (some small sites)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        response = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return 200 <= response.status < 400
    except (urllib.error.HTTPError, urllib.error.URLError):
        # Try GET as fallback (some servers block HEAD)
        try:
            req = urllib.request.Request(url, method="GET")
            req.add_header("User-Agent", USER_AGENT)
            response = urllib.request.urlopen(req, timeout=timeout, context=ctx)
            return 200 <= response.status < 400
        except Exception:
            return False
    except Exception:
        return False


def batch_check_urls(urls, timeout=TIMEOUT):
    """Check multiple URLs. Returns dict of {url: is_live}."""
    results = {}
    for url in urls:
        results[url] = check_url_live(url, timeout)
    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python url_check.py <url> [url2] [url3] ...")
        sys.exit(1)
    for url in sys.argv[1:]:
        live = check_url_live(url)
        status = "LIVE" if live else "DOWN"
        print(f"  {status}: {url}")
