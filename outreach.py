"""Gmail send + follow-up + reply tracking.

The article's 30/30/50 rule says half the result comes from follow-up, so the log is
the point of this module, not the sending. Every send writes a row to
`data/<campaign>/outreach.csv`; `sync` stamps replies back onto it; `stats` reads it.

Transport is stdlib smtplib/imaplib against Gmail with an App Password — no OAuth
client, no extra dependency. Requires 2-step verification on the account, then
https://myaccount.google.com/apppasswords.
"""
import csv
import email
import imaplib
import re
import smtplib
import ssl
import statistics
import time
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from email.utils import make_msgid, parseaddr

import config

LOG_COLS = ["email", "name", "subject", "sent_at", "message_id", "followups_sent",
            "last_followup_at", "replied_at", "reply_hours", "status"]

SMTP_HOST, SMTP_PORT = "smtp.gmail.com", 465
IMAP_HOST = "imap.gmail.com"
SEND_GAP_SECONDS = 8      # Gmail flags bursts; a human pace also reads better if audited
DEFAULT_DAILY_CAP = 30
_STOP_RE = re.compile(r"\b(stop|unsubscribe|berhenti|jangan kirim)\b", re.I)


# --- log -------------------------------------------------------------------

def _log_path(campaign):
    return config.data_dir(campaign) / "outreach.csv"


def load_log(campaign):
    """Return the outreach log as a list of dicts (empty if the campaign has none yet)."""
    path = _log_path(campaign)
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def save_log(campaign, rows):
    with open(_log_path(campaign), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=LOG_COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def _now():
    return datetime.now(timezone.utc)


def _stamp(dt):
    return dt.isoformat(timespec="seconds")


def _parse(stamp):
    return datetime.fromisoformat(stamp) if stamp else None


# --- sending ---------------------------------------------------------------

def _credentials():
    if not (config.GMAIL_ADDRESS and config.GMAIL_APP_PASSWORD):
        raise SystemExit("Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in .env "
                         "(Google account > 2-step verification > App passwords).")
    return config.GMAIL_ADDRESS, config.GMAIL_APP_PASSWORD


def _build(to_addr, subject, body, sender, in_reply_to=None):
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg["Message-ID"] = make_msgid()
    if in_reply_to:
        # Threading the follow-up under the original is what makes it a follow-up
        # rather than a second cold email landing in a separate thread.
        msg["In-Reply-To"] = in_reply_to
        msg["References"] = in_reply_to
    msg.set_content(body)
    return msg


def _deliver(messages):
    """Send a list of EmailMessage over one SMTP session. Returns count sent."""
    user, password = _credentials()
    sent = 0
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ssl.create_default_context()) as s:
        s.login(user, password)
        for i, msg in enumerate(messages):
            if i:
                time.sleep(SEND_GAP_SECONDS)
            s.send_message(msg)
            print(f"    sent -> {msg['To']}  [{msg['Subject']}]")
            sent += 1
    return sent


def _sender_header(campaign_cfg, user):
    name = campaign_cfg.get("sender", "")
    return f"{name} <{user}>" if name else user


