# Manufacturing Scheme Tracker

Free, daily-refreshed dashboard of Indian government manufacturing/MSME
schemes, funds, and grants — with eligibility auto-summarized by Claude.

## How it works

1. `scraper/fetch_myscheme.py` — reads myscheme.gov.in's sitemap, downloads
   the text of every scheme page, caches it in `data/raw_pages.json`.
2. `scraper/extract_with_claude.py` — sends each new/relevant page to
   Claude, gets back structured JSON (name, ministry, eligibility, deadline,
   etc.), saves it to `data/schemes.json`.
3. `.github/workflows/daily_fetch.yml` — runs steps 1-2 automatically every
   day via GitHub Actions (free tier), and commits the updated data files.
4. `app.py` — a Streamlit dashboard that reads `data/schemes.json` and lets
   you filter/search. Deploy it free on Streamlit Community Cloud.

## One-time setup (about 15 minutes)

1. **Create a GitHub repo** and push this folder to it.
2. **Get an Anthropic API key** at console.anthropic.com (pay-as-you-go;
   extracting a few hundred scheme pages costs a small amount, not free,
   but very cheap — a few hundred short completions).
3. In your repo settings → Secrets and variables → Actions, add a secret
   named `ANTHROPIC_API_KEY` with that key.
4. Go to the **Actions** tab → "Daily scheme fetch" → **Run workflow** to
   trigger it manually the first time (don't wait for the 3am cron).
5. Once `data/schemes.json` has entries, deploy the dashboard:
   go to share.streamlit.io (Streamlit Community Cloud, free), connect
   your GitHub repo, point it at `app.py`. Done — you'll have a live URL.

## Extending it

- **More sources**: add a new `scraper/fetch_<source>.py` following the
  same pattern (discover URLs → grab raw text → cache), and add its output
  into the same `extract_with_claude.py` pass. Good next targets: PIB press
  releases (pib.gov.in), DPIIT/Make in India PLI pages, your state's
  industry department site.
- **Telegram alerts**: add a small script that diffs today's
  `schemes.json` against yesterday's git-committed version and posts new
  entries to a Telegram bot (free via the Bot API). Run it as a last step
  in the same GitHub Actions workflow.
- **Cost control**: `extract_with_claude.py` only processes pages whose
  raw text matches a manufacturing keyword list (see `RELEVANT_KEYWORDS`
  in `fetch_myscheme.py`) — tune that list as you learn what's noise.

## Notes

- The scraper is intentionally "dumb" (just extracts raw text) and leaves
  all the parsing to Claude — this means it's much more resistant to the
  government site changing its HTML than a scraper built on exact CSS
  selectors would be.
- Be a polite scraper: the fetch script already rate-limits itself and
  only runs once a day. Don't lower `SLEEP_SECONDS` or increase the cron
  frequency without a good reason.
- This pulls from myScheme's public pages, not a private API — no login,
  no credentials, no ToS violation, just a slow, respectful, once-daily
  read of public information.
