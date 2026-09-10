# Lead Generator (personal, Indonesia B2B)

Finds Indonesian businesses (contractors, interior designers, etc.) via Google Places,
grabs their phone (→ WhatsApp) and best-effort email, pulls their Google reviews and site
profile so the message can name something real, and drafts a personalized WhatsApp +
email per lead with Claude. Email can then be sent and followed up automatically, with
every send, follow-up and reply logged.

Local, personal tool. Not SaaS. Low, manual volume only (WhatsApp ban + UU PDP safety).

## Setup

Python 3.10+.

```bash
git clone https://github.com/Kendrew-K/lead-gen.git
cd lead-gen
python -m venv .venv
.venv\Scripts\activate            # Windows
source .venv/bin/activate         # macOS / Linux
pip install -r requirements.txt
cp .env.example .env              # Windows: copy .env.example .env
```

Then fill in `.env`. Nothing under `data/` ships with this repo: it holds
scraped business contacts, which are personal data under Indonesia's UU PDP, so
it is gitignored and stays on the machine that collected it. Every run
recreates it from scratch.

Keys (all free tiers):
- **GOOGLE_PLACES_API_KEY** — *required.* Google Cloud Console → enable "Places API (New)" → create an API key. Has free monthly credit.
- **HUNTER_API_KEY** — optional email fallback. hunter.io.
- **GMAIL_ADDRESS / GMAIL_APP_PASSWORD** — only for `send`/`followup`/`sync`. App Password, not your account password: turn on 2-step verification, then https://myaccount.google.com/apppasswords

No LLM API key. Message drafting is done by **Claude Code** (the subscription), not the
Anthropic API — see "Drafting" below.

## Run

**Step 0 — coverage probe (do this first).** Proves whether email data even exists
for this segment before you build a campaign on it:

```
python run.py probe --category "interior designer,kontraktor" --city Jakarta --sample 10
```

Read the printed WA% and email%. Expect high phone/WA, low email — that means
WhatsApp is your real channel and email is a bonus.

**Full run** (edit `campaigns/test.json` first — the `mode`, `offer`, `cities`):

```
python run.py find     --campaign test    # Places -> leads.json + leads.csv (no LLM)
python run.py research --campaign test    # + Google reviews & site profile (see below)
# --- Claude Code writes data/test/drafts.json here (see Drafting) ---
python run.py merge    --campaign test    # apply drafts -> leads.xlsx + leads.csv
python run.py send     --campaign test    # dry run; add --confirm to actually send
python run.py sync     --campaign test    # scan inbox, stamp replies
python run.py followup --campaign test    # dry run; add --confirm to send what's due
python run.py stats    --campaign test    # sent / replied / reply rate / speed
```

`find` and `research` are split because reviews sit in a pricier Places SKU — you only
pay for the leads you kept after eyeballing `leads.csv`.

## Research (what makes the message specific)

`research` adds a `research` block to every lead:

- `rating`, `reviews_count`, and up to 5 `review_quotes` with how long ago each was left
- `summary`, `hours`, `type` from Google
- `site`: page title, meta description, h1/h2 headings, social links found, whether there
  is a contact form, and any "sejak/since YYYY"

**Reviews in this segment are almost all 5-star, so there are no complaints to mine.**
The signal is the *shape*: a high rating with a high review count whose newest review is
years old, next to a single inbound channel, means the delivery is proven and the
pipeline is not. That gap is the hook. The `cold-outreach` skill has the full read-out
table. (This is also why Clay isn't used: its strength is LinkedIn/funding/headcount data
that this segment simply doesn't have.)

## Drafting (Claude Code, not the API)

Between `research` and `merge`, ask Claude Code to draft the messages. It will use the
project's **`cold-outreach` skill** (`.claude/skills/cold-outreach/`), which covers mode,
reading the research, hook selection, CTA choice, follow-up rotation and the scoring
rubric. Point it at `data/<campaign>/leads.json` and `campaigns/<campaign>.json` and have
it write `data/<campaign>/drafts.json` — a list aligned 1:1 with the leads:

```json
{
  "whatsapp": "...",
  "email_subject": "...",
  "email_body": "...",
  "followups": [
    {"days": 3,  "body": "..."},
    {"days": 8,  "body": "..."},
    {"days": 15, "body": "..."}
  ]
}
```

`days` counts from the first send. A follow-up with no `subject` threads as
`Re: <original>`, which is what you want.

## Sending, follow-up and tracking

`send` and `followup` are **dry-run by default** — they print exactly what would go out
and send nothing until you add `--confirm`. Both cap at 30 messages per run (`--cap`) and
pace 8 seconds apart.

Everything lands in `data/<campaign>/outreach.csv`: who, subject, when sent, message id,
how many follow-ups, when they replied, how many hours that took, and status
(`sent` / `replied` / `stopped`). `sync` reads your inbox over IMAP and fills the reply
columns in; a reply containing "stop"/"berhenti"/"unsubscribe" marks the row `stopped`
and nothing is ever sent to it again.

`stats` turns that into the numbers worth watching — reply rate, first-touch vs
post-follow-up replies, median hours to reply, stop-outs, and how many are still awaiting
a follow-up.

## Campaign file (`campaigns/<name>.json`)

```json
{
  "mode": "new-customer",       // new-customer | partnership | supplier | validate
  "offer": "what you offer, in plain Bahasa",
  "goal": "book-call",          // or "validate"
  "sender": "Your name",
  "categories": ["interior designer", "kontraktor"],
  "cities": ["Jakarta"],
  "limit": 20,
  "followup_days": 3            // default gap if a draft omits `days`
}
```

**`mode` is the biggest single lever on how the message reads.** The same business gets a
completely different email depending on whether you want to sell to them, partner with
them, buy from them, or just ask them questions. It also changes who you should be
searching for in the first place — check `categories` matches the mode. Full table in the
`cold-outreach` skill.

## Output

`data/test/leads.xlsx` (and `.csv`) — one row per lead with:
`wa_link` (click it → WhatsApp opens with the message prefilled → review → send),
`email` + `email_subject`/`email_body`, plus the raw fields.
`data/test/outreach.csv` — the send/reply log.

## Cost / limits

- Places search: free credit covers thousands of searches/month.
- Places details (`research`): pricier per call, which is why it's a separate step run
  only on kept leads. Still well inside the free monthly credit at 20-50 leads.
- Drafting: no API cost — done by Claude Code.
- Hunter free tier is ~25–50 lookups/month; it's optional.
- Gmail: free, but stay well under a few dozen cold emails a day.

## Not built (deliberately)

Clay or other paid enrichment, Instagram, US market, resale/client hosting, Anthropic API
drafting, WhatsApp auto-send (manual by design — ban risk). Add later if the numbers in
`stats` say the channel works.
