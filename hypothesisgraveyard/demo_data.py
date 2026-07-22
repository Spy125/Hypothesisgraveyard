"""Bundled sample data for offline demo mode.

These are illustrative records, not live results from Semantic Scholar. They let
the tool run end to end without network access or an API key, which is useful
for a quick demonstration and for tests. Pass --demo on the CLI to use them.
"""

from __future__ import annotations

from .scholar import Author, CitationContext, Paper

_PAPERS = [
    Paper(
        paper_id="demo-1",
        title="A metabolic hypothesis for age-related memory decline",
        year=2011,
        authors=[Author("R. Nakamura"), Author("L. Ortega")],
        abstract=(
            "We hypothesize that declining mitochondrial efficiency in hippocampal "
            "neurons drives age-related memory loss. We propose that restoring "
            "NAD+ levels could reverse early deficits."
        ),
        citation_count=140,
    ),
    Paper(
        paper_id="demo-2",
        title="Gut microbiota as a novel driver of autoimmune arthritis",
        year=2013,
        authors=[Author("S. Petrova")],
        abstract=(
            "This suggests that specific commensal bacteria may indicate, and "
            "possibly trigger, joint inflammation. To our knowledge this is the "
            "first evidence linking a single strain to disease onset."
        ),
        citation_count=95,
    ),
    Paper(
        paper_id="demo-3",
        title="A speculative role for magnetoreception in human circadian timing",
        year=2016,
        authors=[Author("H. Bianchi"), Author("K. Adeyemi"), Author("T. Rao")],
        abstract=(
            "We speculate that cryptochrome proteins could be sensitive to weak "
            "magnetic fields. It is possible that this contributes to circadian "
            "entrainment. Future work should test this under controlled fields."
        ),
        citation_count=8,
    ),
    Paper(
        paper_id="demo-4",
        title="Standard characterisation of a soil bacterial community",
        year=2014,
        authors=[Author("M. Costa")],
        abstract=(
            "We sequenced 200 soil samples and catalogued the dominant phyla. "
            "The community composition matched previously reported baselines."
        ),
        citation_count=52,
    ),
]

# Citation contexts keyed by paper id. paper demo-1 is heavily engaged with,
# demo-2 mostly cited as background, demo-3 barely cited at all.
_CITATIONS: dict[str, list[CitationContext]] = {
    "demo-1": [
        CitationContext("Restoring NAD+ rescues synaptic plasticity", 2015,
                        "confirming the metabolic hypothesis of Nakamura et al.,",
                        intents=["result"]),
        CitationContext("Mitochondrial dynamics in the ageing brain", 2017,
                        "extends the model proposed by Nakamura and Ortega",
                        intents=["methodology", "result"]),
        CitationContext("A critical test of NAD+ supplementation", 2019,
                        "our data contradict the reversal predicted by",
                        intents=["result"]),
    ],
    "demo-2": [
        CitationContext("Overview of microbiome research", 2016,
                        "as previously described (Petrova, 2013)",
                        intents=["background"]),
        CitationContext("Commensals and immunity: a review", 2018,
                        "see Petrova (2013) for background",
                        intents=["background"]),
    ],
    "demo-3": [
        CitationContext("Cryptochromes and light sensing", 2020,
                        "one speculative account (Bianchi et al.) remains untested",
                        intents=["background"]),
    ],
    "demo-4": [],
}


def demo_search(query: str, limit: int = 50) -> list[Paper]:
    """Return the sample papers, ignoring the query text."""
    return _PAPERS[:limit]


def demo_citations(paper_id: str, limit: int = 50) -> list[CitationContext]:
    return list(_CITATIONS.get(paper_id, []))[:limit]
