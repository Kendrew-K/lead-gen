"""Lead data sources.

Google Places is the primary source for these targets (Indonesian contractors /
interior designers) — it reliably returns a phone number. Email is best-effort
only: most of this segment has no company domain, so `scrape_email` and
`hunter_email` fire just for the minority that do.
"""
import re
import time

import requests
from bs4 import BeautifulSoup

PLACES_URL = "https://places.googleapis.com/v1/places:searchText"
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_UA = {"User-Agent": "Mozilla/5.0"}


def places_search(query, api_key, max_results=20):
    """Text-search the Google Places API (v1). Returns a list of business dicts."""
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": (
            "places.id,places.displayName,places.internationalPhoneNumber,places.websiteUri,"
            "places.formattedAddress,places.rating,places.userRatingCount,nextPageToken"
        ),
    }
    out, token = [], None
    while len(out) < max_results:
        body = {"textQuery": query, "pageSize": min(20, max_results - len(out))}
        if token:
            body["pageToken"] = token
        r = requests.post(PLACES_URL, headers=headers, json=body, timeout=30)
        r.raise_for_status()
        data = r.json()
        for p in data.get("places", []):
            out.append({
                "place_id": p.get("id", ""),
                "name": p.get("displayName", {}).get("text", ""),
                "phone": p.get("internationalPhoneNumber", ""),
                "website": p.get("websiteUri", ""),
                "address": p.get("formattedAddress", ""),
                "rating": p.get("rating", ""),
                "reviews": p.get("userRatingCount", ""),
            })
        token = data.get("nextPageToken")
        if not token:
            break
        time.sleep(2)  # a fresh nextPageToken needs a moment before it's valid
    return out[:max_results]


DETAILS_URL = "https://places.googleapis.com/v1/places/"
# What the drafter actually reads to find a pain point. Reviews are the payload:
# the lead's own customers name the gap for you, so no hook has to be invented.
_DETAILS_FIELDS = (
    "id,displayName,rating,userRatingCount,reviews,editorialSummary,"
    "regularOpeningHours.weekdayDescriptions,primaryTypeDisplayName,businessStatus"
)


def place_id_for(name, address, api_key):
    """Look up a place id by name+address. For leads found before ids were stored."""
    headers = {"Content-Type": "application/json", "X-Goog-Api-Key": api_key,
               "X-Goog-FieldMask": "places.id"}  # id-only mask stays on the free SKU
    try:
        r = requests.post(PLACES_URL, headers=headers,
                          json={"textQuery": f"{name} {address}", "pageSize": 1}, timeout=20)
        r.raise_for_status()
        places = r.json().get("places", [])
    except requests.RequestException:
        return ""
    return places[0].get("id", "") if places else ""


def place_details(place_id, api_key):
    """Fetch reviews + summary for one place. Returns {} on any failure.

    Called per-kept-lead rather than folded into the search mask: reviews sit in a
    pricier Places SKU, so we only pay for leads that survived the review step.
    """
    if not place_id or not api_key:
        return {}
    try:
        r = requests.get(DETAILS_URL + place_id,
                         headers={"X-Goog-Api-Key": api_key, "X-Goog-FieldMask": _DETAILS_FIELDS},
                         timeout=20)
        r.raise_for_status()
        d = r.json()
    except requests.RequestException:
        return {}
    return {
        "rating": d.get("rating", ""),
        "reviews_count": d.get("userRatingCount", ""),
        "type": d.get("primaryTypeDisplayName", {}).get("text", ""),
        "status": d.get("businessStatus", ""),
        "summary": d.get("editorialSummary", {}).get("text", ""),
        "hours": d.get("regularOpeningHours", {}).get("weekdayDescriptions", []),
        "review_quotes": [
            {
                "rating": rv.get("rating", ""),
                "when": rv.get("relativePublishTimeDescription", ""),
                "text": (rv.get("originalText") or rv.get("text") or {}).get("text", "")[:600],
            }
            for rv in d.get("reviews", [])
        ],
    }


_SINCE_RE = re.compile(r"(?:sejak|since|est\.?|berdiri)\s*(19|20)\d{2}", re.I)
_SOCIAL_RE = re.compile(r"https?://(?:www\.)?(instagram|facebook|tiktok|linkedin)\.com/[^\s\"'<>]+", re.I)


def site_profile(url):
    """Scrape a lead's homepage for positioning signal: what they say they do, and
    which channels they already run. Absence is signal too (no site, no Instagram)."""
    if not url:
        return {}
    try:
        r = requests.get(url, timeout=10, headers=_UA)
        r.raise_for_status()
    except requests.RequestException:
        return {"reachable": False}
    soup = BeautifulSoup(r.text, "html.parser")
    desc = soup.find("meta", attrs={"name": "description"})
    since = _SINCE_RE.search(soup.get_text(" "))
    socials = sorted({m.group(0).rstrip("/") for m in _SOCIAL_RE.finditer(r.text)})
    return {
        "reachable": True,
        "title": (soup.title.string or "").strip()[:200] if soup.title else "",
        "description": (desc.get("content", "") if desc else "")[:300],
        "headings": [h.get_text(" ", strip=True)[:120]
                     for h in soup.find_all(["h1", "h2"])[:12] if h.get_text(strip=True)],
        "socials": socials[:6],
        "has_form": bool(soup.find("form")),
        "since": since.group(0) if since else "",
    }


def wa_number(phone):
    """'+62 21 1234-567' -> '62211234567' (digits only, for a wa.me link). '' if none."""
    return re.sub(r"\D", "", phone or "")


def domain_of(url):
    """'https://www.studio.co.id/about' -> 'studio.co.id'. '' if not a URL."""
    m = re.search(r"https?://([^/]+)", url or "")
    return m.group(1).replace("www.", "") if m else ""


def scrape_email(url):
    """Return the first plausible email from a site's home/contact page, or ''."""
    if not url:
        return ""
    for path in ("", "/contact", "/kontak", "/about"):
        try:
            r = requests.get(url.rstrip("/") + path, timeout=8, headers=_UA)
        except requests.RequestException:
            continue
        if r.status_code != 200:
            continue
        text = BeautifulSoup(r.text, "html.parser").get_text(" ") + " " + r.text
        for m in EMAIL_RE.findall(text):
            if not re.search(r"\.(png|jpg|jpeg|gif|webp|svg)$", m, re.I):
                return m
    return ""


def hunter_email(domain, api_key):
    """Hunter domain-search fallback. Returns (email, name), preferring senior roles."""
    if not domain or not api_key:
        return "", ""
    try:
        r = requests.get(
            "https://api.hunter.io/v2/domain-search",
            params={"domain": domain, "api_key": api_key, "limit": 5},
            timeout=20,
        )
        r.raise_for_status()
        emails = r.json().get("data", {}).get("emails", [])
    except requests.RequestException:
        return "", ""
    # decision-maker first: the whole point is to reach the boss, not info@
    emails.sort(key=lambda e: 0 if e.get("seniority") in ("executive", "senior") else 1)
    if emails:
        e = emails[0]
        name = " ".join(filter(None, [e.get("first_name"), e.get("last_name")]))
        return e.get("value", ""), name
    return "", ""


if __name__ == "__main__":
    # Self-check: exercises parsing/regex without any API key.
    assert wa_number("+62 21 1234-567") == "62211234567"
    assert domain_of("https://www.studio.co.id/about") == "studio.co.id"
    assert domain_of("not a url") == ""
    assert EMAIL_RE.search("halo hi@studio.co.id ya").group() == "hi@studio.co.id"
    print("sources.py self-check OK")
