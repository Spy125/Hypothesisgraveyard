"""Semantic Scholar API client - search for papers and fetch citation contexts."""

from __future__ import annotations

import os
import time
import logging
from dataclasses import dataclass, field

import requests

log = logging.getLogger(__name__)

BASE_URL   = "https://api.semanticscholar.org/graph/v1"
RATE_SLEEP = 1.5   # seconds to wait between requests
MAX_RETRY  = 5


class ScholarError(RuntimeError):
    """Raised when the Semantic Scholar API cannot be reached or keeps rate-limiting.

    The message is written for a CLI user, since the API throttles
    unauthenticated traffic aggressively.
    """


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
    """Wrapper around the Semantic Scholar Graph API.

    An API key is optional but strongly recommended: unauthenticated requests
    share a very low rate limit and are often throttled. Provide one via the
    ``api_key`` argument or the ``SEMANTIC_SCHOLAR_API_KEY`` environment variable.
    Set ``demo=True`` to serve bundled sample data instead of calling the API.
    """

    def __init__(self, timeout: int = 20, api_key: str | None = None,
                 demo: bool = False):
        self.demo = demo
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "HypothesisGraveyard/1.0"})
        key = api_key or os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
        if key:
            self._session.headers["x-api-key"] = key
        self._timeout = timeout

    def search_topic(self, query: str, limit: int = 50,
                     year_start: int = None, year_end: int = None) -> list[Paper]:
        """Search for papers matching query and return Paper objects."""
        if self.demo:
            from .demo_data import demo_search
            return demo_search(query, limit)
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
        if self.demo:
            from .demo_data import demo_citations
            return demo_citations(paper_id, limit)
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
        """GET with retry and exponential backoff on rate limiting.

        Raises ScholarError if the API keeps returning 429 or cannot be reached,
        rather than returning an empty result that would look like "no papers".
        """
        for attempt in range(MAX_RETRY):
            time.sleep(RATE_SLEEP)
            try:
                r = self._session.get(url, params=params, timeout=self._timeout)
            except requests.RequestException as e:
                log.error("Request failed (attempt %d/%d): %s", attempt + 1, MAX_RETRY, e)
                if attempt == MAX_RETRY - 1:
                    raise ScholarError(
                        f"Could not reach Semantic Scholar ({e})."
                    ) from e
                time.sleep(2 ** attempt)
                continue

            if r.status_code == 429:
                # Honour Retry-After when present, otherwise back off exponentially.
                retry_after = r.headers.get("Retry-After")
                wait = int(retry_after) if retry_after and retry_after.isdigit() else 5 * (2 ** attempt)
                log.warning("Rate limited (attempt %d/%d) - waiting %ds",
                            attempt + 1, MAX_RETRY, wait)
                time.sleep(wait)
                continue

            r.raise_for_status()
            return r.json()

        raise ScholarError(
            "Semantic Scholar kept rate-limiting the request. Its free tier "
            "throttles unauthenticated traffic heavily. Set an API key in the "
            "SEMANTIC_SCHOLAR_API_KEY environment variable, or run with --demo "
            "to use bundled sample data."
        )
