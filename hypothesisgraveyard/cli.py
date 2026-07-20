"""CLI entry points: dig (search a topic) and extract (test a single abstract)."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from hypothesisgraveyard.scholar import ScholarClient
from hypothesisgraveyard.hypothesis import HypothesisExtractor
from hypothesisgraveyard.scorer import NeglectScorer
from hypothesisgraveyard.visualiser import render_html

app     = typer.Typer(name="hypothesisgraveyard", add_completion=False)
console = Console()


@app.command("dig")
def dig(
    topic: str = typer.Argument(..., help="Research topic to search"),
    limit: int  = typer.Option(50,  "--limit",     "-n", help="Max papers to fetch"),
    from_year: int = typer.Option(None, "--from-year", help="Earliest publication year"),
    to_year:   int = typer.Option(None, "--to-year",   help="Latest publication year"),
    top:       int = typer.Option(20,  "--top",         help="Show top N most neglected"),
    json_out:  str = typer.Option(None, "--json",       help="Save results as JSON"),
    html_out:  str = typer.Option(None, "--html",       help="Save HTML graveyard to file"),
    no_html:   bool = typer.Option(False, "--no-html",  help="Skip HTML output"),
    threshold: float = typer.Option(0.7, "--threshold", help="Neglect score to be 'buried'"),
):
    """Search a topic and generate a graveyard of neglected hypotheses."""
    client    = ScholarClient()
    extractor = HypothesisExtractor()
    scorer    = NeglectScorer(buried_threshold=threshold)

    console.print(f"[blue]Searching Semantic Scholar for:[/blue] {topic}")
    papers = client.search_topic(topic, limit=limit, year_start=from_year, year_end=to_year)
    console.print(f"Found {len(papers)} papers with abstracts")

    entries = []
    for i, paper in enumerate(papers):
        hyps = extractor.extract(paper.abstract)
        if not hyps:
            continue
        console.print(f"[{i+1}/{len(papers)}] {paper.title[:60]}...")
        ctxs  = client.fetch_citations(paper.paper_id)
        entry = scorer.score(paper, hyps, ctxs)
        entries.append(entry)

    if not entries:
        console.print("[yellow]No papers with hypothesis language found.[/yellow]")
        raise typer.Exit()

    entries = scorer.sort_by_neglect(entries)[:top]
    rate    = scorer.survival_rate(entries)

    # table summary
    table = Table(title=f"Top {len(entries)} most neglected hypotheses")
    table.add_column("Title", max_width=45)
    table.add_column("Year")
    table.add_column("Neglect")
    table.add_column("Status")
    for e in entries:
        status = "[red]Buried[/red]" if e.is_buried else "[green]Alive[/green]"
        table.add_row(e.paper.title[:44], str(e.paper.year),
                      f"{e.neglect_score:.2f}", status)
    console.print(table)
    console.print(f"\nSurvival rate: {rate:.1%}")

    if json_out:
        data = [{"title": e.paper.title, "year": e.paper.year,
                 "neglect_score": e.neglect_score, "is_buried": e.is_buried,
                 "hypothesis": e.strongest_hypothesis} for e in entries]
        Path(json_out).write_text(json.dumps(data, indent=2))
        console.print(f"JSON saved -> {json_out}")

    if not no_html:
        out = html_out or f"{topic.replace(' ', '_')}_graveyard.html"
        render_html(entries, topic=topic, survival_rate=rate, output_path=Path(out))
        console.print(f"HTML graveyard -> {out}")


@app.command("extract")
def extract_cmd(
    abstract: str = typer.Argument(..., help="Abstract text to analyse"),
    threshold: float = typer.Option(0.4, "--threshold", help="Min confidence"),
):
    """Test hypothesis extraction on a single abstract."""
    extractor = HypothesisExtractor()
    results   = extractor.extract(abstract, min_confidence=threshold)
    if not results:
        console.print("[yellow]No hypothesis sentences found.[/yellow]")
        return
    for r in results:
        console.print(f"[cyan]{r.signal}[/cyan] ({r.confidence:.1f}): {r.text}")


if __name__ == "__main__":
    app()
