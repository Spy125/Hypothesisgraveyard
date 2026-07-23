# HypothesisGraveyard

Searches a research topic on Semantic Scholar, extracts hypothesis sentences from paper abstracts, then checks whether each hypothesis was ever engaged with by later citations. Papers whose hypotheses were only cited as background - or never cited at all - are marked as abandoned.

The motivation: science produces many more hypotheses than it can test, and citation counts alone do not tell you whether an idea was taken seriously or just referenced in a literature review.

---

## How it works

1. Papers matching the query are fetched from Semantic Scholar (an API key is optional but recommended; see below)
2. Abstracts are scanned for hypothesis language: proposal markers ("we propose", "we hypothesise"), hedging ("this suggests", "may indicate"), possibility ("could be", "it is possible that"), and future predictions
3. Citation contexts are retrieved for each paper
4. A citation is classed as "engaging" if it confirms, challenges, or extends the work - not just cites it as background
5. A neglect score is computed per paper: `1 - (engaging citations / citation contexts examined)`
6. Papers with neglect score >= 0.7 are marked as buried
7. Results are rendered as a self-contained HTML graveyard page

---

## Usage

```bash
pip install -r requirements.txt

# Try it offline with bundled sample data (no network or API key needed)
python -m hypothesisgraveyard.cli dig "anything" --demo --no-html

# Search a topic and generate a graveyard
python -m hypothesisgraveyard.cli dig "gut-brain axis"

# Filter by year range
python -m hypothesisgraveyard.cli dig "CRISPR off-target" --from-year 2018 --to-year 2023

# Export as JSON and show only the 10 most neglected
python -m hypothesisgraveyard.cli dig "quantum cognition" --top 10 --json results.json

# Test hypothesis extraction on a single abstract
python -m hypothesisgraveyard.cli extract "We propose that gut bacteria modulate dopamine synthesis."
```

### Live data and rate limits

Live queries use the Semantic Scholar API, whose free tier throttles
unauthenticated traffic heavily. For live use, request a free API key from
Semantic Scholar and set it in the `SEMANTIC_SCHOLAR_API_KEY` environment
variable. Without a key, use `--demo` to run against the bundled sample data.

---

## Testing

Install the dependencies and run the suite:

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt pytest   # Linux/macOS: .venv/bin/pip
.venv/Scripts/python -m pytest -v
```

Exercise the CLI directly with `python -m hypothesisgraveyard.cli --help`.

---

## Project structure

```
hypothesisgraveyard/
├── hypothesisgraveyard/
│   ├── scholar.py      # Semantic Scholar search and citation fetch
│   ├── demo_data.py    # bundled sample data for --demo
│   ├── hypothesis.py   # hypothesis sentence extraction
│   ├── scorer.py       # neglect score computation
│   ├── visualiser.py   # standalone HTML output
│   └── cli.py
└── tests/
    ├── test_hypothesis.py
    └── test_scorer.py
```

---

## Stack

Python 3.10, Requests, Typer, Rich

An API key is optional but recommended for live use; `--demo` needs neither key nor network.
