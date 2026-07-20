# HypothesisGraveyard

Searches a research topic on Semantic Scholar, extracts hypothesis sentences from paper abstracts, then checks whether each hypothesis was ever engaged with by later citations. Papers whose hypotheses were only cited as background - or never cited at all - are marked as abandoned.

The motivation: science produces many more hypotheses than it can test, and citation counts alone do not tell you whether an idea was taken seriously or just referenced in a literature review.

---

## How it works

1. Papers matching the query are fetched from Semantic Scholar (free, no API key needed)
2. Abstracts are scanned for hypothesis language: proposal markers ("we propose", "we hypothesise"), hedging ("this suggests", "may indicate"), possibility ("could be", "it is possible that"), and future predictions
3. Citation contexts are retrieved for each paper
4. A citation is classed as "engaging" if it confirms, challenges, or extends the work - not just cites it as background
5. A neglect score is computed per paper: `1 - (engaging citations / total citations)`
6. Papers with neglect score >= 0.7 are marked as buried
7. Results are rendered as a self-contained HTML graveyard page

---

## Usage

```bash
pip install -r requirements.txt

# Search a topic and generate a graveyard
python -m hypothesisgraveyard.cli dig "gut-brain axis"

# Filter by year range
python -m hypothesisgraveyard.cli dig "CRISPR off-target" --from-year 2018 --to-year 2023

# Export as JSON and show only the 10 most neglected
python -m hypothesisgraveyard.cli dig "quantum cognition" --top 10 --json results.json

# Test hypothesis extraction on a single abstract
python -m hypothesisgraveyard.cli extract "We propose that gut bacteria modulate dopamine synthesis."
```

---

## Project structure

```
hypothesisgraveyard/
├── hypothesisgraveyard/
│   ├── scholar.py      # Semantic Scholar search and citation fetch
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

No API key required.