def send(campaign, leads, campaign_cfg, confirm=False, cap=DEFAULT_DAILY_CAP):
    """Send the first-touch email to every lead with an address not already contacted.

    Without `confirm` this prints the plan and sends nothing — cold email is not
    something to fire off by accident.
    """
    rows = load_log(campaign)
    seen = {r["email"] for r in rows}
    queue = []
    for lead in leads:
        addr = lead.get("email")
        # One company can hold several Google listings (branch + HQ). Same inbox,
        # so dedupe within the batch too, not just against the log.
        if not addr or not lead.get("email_body") or addr in seen:
            continue
        seen.add(addr)
        queue.append(lead)
        if len(queue) >= cap:
            break
    if not queue:
        print("  nothing to send (all leads with an email have been contacted)")
        return rows

    print(f"  {len(queue)} to send:")
    for l in queue:
        print(f"    {l['email']:<38} {l.get('email_subject', '')}")
    if not confirm:
        print("  DRY RUN. Re-run with --confirm to actually send.")
        return rows

    user, _ = _credentials()
    sender = _sender_header(campaign_cfg, user)
    messages = [_build(l["email"], l.get("email_subject", ""), l["email_body"], sender)
                for l in queue]
    _deliver(messages)
    for lead, msg in zip(queue, messages):
        rows.append({
            "email": lead["email"], "name": lead.get("name", ""),
            "subject": msg["Subject"], "sent_at": _stamp(_now()),
            "message_id": msg["Message-ID"], "followups_sent": "0",
            "last_followup_at": "", "replied_at": "", "reply_hours": "", "status": "sent",
        })
    save_log(campaign, rows)
    print(f"  logged {len(queue)} sends -> {_log_path(campaign)}")
    return rows


def _due_followup(row, lead, default_days):
    """Return the next follow-up draft for this row if it is due, else None.

    Delay is measured from the ORIGINAL send, so a 3/8/15 schedule stays on the
    calendar you designed even if a run is skipped for a day.
    """
    if row["status"] != "sent":
        return None
    plan = lead.get("followups") or []
    n = int(row.get("followups_sent") or 0)
    if n >= len(plan):
        return None
    step = plan[n]
    due_after = timedelta(days=step.get("days", default_days))
    if _now() - _parse(row["sent_at"]) < due_after:
        return None
    return step


def followup(campaign, leads, campaign_cfg, confirm=False, cap=DEFAULT_DAILY_CAP):
    """Send the next scheduled follow-up to everyone who is due and hasn't replied."""
    rows = load_log(campaign)
    by_email = {l.get("email"): l for l in leads if l.get("email")}
    default_days = campaign_cfg.get("followup_days", 3)

    due = []
    for row in rows:
        lead = by_email.get(row["email"])
        step = _due_followup(row, lead, default_days) if lead else None
        if step:
            due.append((row, step))
    due = due[:cap]
    if not due:
        print("  no follow-ups due")
        return rows

    print(f"  {len(due)} follow-ups due:")
    for row, step in due:
        age = (_now() - _parse(row["sent_at"])).days
        print(f"    {row['email']:<38} touch #{int(row['followups_sent']) + 2}, {age}d after first")
    if not confirm:
        print("  DRY RUN. Re-run with --confirm to actually send.")
        return rows

    user, _ = _credentials()
    sender = _sender_header(campaign_cfg, user)
    messages = [_build(row["email"], step.get("subject") or f"Re: {row['subject']}",
                       step["body"], sender, in_reply_to=row["message_id"])
                for row, step in due]
    _deliver(messages)
    for (row, _step) in due:
        row["followups_sent"] = str(int(row["followups_sent"] or 0) + 1)
        row["last_followup_at"] = _stamp(_now())
    save_log(campaign, rows)
    print(f"  logged {len(due)} follow-ups")
    return rows


# --- reply tracking --------------------------------------------------------

def _imap_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode(errors="replace")
        return ""
    return (msg.get_payload(decode=True) or b"").decode(errors="replace")


def _find_reply(imap, addr, since):
    """Return (received_datetime, body) of the first mail from addr since `since`, or None."""
    criteria = f'(FROM "{addr}" SINCE {since.strftime("%d-%b-%Y")})'
    ok, data = imap.search(None, criteria)
    if ok != "OK" or not data[0]:
        return None
    uid = data[0].split()[0]
    ok, raw = imap.fetch(uid, "(RFC822)")
    if ok != "OK":
        return None
    msg = email.message_from_bytes(raw[0][1])
    received = email.utils.parsedate_to_datetime(msg["Date"])
    if received.tzinfo is None:
        received = received.replace(tzinfo=timezone.utc)
    return received, _imap_body(msg)


