"""Offline demo mode and API error handling (no network)."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import requests

from hypothesisgraveyard.scholar import ScholarClient, ScholarError
from hypothesisgraveyard.hypothesis import HypothesisExtractor
from hypothesisgraveyard.scorer import NeglectScorer


class TestDemoMode:
    def test_search_returns_sample_papers(self):
        papers = ScholarClient(demo=True).search_topic("anything")
        assert len(papers) >= 3
        assert all(p.abstract for p in papers)

    def test_pipeline_runs_offline(self):
        client    = ScholarClient(demo=True)
        extractor = HypothesisExtractor()
        scorer    = NeglectScorer(buried_threshold=0.7)

        entries = []
        for paper in client.search_topic("anything"):
            hyps = extractor.extract(paper.abstract)
            if not hyps:
                continue
            ctxs = client.fetch_citations(paper.paper_id)
            entries.append(scorer.score(paper, hyps, ctxs))

        assert len(entries) >= 2
        # the sample data is designed so some hypotheses are buried and some are not
        assert {e.is_buried for e in entries} == {True, False}


class TestErrorHandling:
    def test_rate_limit_raises_scholar_error(self, monkeypatch):
        class _Resp:
            status_code = 429
            headers = {"Retry-After": "0"}

            def raise_for_status(self):  # pragma: no cover - not reached on 429
                pass

        client = ScholarClient()
        monkeypatch.setattr(client._session, "get", lambda *a, **k: _Resp())
        monkeypatch.setattr("hypothesisgraveyard.scholar.time.sleep", lambda *_: None)
        with pytest.raises(ScholarError):
            client._get("https://example.test/paper/search", {})

    def test_network_failure_raises_scholar_error(self, monkeypatch):
        def _boom(*a, **k):
            raise requests.ConnectionError("no network")

        client = ScholarClient()
        monkeypatch.setattr(client._session, "get", _boom)
        monkeypatch.setattr("hypothesisgraveyard.scholar.time.sleep", lambda *_: None)
        with pytest.raises(ScholarError):
            client._get("https://example.test/paper/search", {})
