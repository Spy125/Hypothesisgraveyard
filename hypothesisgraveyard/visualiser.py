"""Render a self-contained HTML graveyard page for abandoned hypotheses."""

from __future__ import annotations

from html import escape as _escape
from pathlib import Path

from hypothesisgraveyard.scorer import GraveyardEntry


_CSS = """
body { background:#0d1117; color:#c9d1d9; font-family:'Segoe UI',sans-serif;
       max-width:900px; margin:0 auto; padding:2rem; }
h1   { color:#58a6ff; border-bottom:1px solid #30363d; padding-bottom:.5rem; }
.stats { color:#8b949e; margin-bottom:2rem; font-size:.9rem; }
.section-title { font-size:1.2rem; font-weight:600; margin:2rem 0 1rem;
                  border-left:3px solid #f85149; padding-left:.8rem; }
.survived .section-title { border-left-color:#3fb950; }
.stone { background:#161b22; border:1px solid #30363d; border-radius:8px;
          padding:1.2rem 1.5rem; margin-bottom:1rem; }
.stone.buried { border-left:4px solid #f85149; }
.stone.survived-entry { border-left:4px solid #3fb950; }
.stone-title { font-weight:600; font-size:1rem; margin-bottom:.4rem; }
.stone-meta  { color:#8b949e; font-size:.82rem; margin-bottom:.7rem; }
.hypothesis  { font-style:italic; color:#e3b341; font-size:.9rem;
                background:#21262d; padding:.6rem .9rem; border-radius:4px;
                margin:.5rem 0; }
.neglect { font-size:.85rem; margin-top:.6rem; }
.neglect-bar { display:inline-block; height:8px; border-radius:4px;
                background:#f85149; margin-right:.5rem; vertical-align:middle; }
"""


def _gravestone_html(entry: GraveyardEntry) -> str:
    """Render one gravestone.

    Titles, author names and hypothesis text all originate from the Semantic
    Scholar API, so they are escaped rather than interpolated raw: an abstract
    containing markup would otherwise be parsed as part of the page.
    """
    css_class = "buried" if entry.is_buried else "survived-entry"
    bar_width  = int(entry.neglect_score * 120)
    hyp_html   = (f'<div class="hypothesis">{_escape(entry.strongest_hypothesis)}</div>'
                  if entry.strongest_hypothesis else "")

    return f"""
<div class="stone {css_class}">
  <div class="stone-title">{_escape(entry.paper.title)}</div>
  <div class="stone-meta">
    {_escape(entry.author_string)} &middot; {entry.paper.year} &middot;
    {entry.paper.citation_count} citations &middot;
    {entry.engaging_count} engaging
  </div>
  {hyp_html}
  <div class="neglect">
    <span class="neglect-bar" style="width:{bar_width}px"></span>
    Neglect score: <strong>{entry.neglect_score:.2f}</strong>
  </div>
</div>"""


def render_html(entries: list[GraveyardEntry], topic: str,
                survival_rate: float, output_path: Path = None) -> str:
    """Render the full graveyard HTML and optionally write to output_path."""
    buried   = [e for e in entries if e.is_buried]
    survived = [e for e in entries if not e.is_buried]

    buried_html   = "\n".join(_gravestone_html(e) for e in buried)
    survived_html = "\n".join(_gravestone_html(e) for e in survived)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>HypothesisGraveyard - {_escape(topic)}</title>
  <style>{_CSS}</style>
</head>
<body>
  <h1>HypothesisGraveyard</h1>
  <p class="stats">
    Topic: <strong>{_escape(topic)}</strong> &mdash;
    {len(entries)} papers analysed &mdash;
    Survival rate: <strong>{survival_rate:.1%}</strong>
  </p>

  <div class="buried">
    <div class="section-title">Abandoned ({len(buried)} papers)</div>
    {buried_html}
  </div>

  <div class="survived">
    <div class="section-title">Still alive ({len(survived)} papers)</div>
    {survived_html}
  </div>
</body>
</html>"""

    if output_path:
        Path(output_path).write_text(html, encoding="utf-8")

    return html