def sync(campaign):
    """Scan the inbox and stamp replied_at / reply_hours / stop-outs onto the log."""
    rows = load_log(campaign)
    pending = [r for r in rows if not r["replied_at"] and r["status"] != "stopped"]
    if not pending:
        print("  nothing pending to check")
        return rows

    user, password = _credentials()
    imap = imaplib.IMAP4_SSL(IMAP_HOST)
    found = 0
    try:
        imap.login(user, password)
        imap.select("INBOX")
        for row in pending:
            sent_at = _parse(row["sent_at"])
            # IMAP SINCE is date-granular and server-local; back up a day so a reply
            # that arrived hours after a late-night send is not missed.
            hit = _find_reply(imap, parseaddr(row["email"])[1], sent_at - timedelta(days=1))
            if not hit:
                continue
            received, body = hit
            if received < sent_at:
                continue
            row["replied_at"] = _stamp(received)
            row["reply_hours"] = str(round((received - sent_at).total_seconds() / 3600, 1))
            row["status"] = "stopped" if _STOP_RE.search(body[:500]) else "replied"
            found += 1
            print(f"    reply from {row['email']} after {row['reply_hours']}h ({row['status']})")
    finally:
        imap.logout()
    save_log(campaign, rows)
    print(f"  {found} new replies stamped")
    return rows


# --- metrics ---------------------------------------------------------------

def _rate(n, total):
    return f"{round(100 * n / total)}%" if total else "n/a"


def stats(campaign):
    """Print the funnel: sent, followed up, replied, reply rate, speed, follow-up lift."""
    rows = load_log(campaign)
    if not rows:
        print("  no outreach logged yet")
        return {}

    total = len(rows)
    replied = [r for r in rows if r["replied_at"]]
    stopped = [r for r in rows if r["status"] == "stopped"]
    followed = [r for r in rows if int(r["followups_sent"] or 0) > 0]
    hours = [float(r["reply_hours"]) for r in replied if r["reply_hours"]]
    # The article's claim to test on your own data: follow-ups roughly double replies.
    after_fu = [r for r in replied if r["last_followup_at"]
                and _parse(r["replied_at"]) > _parse(r["last_followup_at"])]

    out = {
        "sent": total, "followed_up": len(followed), "replied": len(replied),
        "stopped": len(stopped), "reply_rate": _rate(len(replied), total),
        "reply_rate_first_touch": _rate(len(replied) - len(after_fu), total),
        "replies_after_followup": len(after_fu),
        "median_reply_hours": round(statistics.median(hours), 1) if hours else "n/a",
        "awaiting": total - len(replied),
    }
    print(f"\n=== OUTREACH: {campaign} ===")
    for k, v in out.items():
        print(f"  {k:<24} {v}")
    return out


if __name__ == "__main__":
    # Self-check: the date/threading/parsing logic, no network and no credentials.
    m = _build("a@b.com", "hi", "body", "Me <me@x.com>", in_reply_to="<orig@x>")
    assert m["In-Reply-To"] == "<orig@x>" and m["References"] == "<orig@x>"
    assert m["Message-ID"].startswith("<")
    old = {"status": "sent", "sent_at": _stamp(_now() - timedelta(days=4)), "followups_sent": "0"}
    fresh = {"status": "sent", "sent_at": _stamp(_now()), "followups_sent": "0"}
    lead = {"followups": [{"days": 3, "body": "x"}]}
    assert _due_followup(old, lead, 3) is not None
    assert _due_followup(fresh, lead, 3) is None
    assert _due_followup({**old, "followups_sent": "1"}, lead, 3) is None
    assert _due_followup({**old, "status": "replied"}, lead, 3) is None
    assert _STOP_RE.search("tolong berhenti kirim") and not _STOP_RE.search("stopwatch")
    assert _rate(1, 4) == "25%" and _rate(0, 0) == "n/a"
    print("outreach.py self-check OK")
