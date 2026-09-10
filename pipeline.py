"""The lead pipeline: find -> (review) -> draft -> output.

`find` and `draft` are split so you can eyeball the lead list (leads.csv) before
spending any LLM tokens or writing messages.
"""
import csv
import json
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

import config
from sources import (places_search, wa_number, scrape_email, hunter_email, domain_of,
                     place_details, place_id_for, site_profile)

COLS = [
    "name", "category", "city", "phone", "wa_link", "email", "contact_name",
    "confidence", "whatsapp", "email_subject", "email_body", "website", "address",
]


def load_campaign(name):
    with open(config.CAMPAIGNS / f"{name}.json", encoding="utf-8") as f:
        return json.load(f)


def discover(categories, cities, limit=20):
    """Query Places for each category x city. Dedupe by (name, phone)."""
    seen, out = set(), []
    for cat in categories:
        for city in cities:
            print(f"  Places: {cat} in {city}")
            for b in places_search(f"{cat} in {city}", config.GOOGLE_PLACES_API_KEY, limit):
                # same phone = same business even if the listing name differs slightly
                key = b["phone"] or b["name"]
                if key in seen:
                    continue
                seen.add(key)
                b["category"], b["city"] = cat, city
                out.append(b)
    return out


def _enrich_one(b):
    """Fill wa/email/snippet/confidence for one business. Network-bound (scrape + Hunter)."""
    b["wa"] = wa_number(b.get("phone"))
    email, name = "", ""
    if b.get("website"):
        email = scrape_email(b["website"])
        if not email:
            email, name = hunter_email(domain_of(b["website"]), config.HUNTER_API_KEY)
    b["email"], b["contact_name"] = email, name
    b["snippet"] = f'{b.get("category", "")} di {b.get("city", "")}, {b.get("reviews", "?")} ulasan'
    b["confidence"] = ("wa" if b["wa"] else "") + ("+email" if b["email"] else "")
    return b


def enrich(companies):
    """Enrich all leads concurrently — it's I/O-bound, so threads collapse the wall time."""
    with ThreadPoolExecutor(max_workers=8) as pool:
        done = list(pool.map(_enrich_one, companies))
    print(f"  enriched {len(done)} leads", flush=True)
    return done


def _pct(n, total):
    return round(100 * n / total) if total else 0


def probe(categories, city, sample):
    """Step 0 gate: measure how many leads actually have a WA number / email."""
    leads = enrich(discover(categories, [city], limit=sample))
    n = len(leads)
    wa = sum(1 for x in leads if x["wa"])
    em = sum(1 for x in leads if x["email"])
    print(f"\n=== COVERAGE PROBE: {n} leads, {categories} in {city} ===")
    print(f"  phone/WhatsApp: {wa}/{n} ({_pct(wa, n)}%)")
    print(f"  email:          {em}/{n} ({_pct(em, n)}%)")
    verdict = ("email viable, keep both channels" if n and em >= n * 0.4
               else "email thin (as predicted) -> WhatsApp is the real channel")
    print(f"  -> {verdict}")
    return leads


def find(campaign, name, limit=None):
    """Discover + enrich, checkpoint to data/<name>/leads.json + leads.csv. No LLM."""
    leads = enrich(discover(campaign["categories"], campaign["cities"],
                            limit or campaign.get("limit", 20)))
    _save_json(leads, name)
    _write_csv(leads, name)
    print(f"  found {len(leads)} leads -> data/{name}/leads.json")
    print("  next: Claude Code drafts data/{0}/drafts.json, then `python run.py merge --campaign {0}`".format(name))
    return leads


def _research_one(lead):
    """Attach a `research` block to one lead: Google reviews + site positioning."""
    pid = lead.get("place_id") or place_id_for(lead["name"], lead.get("address", ""),
                                               config.GOOGLE_PLACES_API_KEY)
    lead["place_id"] = pid
    lead["research"] = place_details(pid, config.GOOGLE_PLACES_API_KEY)
    lead["research"]["site"] = site_profile(lead.get("website", ""))
    return lead


def research(name):
    """Deep-enrich leads.json in place so drafts can name a real, sourced pain point.

    Separate from `find` on purpose: reviews sit in a pricier Places SKU, so this only
    runs on the leads you kept after eyeballing leads.csv.
    """
    leads = _load_json(name)
    with ThreadPoolExecutor(max_workers=6) as pool:
        leads = list(pool.map(_research_one, leads))
    _save_json(leads, name)
    quoted = sum(1 for x in leads if x["research"].get("review_quotes"))
    sites = sum(1 for x in leads if x["research"].get("site", {}).get("reachable"))
    print(f"  researched {len(leads)} leads: {quoted} with review text, {sites} with a live site")
    print(f"  next: Claude Code reads data/{name}/leads.json + campaigns/{name}.json -> drafts.json")
    return leads


