"""Bundled sample records for offline demo mode.

These are illustrative, not live results from Semantic Scholar. They let the
tool run end to end without network access or an API key, which is useful for a
quick demonstration and for tests. Pass --demo on the CLI to use them.

The records are plain dictionaries in the same shape the Semantic Scholar API
returns, and this module imports nothing from the rest of the package. That is
deliberate: an earlier version defined them as Paper and CitationContext
objects, which meant importing those classes from scholar.py while scholar.py
imported this module back. The cycle only worked because one side deferred its
import inside a function, and would have broken the moment anyone moved it to
the top of the file. Keeping the data as dictionaries lets the dependency run
one way, from scholar.py to here.
"""

from __future__ import annotations

PAPERS: list[dict] = [
    {
        "paperId": "demo-1",
        "title": "A metabolic hypothesis for age-related memory decline",
        "year": 2011,
        "authors": [{"name": "R. Nakamura"}, {"name": "L. Ortega"}],
        "abstract": (
            "We hypothesize that declining mitochondrial efficiency in hippocampal "
            "neurons drives age-related memory loss. We propose that restoring "
            "NAD+ levels could reverse early deficits."
        ),
        "citationCount": 140,
    },
    {
        "paperId": "demo-2",
        "title": "Gut microbiota as a novel driver of autoimmune arthritis",
        "year": 2013,
        "authors": [{"name": "S. Petrova"}],
        "abstract": (
            "This suggests that specific commensal bacteria may indicate, and "
            "possibly trigger, joint inflammation. To our knowledge this is the "
            "first evidence linking a single strain to disease onset."
        ),
        "citationCount": 95,
    },
    {
        "paperId": "demo-3",
        "title": "A speculative role for magnetoreception in human circadian timing",
        "year": 2016,
        "authors": [{"name": "H. Bianchi"}, {"name": "K. Adeyemi"}, {"name": "T. Rao"}],
        "abstract": (
            "We speculate that cryptochrome proteins could be sensitive to weak "
            "magnetic fields. It is possible that this contributes to circadian "
            "entrainment. Future work should test this under controlled fields."
        ),
        "citationCount": 8,
    },
    {
        "paperId": "demo-4",
        "title": "Standard characterisation of a soil bacterial community",
        "year": 2014,
        "authors": [{"name": "M. Costa"}],
        "abstract": (
            "We sequenced 200 soil samples and catalogued the dominant phyla. "
            "The community composition matched previously reported baselines."
        ),
        "citationCount": 52,
    },
]


def _citation(title: str, year: int, text: str, intents: tuple[str, ...]) -> dict:
    return {
        "citingPaper": {"title": title, "year": year},
        "contexts": [text],
        "intents": list(intents),
    }


# demo-1 is engaged with substantively, demo-2 is cited only as background, and
# demo-3 is barely cited, so the three neglect scores differ.
CITATIONS: dict[str, list[dict]] = {
    "demo-1": [
        _citation("Restoring NAD+ rescues synaptic plasticity", 2015,
                  "confirming the metabolic hypothesis of Nakamura et al.,", ("result",)),
        _citation("Mitochondrial dynamics in the ageing brain", 2017,
                  "extends the model proposed by Nakamura and Ortega",
                  ("methodology", "result")),
        _citation("A critical test of NAD+ supplementation", 2019,
                  "our data contradict the reversal predicted by", ("result",)),
    ],
    "demo-2": [
        _citation("Overview of microbiome research", 2016,
                  "as previously described (Petrova, 2013)", ("background",)),
        _citation("Commensals and immunity: a review", 2018,
                  "see Petrova (2013) for background", ("background",)),
    ],
    "demo-3": [
        _citation("Cryptochromes and light sensing", 2020,
                  "one speculative account (Bianchi et al.) remains untested",
                  ("background",)),
    ],
    "demo-4": [],
}


def search_response(limit: int = 50) -> dict:
    """Return sample papers shaped like the paper/search endpoint."""
    return {"data": PAPERS[:limit]}


def citations_response(paper_id: str, limit: int = 50) -> dict:
    """Return sample citations shaped like the paper/{id}/citations endpoint."""
    return {"data": CITATIONS.get(paper_id, [])[:limit]}
