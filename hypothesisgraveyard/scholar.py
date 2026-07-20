"""Semantic Scholar API client - search for papers and fetch citation contexts."""

from __future__ import annotations

import time
import logging
from dataclasses import dataclass, field

import requests

log = logging.getLogger(__name__)

BASE_URL   = "https://api.semanticscholar.org/graph/v1"
RATE_SLEEP = 1.5   # seconds to wait between requests
MAX_RETRY  = 3


@dataclass
class Author:
    name: str


@dataclass
class CitationContext:
    citing_title: str
    citing_year: int
    context: str
    intents: list[str] = field(default_factory=list)


@dataclass
class Paper:
    paper_id: str
    title: str
    year: int
    authors: list[Author]
    abstract: str
    citation_count: int
    citations: list[CitationContext] = field(default_factory=list)


class ScholarClient:
    """Thin wrapper around the Semantic Scholar Graph API (no key required)."""

    def __init__(self, timeout: int = 20):
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "HypothesisGraveyard/1.0"})
        self._timeout = timeout

    def search_topic(self, query: str, limit: int = 50,
                     year_start: int = None, year_end: int = None) -> list[Paper]:
        """Search for papers matching query and return Paper objects."""
        params = {
            "query": query,
            "limit": min(limit, 100),
            "fields": "paperId,title,year,authors,abstract,citationCount",
        }
        if year_start or year_end:
            lo = year_start or 1900
            hi = year_end or 2099
            params["year"] = f"{lo}-{hi}"

        data = self._get(f"{BASE_URL}/paper/search", params=params)
        papers = []
        for item in data.get("data", []):
            if not item.get("abstract"):
                continue
            papers.append(Paper(
                paper_id=item["paperId"],
                title=item.get("title", ""),
                year=item.get("year") or 0,
                authors=[Author(name=a.get("name", "")) for a in item.get("authors", [])],
                abstract=item["abstract"],
                citation_count=item.get("citationCount") or 0,
            ))
        return papers

    def fetch_citations(self, paper_id: str, limit: int = 50) -> list[CitationContext]:
        """Fetch citation contexts for a paper - shows HOW citing papers reference it."""
        params = {
            "limit": min(limit, 100),
            "fields": "title,year,contexts,intents",
        }
        data = self._get(f"{BASE_URL}/paper/{paper_id}/citations", params=params)
        ctxs = []
        for item in data.get("data", []):
            citing = item.get("citingPaper", {})
            for ctx_text in item.get("contexts", [""]):
                ctxs.append(CitationContext(
                    citing_title=citing.get("title", ""),
                    citing_year=citing.get("year") or 0,
                    context=ctx_text,
                    intents=item.get("intents", []),
                ))
        return ctxs

    def _get(self, url: str, params: dict = None) -> dict:
        """Make a GET request with retry on 429 rate limit."""
        for attempt in range(MAX_RETRY):
            time.sleep(RATE_SLEEP)
            try:
                r = self._session.get(url, params=params, timeout=self._timeout)
                if r.status_code == 429:
                    wait = 5 * (attempt + 1)
                    log.warning("Rate limited - waiting %ds", wait)
                    time.sleep(wait)
                    continue
                r.raise_for_status()
                return r.json()
            except requests.RequestException as e:
                log.error("Request failed (attempt %d): %s", attempt + 1, e)
                if attempt == MAX_RETRY - 1:
                    raise
        return {}
