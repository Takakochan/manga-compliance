# Interfaces

Written by a human. Agents implement *inside* these boundaries and must not change a type or a module boundary without saying so in the PR's Summary and asking first.

## Data flow

```
page image
  → detect (client.py)   FlagsResult
  → judge  (rules.py)    CountryVerdict per country
  → cite   (search.py)   Chunk per finding
  → verify (verify.py)   citation or null per finding
  → report (UI / CLI)    overlay + per-country summary, reviewer approves or rejects
```

## Types

Defined in `src/manga_compliance/models.py`.

```python
class Flag(BaseModel):          # one thing on the page a reviewer should look at
    bbox: list[int]             # [x1, y1, x2, y2] in pixels of the original image; approximate
    source: Source              # "image" (drawn) | "text" (written or said)
    category: Category          # violence | bad_language | fear | sex | drugs
                                # | discrimination | gambling | prohibited_symbol
    severity: Severity          # mild < moderate < strong
    confidence: float           # 0–1, how sure the model is the element is there
    evidence: str               # what the model saw, in English

class FlagsResult(BaseModel):   # the /flags response, unchanged
    status: str                 # ok | refused | unparsed | error
    summary: str
    flags: list[Flag]
    size: list[int]             # [width, height]
    seconds: float
    error: str | None

class Rule(BaseModel):          # one entry in rules/<country>.yaml
    id: str                     # COUNTRY-TOPIC-NN
    country: str                # ISO code
    category: Category
    min_severity: Severity      # default "mild"
    sources: list[Source]       # default both
    outcome: Outcome            # ok < review < age_restricted < edit_required < blocked
    label: str
    doc: str                    # file in corpus/ that holds the legal basis
    query: str                  # search text for cite, in the language of doc

class Finding(BaseModel):
    flag: Flag
    rule: Rule                  # the strictest matching rule of that country

class CountryVerdict(BaseModel):
    country: str
    outcome: Outcome            # strictest outcome among findings; "ok" if none
    findings: list[Finding]
```

To be added (not yet in `models.py`):

```python
class Chunk(BaseModel):         # cite → verify
    file_path: str              # relative to corpus/
    first_character_index: int
    last_character_index: int   # text == source[first:last]
    text: str

# Finding gets: citation: Chunk | None   (None = "no verified source")
```

## Modules and their contracts

| Module | Input | Output | Must not |
|---|---|---|---|
| `client.py` (detect) | image file | `FlagsResult` | decide outcomes; retry in a loop (the API is rate-limited) |
| `tiles.py` (zoom, 1b) | image file | `FlagsResult` with boxes in page coordinates | change the `FlagsResult` shape |
| `rules.py` (judge) | `list[Flag]`, `list[Rule]`, country | `CountryVerdict` | call a model or the network |
| `search.py` (cite) | `Rule.doc`, `Rule.query` | `Chunk` or nothing | paraphrase or generate text |
| `verify.py` | `Chunk` | `Chunk` or `None` | pass a quote that is not exactly `source[first:last]` |
| report (UI / CLI) | `CountryVerdict` list | screen / `out/*.report.json` | say "compliant" or "legal"; omit "not legal advice" |

## External APIs

| Service | Endpoint | Request | Response | Limits |
|---|---|---|---|---|
| Fukidashi | `GET /health` | none | `{"status": "ok"}` | — |
| Fukidashi | `POST /flags` | multipart `image` (png/jpeg/webp, ≤15 MB), header `X-API-Key` | `FlagsResult` | Rate-limited; cache results |

Details: `docs/API.md`. The engine is closed: call it, don't rebuild it.

## Errors

- HTTP errors (401, 413, 415, 400, 429, 502/504): `client.py` raises `ApiError` with the code and message. The CLI stops; nothing is judged.
- A 200 response with `status` = `refused`, `unparsed` or `error` has no flags. The page is **unresolved**, never `ok`: it is not judged, the CLI prints `UNRESOLVED` and asks for a manual review, and the report has `"checked": false` and no verdicts.
- No rule matches a flag: the flag is not a finding in that country (not an error).
- No verified citation: the finding stays, with `citation: null` shown as "no verified source".

## Decisions (and why)

- The AI describes the page, rules decide, a human approves: results are reproducible and explainable.
- A citation is shown only after `verify` confirms the exact quote: no invented laws.
- BM25 rather than embeddings for cite: simple, and returns character ranges that `verify` can check.
- Germany and Australia first: detailed youth-protection criteria and a formal publication classification scheme. UK and US come next.
- Zoom happens on our side (`tiles.py`), because the engine is a closed API.