def merge(name):
    """Apply Claude-Code-written drafts.json onto leads.json, write final CSV + XLSX.

    Drafting is done by Claude Code (the subscription), not an API. drafts.json is a
    list aligned 1:1 with leads.json, each item {whatsapp, email_subject, email_body}.
    """
    leads = _load_json(name)
    drafts_path = config.data_dir(name) / "drafts.json"
    if not drafts_path.exists():
        raise SystemExit(f"No {drafts_path}. Have Claude Code write it (one entry per lead), then rerun merge.")
    drafts = json.loads(drafts_path.read_text(encoding="utf-8"))
    if len(drafts) != len(leads):
        raise SystemExit(f"drafts.json has {len(drafts)} entries but leads.json has {len(leads)}.")
    for lead, d in zip(leads, drafts):
        lead.update(whatsapp=d.get("whatsapp", ""),
                    email_subject=d.get("email_subject", ""),
                    email_body=d.get("email_body", ""),
                    followups=d.get("followups", []))  # read later by `run.py followup`
    _save_json(leads, name)
    _write_csv(leads, name)
    _write_xlsx(leads, name)
    print(f"  merged {len(drafts)} drafts into data/{name}/leads.xlsx")
    return leads


def _wa_link(lead):
    if not lead.get("wa"):
        return ""
    return f"https://wa.me/{lead['wa']}?text={quote(lead.get('whatsapp', '') or '')}"


def _save_json(leads, name):
    (config.data_dir(name) / "leads.json").write_text(
        json.dumps(leads, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_json(name):
    """Load data/<name>/leads.json, or exit telling the user to run `find` first.

    Every command after `find` reads this file, and on a fresh clone it does not
    exist yet. Without this the first thing a new user sees is a FileNotFoundError
    traceback pointing at a path they have no reason to recognise.
    """
    path = config.data_dir(name) / "leads.json"
    if not path.exists():
        raise SystemExit(
            f"No leads yet for campaign '{name}' ({path} is missing)." + chr(10)
            + f"Run this first:  python run.py find --campaign {name}")
    return json.loads(path.read_text(encoding="utf-8"))


load_leads = _load_json  # public alias for run.py / outreach.py


def _write_csv(leads, name):
    path = config.data_dir(name) / "leads.csv"
    with open(path, "w", newline="", encoding="utf-8-sig") as f:  # BOM so Excel reads UTF-8
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        for lead in leads:
            lead["wa_link"] = _wa_link(lead)
            w.writerow(lead)
    print(f"  wrote {path}")


# Wide, wrap-friendly widths for the long message columns; the rest stay narrow.
_XLSX_WIDTHS = {"whatsapp": 55, "email_body": 60, "email_subject": 26, "wa_link": 40,
                "name": 28, "email": 26, "address": 30, "website": 24}
_WRAP_COLS = {"whatsapp", "email_body", "email_subject", "address", "name"}


def _write_xlsx(leads, name):
    """Excel with wrapped text on the long columns so message cells are readable, not clipped."""
    path = config.data_dir(name) / "leads.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "leads"
    ws.append(COLS)
    for cell in ws[1]:
        cell.font = Font(bold=True)
    ws.freeze_panes = "A2"
    for i, col in enumerate(COLS, 1):
        ws.column_dimensions[ws.cell(1, i).column_letter].width = _XLSX_WIDTHS.get(col, 14)
    wrap_top = Alignment(wrap_text=True, vertical="top")
    for lead in leads:
        lead["wa_link"] = _wa_link(lead)
        ws.append([lead.get(c, "") for c in COLS])
        for i, col in enumerate(COLS, 1):
            if col in _WRAP_COLS:
                ws.cell(ws.max_row, i).alignment = wrap_top
    try:
        wb.save(path)
    except PermissionError:
        # Excel holds a write lock on an open file; fall back so we don't lose the run.
        path = path.with_name("leads.new.xlsx")
        wb.save(path)
        print("  (leads.xlsx was open in Excel — close it; wrote leads.new.xlsx instead)")
    print(f"  wrote {path}")
