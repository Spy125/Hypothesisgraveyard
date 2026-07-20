"""Tests for hypothesis sentence extraction."""

import pytest
from hypothesisgraveyard.hypothesis import HypothesisExtractor, HypothesisSentence


@pytest.fixture
def extractor():
    return HypothesisExtractor()


class TestHypothesisExtraction:
    def test_propose_signal_detected(self, extractor):
        abstract = "We propose that gut bacteria directly modulate dopamine synthesis."
        results = extractor.extract(abstract)
        assert len(results) == 1
        assert results[0].confidence == 1.0

    def test_hedge_signal_detected(self, extractor):
        abstract = "This suggests that early exposure may alter neural pathways."
        results = extractor.extract(abstract)
        assert len(results) >= 1

    def test_novel_signal_gives_high_confidence(self, extractor):
        abstract = "We present, to our knowledge, the first novel hypothesis about cancer metastasis."
        results = extractor.extract(abstract)
        assert any(r.confidence >= 0.9 for r in results)

    def test_plain_factual_sentence_not_extracted(self, extractor):
        abstract = "The study included 200 participants from three hospitals."
        results = extractor.extract(abstract)
        assert results == []

    def test_multiple_hypotheses_extracted(self, extractor):
        abstract = (
            "We propose that immune cells mediate the effect. "
            "This suggests a role for inflammation. "
            "These results may indicate a novel pathway."
        )
        results = extractor.extract(abstract)
        assert len(results) >= 2

    def test_min_confidence_filters_weak_signals(self, extractor):
        abstract = "This could be relevant in some contexts."
        high = extractor.extract(abstract, min_confidence=0.9)
        low  = extractor.extract(abstract, min_confidence=0.1)
        assert len(high) <= len(low)

    def test_has_hypothesis_true(self, extractor):
        abstract = "We hypothesize that stress triggers epigenetic changes."
        assert extractor.has_hypothesis(abstract) is True

    def test_has_hypothesis_false(self, extractor):
        abstract = "A total of 50 mice were divided into control and experimental groups."
        assert extractor.has_hypothesis(abstract) is False

    def test_returned_type_is_hypothesis_sentence(self, extractor):
        abstract = "We suggest that the mechanism involves autophagy."
        results = extractor.extract(abstract)
        assert all(isinstance(r, HypothesisSentence) for r in results)

    def test_text_preserved_in_result(self, extractor):
        sentence = "We propose a novel model for synaptic plasticity."
        results = extractor.extract(sentence)
        assert len(results) == 1
        assert "synaptic plasticity" in results[0].text
