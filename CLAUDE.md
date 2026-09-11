# Working in this repo

Notes for a coding agent (Claude Code or similar) pointed at a fresh clone.
This is a personal, low-volume B2B lead tool for the Indonesian market. It is
not SaaS, and the volume limits below are safety rails, not defaults to raise.

## First run

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then fill in GOOGLE_PLACES_API_KEY
```

Only `GOOGLE_PLACES_API_KEY` is required. Hunter and Gmail keys are optional
and only matter for email fallback and for `send`/`followup`/`sync`. Every
command exits with a plain sentence naming what is missing rather than a
traceback, so run the command and read what it says.

## The pipeline

```bash
python run.py probe    --category "kontraktor" --city Jakarta --sample 10
python run.py find     --campaign <name>     # Places -> data/<name>/leads.json
python run.py research --campaign <name>     # + reviews and site profile
#   you draft data/<name>/drafts.json here
python run.py merge    --campaign <name>     # drafts -> leads.xlsx / leads.csv
python run.py send     --campaign <name>     # dry run; --confirm to actually send
python run.py sync     --campaign <name>     # read inbox, stamp replies
python run.py followup --campaign <name>     # dry run; --confirm to send
python run.py stats    --campaign <name>
```

Always `probe` before building a campaign: it reports what share of a segment
even has an email, which decides whether email is worth writing at all.

## Turning a description of a business into a campaign

When the user describes their business in plain words, write
`campaigns/<name>.json` yourself. The fields are documented in
[`README.md`](README.md). Two of them do most of the work:

- **`mode`** (`new-customer` | `partnership` | `supplier` | `validate`) changes
  both how the message reads and who should be in `categories`. Pick it from
  what the user actually wants out of the conversation, and say which you
  picked and why.
- **`categories`** are Google Places search terms in the language the listings
  are written in, which for Indonesia usually means Bahasa (`kontraktor`, not
  `contractor`).

## Drafting messages

Between `research` and `merge`, write `data/<campaign>/drafts.json`, aligned
1:1 with `leads.json`. **Read `.claude/skills/cold-outreach/SKILL.md` first and
follow it** — it covers mode, reading the research into a diagnosis, hook
selection, CTA choice and the follow-up rotation. Never write a first touch
without writing its follow-ups in the same pass.

The research block is the point: name something real from that specific
business (a review quote, a gap between a strong rating and a stale listing, a
missing contact channel). A draft that would read the same for any business on
the list is a failed draft.

## Rules that are not negotiable

- **Never send without the user saying so.** `send` and `followup` are dry-run
  by default; do not add `--confirm` on your own initiative.
- **Never raise the caps.** 30 messages per run, paced 8 seconds apart, and low
  daily volume. This is WhatsApp ban risk and inbox reputation, not a
  throughput problem to optimise.
- **`data/` never leaves the machine.** It holds scraped names, phone numbers
  and addresses: personal data under Indonesia's UU PDP. It is gitignored.
  Do not commit it, do not paste it into a commit message, and do not upload it
  anywhere.
- **Honour stop requests.** A reply containing "stop", "berhenti" or
  "unsubscribe" marks the row `stopped` and nothing goes to it again. Do not
  work around that.
- No Anthropic API key is used or wanted here. Drafting is done by the agent
  reading the files, which is why there is no LLM dependency in
  `requirements.txt`.
