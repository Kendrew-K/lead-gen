"""CLI. `python run.py <command> ...`

  probe    --category "interior designer,kontraktor" --city Jakarta --sample 10
  find     --campaign test [--limit N]   -> leads.json + leads.csv (no LLM)
  research --campaign test               -> add Google reviews + site profile to leads.json
  merge    --campaign test               -> apply drafts.json (written by Claude Code) -> leads.xlsx
  send     --campaign test [--confirm]   -> Gmail first touch, logged to outreach.csv
  followup --campaign test [--confirm]   -> next scheduled touch to anyone due, no reply
  sync     --campaign test               -> scan inbox, stamp replies onto the log
  stats    --campaign test               -> sent / replied / reply rate / speed

Drafting is done by Claude Code, not an API. Between `research` and `merge`, Claude Code
writes data/<campaign>/drafts.json (one entry per lead, see README).

`send` and `followup` are dry-run unless you pass --confirm.
"""
import argparse
import sys

import config
import outreach
import pipeline


def _split(csv_arg):
    return [s.strip() for s in csv_arg.split(",") if s.strip()]


def _require(key, name, what):
    if not key:
        sys.exit(f"Missing {name}. Set it in .env (copy .env.example). Needed for: {what}.")


def _campaign_args(parser):
    parser.add_argument("--campaign", required=True)
    return parser


def _sending_args(parser):
    _campaign_args(parser)
    parser.add_argument("--confirm", action="store_true", help="actually send (default: dry run)")
    parser.add_argument("--cap", type=int, default=outreach.DEFAULT_DAILY_CAP,
                        help="max messages this run")
    return parser


def main():
    ap = argparse.ArgumentParser(prog="leadgen")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("probe", help="Step 0: measure WA/email coverage on a small sample")
    p.add_argument("--category", required=True, help="comma-separated categories")
    p.add_argument("--city", required=True)
    p.add_argument("--sample", type=int, default=10)

    f = _campaign_args(sub.add_parser("find"))
    f.add_argument("--limit", type=int, default=None)
    _campaign_args(sub.add_parser("research"))
    _campaign_args(sub.add_parser("merge"))
    _sending_args(sub.add_parser("send"))
    _sending_args(sub.add_parser("followup"))
    _campaign_args(sub.add_parser("sync"))
    _campaign_args(sub.add_parser("stats"))

    args = ap.parse_args()
    if args.cmd == "probe":
        _require(config.GOOGLE_PLACES_API_KEY, "GOOGLE_PLACES_API_KEY", "finding leads")
        pipeline.probe(_split(args.category), args.city, args.sample)
    elif args.cmd == "find":
        _require(config.GOOGLE_PLACES_API_KEY, "GOOGLE_PLACES_API_KEY", "finding leads")
        pipeline.find(pipeline.load_campaign(args.campaign), args.campaign, args.limit)
    elif args.cmd == "research":
        _require(config.GOOGLE_PLACES_API_KEY, "GOOGLE_PLACES_API_KEY", "fetching reviews")
        pipeline.research(args.campaign)
    elif args.cmd == "merge":
        pipeline.merge(args.campaign)
    elif args.cmd in ("send", "followup"):
        leads = pipeline.load_leads(args.campaign)
        cfg = pipeline.load_campaign(args.campaign)
        fn = outreach.send if args.cmd == "send" else outreach.followup
        fn(args.campaign, leads, cfg, confirm=args.confirm, cap=args.cap)
    elif args.cmd == "sync":
        outreach.sync(args.campaign)
    elif args.cmd == "stats":
        outreach.stats(args.campaign)


if __name__ == "__main__":
    main()
