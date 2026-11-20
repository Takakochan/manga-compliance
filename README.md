# Manga Compliance Check

**Before a manga volume goes on sale in another country, find every page that country's content rules would flag, and back each finding with the exact rule it comes from.**

## Why

A licensed publisher has release gates before a volume goes on sale: rights, editorial quality, page quality, price, delivery. There is no gate for *"may this content be sold, as drawn, in this country?"*. Today that check is manual, page by page, and it differs per country. One well-known example: when One Piece aired on US television, a character's cigarette was redrawn as a lollipop.

This prototype automates the first pass and leaves the decision to a human.

## How it works

```
manga page
  1. Detect   vision model (Fukidashi API)  -> flags: what is drawn or said, where, how strong
  2. Judge    rules/*.yaml (no AI)          -> per country: ok / review / age_restricted / edit_required / blocked
  3. Cite     search over legal texts       -> the exact paragraph of the law or guideline
  4. Verify   code check                    -> the quote must exist in the source, or it is dropped
  5. Report   per-country summary           -> a reviewer approves or rejects each finding
```

- **The AI describes, the rules decide.** The model only says what is on the page. Outcomes come from human-written rules, so they are reproducible and explainable.
- **Cite or stay silent.** A citation is shown only if code confirms the quoted text exists in the source document.
- **Humans decide.** The tool ranks what to review. It is not legal advice.

Types and module contracts: [`docs/INTERFACES.md`](docs/INTERFACES.md). Rule format: [`rules/`](rules/).

## Status

This is an early prototype.

| Step | State |
|---|---|
| 1. Detect | Works on first test pages (violence, gore, smoking, alcohol). Small symbols in the artwork are not reliably detected yet |
| 2. Judge | Engine works; rules for Germany and Australia are drafts |
| 3. Cite | To do |
| 4. Verify | To do |
| 5. Report | Command-line report only |

## Run it

Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```
uv sync
uv run pytest                     # runs without the detection API
```

The detection engine (Fukidashi) is a separate, non-public service. With access:

```
cp .env.example .env              # fill in the URL and key
uv run python -m manga_compliance health
uv run python -m manga_compliance check page.png --countries DE,AU
```

## How it was built

Built with Claude Code as the coding agent, in a private working repository:

- I wrote the module boundaries and data types first (`docs/INTERFACES.md`); the agent implemented inside them.
- One task = one branch = one pull request, each with *Known limits*, a *Test plan* and evidence from a real run. I reviewed and merged.
- Claims are tested on real pages before they go into the docs. Example: an early draft said the tool detects the Buddhist manji; a test page with a small manji on an armband showed it does not, so the claim was withdrawn and page tiling was planned instead.
- This public repository is an export of the reviewed code (`LICENSE`: all rights reserved).

## Data

No manga pages are included. Use only pages you have the rights to process.

## Not legal advice

Outputs are a list of things to review, based on draft rules. They are not a legal assessment.

## Licence

All rights reserved. The code is published for reading only. Use, copying, modification, distribution and commercial use require prior written permission. See [`LICENSE`](LICENSE).
