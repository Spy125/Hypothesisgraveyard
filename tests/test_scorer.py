"""Tests for the neglect scorer."""

import pytest
from hypothesisgraveyard.scholar import Paper, Author, CitationContext
from hypothesisgraveyard.hypothesis import HypothesisSentence
from hypothesisgraveyard.scorer import NeglectScorer, GraveyardEntry


def _paper(citation_count: int = 0) -> Paper:
    return Paper(
        paper_id="abc123",
        title="A Novel Hypothesis about X",
        year=2020,
        authors=[Author(name="Smith J"), Author(name="Jones A")],
        abstract="We propose that X causes Y.",
        citation_count=citation_count,
    )


def _hyp(text: str = "We propose X causes Y.", confidence: float = 1.0) -> HypothesisSentence:
    return HypothesisSentence(text=text, confidence=confidence, signal="propose")


def _ctx(context: str, intents: list = None) -> CitationContext:
    return CitationContext(
        citing_title="Some Paper",
        citing_year=2022,
        context=context,
        intents=intents or [],
    )


@pytest.fixture
def scorer():
    return NeglectScorer(buried_threshold=0.7)


class TestNeglectScorer:
    def test_zero_citations_fully_neglected(self, scorer):
        entry = scorer.score(_paper(0), [_hyp()], [])
        assert entry.neglect_score == 1.0

    def test_zero_citations_is_buried(self, scorer):
        entry = scorer.score(_paper(0), [_hyp()], [])
        assert entry.is_buried is True

    def test_engaging_citation_reduces_neglect(self, scorer):
        ctx = _ctx("The authors confirm the hypothesis using a new dataset.", intents=["result"])
        entry = scorer.score(_paper(5), [_hyp()], [ctx])
        assert entry.neglect_score < 1.0

    def test_background_only_intent_not_engaging(self, scorer):
        ctx = _ctx("As previously shown (Smith et al., 2020)...", intents=["background"])
        entry = scorer.score(_paper(5), [_hyp()], [ctx])
        assert entry.engaging_count == 0

    def test_challenge_context_is_engaging(self, scorer):
        ctx = _ctx("Our results contradict the hypothesis proposed by Smith et al.")
        entry = scorer.score(_paper(3), [_hyp()], [ctx])
        assert entry.engaging_count >= 1

    def test_buried_threshold_respected(self, scorer):
        ctx = _ctx("Prior work (Smith et al.) described this pathway.", intents=["background"])
        entry = scorer.score(_paper(10), [_hyp()], [ctx])
        assert entry.is_buried == (entry.neglect_score >= 0.7)

    def test_survival_rate_all_engaged(self, scorer):
        ctx = _ctx("We confirm and extend this hypothesis.")
        entries = [
            scorer.score(_paper(3), [_hyp()], [ctx]),
            scorer.score(_paper(5), [_hyp()], [ctx]),
        ]
        rate = scorer.survival_rate(entries)
        assert rate == 1.0

    def test_survival_rate_none_engaged(self, scorer):
        entries = [
            scorer.score(_paper(0), [_hyp()], []),
            scorer.score(_paper(0), [_hyp()], []),
        ]
        rate = scorer.survival_rate(entries)
        assert rate == 0.0

    def test_sort_by_neglect_descending(self, scorer):
        ctx = _ctx("We confirm the finding.")
        e1 = scorer.score(_paper(0), [_hyp()], [])
        e2 = scorer.score(_paper(5), [_hyp()], [ctx])
        sorted_e = scorer.sort_by_neglect([e2, e1])
        assert sorted_e[0].neglect_score >= sorted_e[1].neglect_score

    def test_author_string_single_author(self, scorer):
        paper = _paper()
        paper.authors = [Author(name="Chen L")]
        entry = scorer.score(paper, [_hyp()], [])
        assert entry.author_string == "Chen L"

    def test_author_string_multiple_authors(self, scorer):
        entry = scorer.score(_paper(), [_hyp()], [])
        assert "et al." in entry.author_string

    def test_strongest_hypothesis_returns_text(self, scorer):
        hyps = [_hyp("Weaker claim.", 0.5), _hyp("Strong proposal.", 1.0)]
        entry = scorer.score(_paper(), hyps, [])
        assert entry.strongest_hypothesis == "Strong proposal."
