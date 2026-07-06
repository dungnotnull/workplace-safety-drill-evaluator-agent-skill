# -*- coding: utf-8 -*-
"""
knowledge_updater.py — SECOND-KNOWLEDGE-BRAIN crawler for
`workplace-safety-drill-evaluator` (idea 120).

Production-grade async enrichment pipeline:

  1. fetch   -> structured scholarly APIs (Crossref, arXiv, Semantic Scholar).
                Optional HTML crawl of OSHA/NFPA pages via crawl4ai (graceful skip
                if the optional dependency is not installed).
  2. parse   -> normalized entry dict {title, authors, year, venue, url, doi,
                abstract, source, fetched_at}.
  3. score   -> recency (year-based) + domain-keyword relevance, combined 0..1.
  4. dedup   -> SHA-256(16) of DOI/URL lowercased-stripped; skip existing hashes.
  5. append  -> dated, schema-stable markdown entries in SECOND-KNOWLEDGE-BRAIN.md.

Run weekly (cron / scheduler). Designed to be safe and idempotent: re-running with
the same data appends nothing; a failed source never aborts the whole run.

Usage:
    python tools/knowledge_updater.py --dry-run
    python tools/knowledge_updater.py --since 2025-01-01 --min-score 0.40
    python tools/knowledge_updater.py --config tools/knowledge_updater.toml

Exit codes: 0 ok (even with zero new entries), 2 hard error (config/IO).
"""
from __future__ import annotations

import argparse
import asyncio
import datetime as _dt
import hashlib
import json
import logging
import os
import re
import sys
import time
import tomllib  # Python 3.11+
from dataclasses import dataclass, field, asdict
from typing import Any, Iterable
from xml.etree import ElementTree as ET

try:  # pragma: no cover - import guarded for environments without httpx
    import httpx
except ImportError as _exc:  # pragma: no cover
    sys.stderr.write(
        "[fatal] httpx is required. Install with: pip install -r tools/requirements.txt\n"
    )
    raise

LOG = logging.getLogger("knowledge_updater")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
DEFAULT_BRAIN = os.path.join(ROOT, "SECOND-KNOWLEDGE-BRAIN.md")
DEFAULT_CONFIG = os.path.join(HERE, "knowledge_updater.toml")

HASH_RE = re.compile(r"<!--hash:([0-9a-f]{16})-->")
ENTRY_HEAD_RE = re.compile(r"^### Crawl (\d{4}-\d{2}-\d{2}) \(\+\d+\)\s*$", re.MULTILINE)

DEFAULT_QUERIES = [
    "evacuation drill effectiveness metrics",
    "OSHA emergency action plan compliance",
    "ISO 45001 audit findings",
    "fire drill response time benchmark",
    "HAZWOPER drill evaluation",
    "defend in place evacuation healthcare",
    "HFACS drill root cause",
]

DEFAULT_KEYWORDS = [
    "evacuation drill", "regulatory compliance", "response time", "communication",
    "evacuation effectiveness", "gap closure", "OSHA", "NFPA", "ISO 45001",
    "HAZWOPER", "RSET", "ASET",
]

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class Entry:
    """Normalized scholarly entry produced by a source parser."""

    title: str
    authors: str
    year: int | None
    venue: str
    url: str
    doi: str | None
    abstract: str
    source: str
    fetched_at: str = field(default_factory=lambda: _dt.date.today().isoformat())

    def hash(self) -> str:
        key = (self.doi or self.url or self.title or "").strip().lower()
        return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]

    def to_markdown(self, today: str, score: float) -> str:
        authors = self.authors or "—"
        year = self.year if self.year else "—"
        venue = self.venue or "—"
        url = self.url or "—"
        doi = self.doi or "—"
        abstract = (self.abstract or "").strip().replace("\n", " ")
        if len(abstract) > 600:
            abstract = abstract[:597] + "…"
        return (
            f"- {today} | score={score} | **{self.title}** | {authors} | {year} "
            f"| {venue} | DOI:{doi} | URL:{url} | src={self.source} "
            f"| abstract: {abstract} <!--hash:{self.hash()}-->"
        )

    def to_json(self, score: float) -> dict[str, Any]:
        d = asdict(self)
        d["hash"] = self.hash()
        d["score"] = score
        return d


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

DOMAIN_KEYWORDS: list[str] = list(DEFAULT_KEYWORDS)


def configure_keywords(keywords: list[str]) -> None:
    global DOMAIN_KEYWORDS
    DOMAIN_KEYWORDS = list(keywords)


def score_entry(entry: Entry) -> float:
    """Recency + relevance score in [0, 1], rounded to 3 dp.

    Recency: linear decay over 10 years from the current year; unknown year -> 0.3.
    Relevance: fraction of domain keywords found in title+abstract (capped at 1.0).
    Combined: 0.5 * recency + 0.5 * relevance.
    """
    now = _dt.date.today().year
    year = entry.year
    if isinstance(year, int) and year > 1900:
        recency = max(0.0, 1.0 - (now - year) / 10.0)
    else:
        recency = 0.3
    text = (entry.title + " " + entry.abstract).lower()
    hits = sum(1 for k in DOMAIN_KEYWORDS if k.lower() in text)
    relevance = min(1.0, hits / max(1, len(DOMAIN_KEYWORDS)))
    return round(0.5 * recency + 0.5 * relevance, 3)


# ---------------------------------------------------------------------------
# Dedup + append
# ---------------------------------------------------------------------------


def load_existing_hashes(path: str) -> set[str]:
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return set(HASH_RE.findall(text))


def append_entries(
    entries: list[Entry],
    path: str,
    min_score: float = 0.0,
    max_per_source: int | None = None,
) -> tuple[int, list[Entry]]:
    """Append scored, de-duplicated entries under a dated crawl heading.

    Returns (added_count, added_entries). Idempotent: re-running with the same
    entries yields zero new appends.
    """
    existing = load_existing_hashes(path)
    today = _dt.date.today().isoformat()
    by_source: dict[str, list[Entry]] = {}
    for e in entries:
        by_source.setdefault(e.source, []).append(e)

    kept: list[Entry] = []
    for src, items in by_source.items():
        items_sorted = sorted(items, key=score_entry, reverse=True)
        cap = max_per_source or len(items_sorted)
        for e in items_sorted[:cap]:
            h = e.hash()
            if h in existing:
                continue
            sc = score_entry(e)
            if sc < min_score:
                continue
            kept.append(e)
            existing.add(h)

    if not kept:
        LOG.info("no new entries to append")
        return 0, []

    # Stable sort for deterministic output.
    kept.sort(key=lambda e: (score_entry(e), e.source, e.title), reverse=True)
    lines = [e.to_markdown(today, score_entry(e)) for e in kept]
    block = f"\n### Crawl {today} (+{len(kept)})\n" + "\n".join(lines) + "\n"

    with open(path, "a", encoding="utf-8") as f:
        f.write(block)
    LOG.info("appended %d new entries to %s", len(kept), path)
    return len(kept), kept


# ---------------------------------------------------------------------------
# Source parsers (pure functions; unit-testable without network)
# ---------------------------------------------------------------------------


def parse_crossref(item: dict[str, Any]) -> Entry | None:
    title_field = item.get("title") or []
    title = title_field[0] if isinstance(title_field, list) and title_field else (
        str(title_field) if title_field else ""
    )
    if not title:
        return None
    authors = []
    for a in item.get("author", []) or []:
        given = (a.get("given") or "").strip()
        family = (a.get("family") or "").strip()
        name = " ".join(p for p in (given, family) if p)
        if name:
            authors.append(name)
    year = None
    for dkey in ("published-print", "published-online", "issued", "created"):
        parts = (item.get(dkey) or {}).get("date-parts") or []
        if parts and parts[0] and parts[0][0]:
            year = int(parts[0][0])
            break
    venue = ""
    for vk in ("container-title",):
        v = item.get(vk) or []
        if v:
            venue = v[0] if isinstance(v, list) else str(v)
            break
    doi = item.get("DOI")
    url = item.get("URL") or (f"https://doi.org/{doi}" if doi else "")
    abstract = _strip_tags(item.get("abstract") or "")
    return Entry(
        title=title, authors="; ".join(authors), year=year, venue=venue or "Crossref",
        url=url, doi=doi, abstract=abstract, source="crossref",
    )


def parse_arxiv(entry_xml: ET.Element) -> Entry | None:
    ns = {"a": "http://www.w3.org/2005/Atom"}
    title_el = entry_xml.find("a:title", ns)
    if title_el is None or not (title_el.text or "").strip():
        return None
    title = " ".join(title_el.text.split())
    authors = []
    for au in entry_xml.findall("a:author", ns):
        n = au.find("a:name", ns)
        if n is not None and n.text:
            authors.append(n.text.strip())
    year = None
    published = entry_xml.find("a:published", ns)
    if published is not None and published.text:
        m = re.match(r"(\d{4})", published.text)
        if m:
            year = int(m.group(1))
    arxiv_id = ""
    id_el = entry_xml.find("a:id", ns)
    if id_el is not None and id_el.text:
        arxiv_id = id_el.text.strip()
        m = re.search(r"/abs/([^/]+)$", arxiv_id)
        if m:
            arxiv_id = m.group(1)
    summary_el = entry_xml.find("a:summary", ns)
    abstract = " ".join((summary_el.text or "").split()) if summary_el is not None else ""
    return Entry(
        title=title, authors="; ".join(authors), year=year, venue="arXiv",
        url=f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else arxiv_id,
        doi=None, abstract=abstract, source="arxiv",
    )


def parse_semantic_scholar(item: dict[str, Any]) -> Entry | None:
    title = item.get("title")
    if not title:
        return None
    authors = []
    for a in item.get("authors", []) or []:
        name = a.get("name")
        if name:
            authors.append(name)
    year = item.get("year")
    if isinstance(year, str) and year.isdigit():
        year = int(year)
    elif not isinstance(year, int):
        year = None
    venue = item.get("venue") or "Semantic Scholar"
    ext = item.get("externalIds") or {}
    doi = ext.get("DOI")
    url = item.get("url") or (f"https://doi.org/{doi}" if doi else "")
    abstract = item.get("abstract") or ""
    return Entry(
        title=title, authors="; ".join(authors), year=year, venue=venue,
        url=url, doi=doi, abstract=abstract, source="semantic_scholar",
    )


def _strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text or "").strip()


# ---------------------------------------------------------------------------
# Async fetchers (real APIs; per-source try/except isolates failures)
# ---------------------------------------------------------------------------


async def _get(client: "httpx.AsyncClient", url: str, **kw: Any) -> Any:
    resp = await client.get(url, **kw)
    resp.raise_for_status()
    return resp


async def fetch_crossref(
    queries: list[str], cfg: dict[str, Any], client: "httpx.AsyncClient",
) -> list[Entry]:
    rows = int(cfg.get("crossref", {}).get("rows", 25))
    mailto = cfg.get("crossref", {}).get("mailto", "")
    issn = cfg.get("crossref", {}).get("issn_filter")
    base = "https://api.crossref.org/works"
    headers = {"User-Agent": cfg.get("user_agent", "knowledge-updater")}
    if mailto:
        headers["User-Agent"] = f"{headers['User-Agent']} (mailto:{mailto})"
    out: list[Entry] = []
    for q in queries:
        params: dict[str, Any] = {
            "query": q, "rows": rows, "select": "DOI,title,author,published-print,"
            "published-online,issued,created,container-title,abstract,URL",
        }
        if issn:
            params["filter"] = f"issn:{issn}"
        try:
            resp = await _get(client, base, params=params, headers=headers, timeout=cfg.get("timeout_seconds", 30))
            items = resp.json().get("message", {}).get("items", []) or []
            for it in items:
                e = parse_crossref(it)
                if e:
                    out.append(e)
        except Exception as e:  # noqa: BLE001 - isolate source failure
            LOG.warning("crossref query %r failed: %s", q, e)
    return out


async def fetch_arxiv(
    queries: list[str], cfg: dict[str, Any], client: "httpx.AsyncClient",
) -> list[Entry]:
    max_results = int(cfg.get("arxiv", {}).get("max_results", 25))
    base = "http://export.arxiv.org/api/query"
    out: list[Entry] = []
    for q in queries:
        params = {"search_query": f"all:{q}", "start": 0, "max_results": max_results}
        try:
            resp = await _get(client, base, params=params, timeout=cfg.get("timeout_seconds", 30))
            root = ET.fromstring(resp.text)
            ns = {"a": "http://www.w3.org/2005/Atom"}
            for el in root.findall("a:entry", ns):
                e = parse_arxiv(el)
                if e:
                    out.append(e)
        except Exception as e:  # noqa: BLE001
            LOG.warning("arxiv query %r failed: %s", q, e)
    return out


async def fetch_semantic_scholar(
    queries: list[str], cfg: dict[str, Any], client: "httpx.AsyncClient",
) -> list[Entry]:
    limit = int(cfg.get("semantic_scholar", {}).get("limit", 25))
    fields = cfg.get("semantic_scholar", {}).get("fields", "title,authors,year,venue,externalIds,abstract")
    base = "https://api.semanticscholar.org/graph/v1/paper/search"
    headers = {"User-Agent": cfg.get("user_agent", "knowledge-updater")}
    out: list[Entry] = []
    for q in queries:
        params = {"query": q, "limit": limit, "fields": fields}
        try:
            resp = await _get(client, base, params=params, headers=headers, timeout=cfg.get("timeout_seconds", 30))
            data = resp.json().get("data", []) or []
            for it in data:
                e = parse_semantic_scholar(it)
                if e:
                    out.append(e)
        except Exception as e:  # noqa: BLE001
            LOG.warning("semantic_scholar query %r failed: %s", q, e)
    return out


async def fetch_crawl4ai(
    queries: list[str], cfg: dict[str, Any], client: "httpx.AsyncClient",
) -> list[Entry]:  # pragma: no cover - optional dep path
    """Optional HTML crawl for OSHA/NFPA pages via crawl4ai (extra dep)."""
    try:
        from crawl4ai import AsyncWebCrawler  # type: ignore
    except Exception as e:  # noqa: BLE001
        LOG.info("crawl4ai unavailable, skipping HTML crawl sources: %s", e)
        return []
    out: list[Entry] = []
    async with AsyncWebCrawler(verbose=False) as crawler:
        for source in cfg.get("crawl_sources", []):
            for q in queries:
                try:
                    res = await crawler.arun(
                        url=f"https://www.google.com/search?q={q.replace(' ', '+')}+{source.split()[0]}"
                    )
                    md = getattr(res, "markdown", "") or ""
                    if not md.strip():
                        continue
                    out.append(Entry(
                        title=f"[{source}] {q}", authors="", year=_dt.date.today().year,
                        venue=source, url=getattr(res, "url", "") or "",
                        doi=None, abstract=md[:500], source=f"crawl4ai:{source}",
                    ))
                except Exception as e:  # noqa: BLE001
                    LOG.warning("crawl4ai %s/%s failed: %s", source, q, e)
    return out


SOURCE_FUNCS = {
    "crossref": fetch_crossref,
    "arxiv": fetch_arxiv,
    "semantic_scholar": fetch_semantic_scholar,
    "crawl4ai": fetch_crawl4ai,
}


async def fetch_all(cfg: dict[str, Any], queries: list[str]) -> list[Entry]:
    api_sources = cfg.get("api_sources", ["crossref", "arxiv", "semantic_scholar"])
    sem = asyncio.Semaphore(max(1, int(cfg.get("concurrency", 4))))
    timeout = httpx.Timeout(cfg.get("timeout_seconds", 30))

    async with httpx.AsyncClient(timeout=timeout) as client:

        async def run(name: str) -> list[Entry]:
            fn = SOURCE_FUNCS.get(name)
            if not fn:
                LOG.warning("unknown source %r", name)
                return []
            async with sem:
                try:
                    return await fn(queries, cfg, client)
                except Exception as e:  # noqa: BLE001
                    LOG.warning("source %r raised: %s", name, e)
                    return []

        results = await asyncio.gather(*[run(n) for n in api_sources])
    flat: list[Entry] = []
    for r in results:
        flat.extend(r)
    return flat


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------


def load_config(path: str | None) -> dict[str, Any]:
    if path and os.path.exists(path):
        with open(path, "rb") as f:
            return tomllib.load(f)
    if os.path.exists(DEFAULT_CONFIG):
        with open(DEFAULT_CONFIG, "rb") as f:
            return tomllib.load(f)
    return {}


def filter_since(entries: list[Entry], since: str) -> list[Entry]:
    try:
        since_date = _dt.date.fromisoformat(since)
    except ValueError:
        return entries
    kept = []
    for e in entries:
        if not e.year:
            kept.append(e)
            continue
        try:
            ed = _dt.date(e.year, 1, 1)
        except ValueError:
            kept.append(e)
            continue
        if ed >= since_date:
            kept.append(e)
    return kept


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_argparser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="knowledge_updater",
        description="Refresh SECOND-KNOWLEDGE-BRAIN.md with dated, deduplicated scholarly entries.",
    )
    ap.add_argument("--config", default=DEFAULT_CONFIG, help="path to TOML config")
    ap.add_argument("--out", default=DEFAULT_BRAIN, help="path to SECOND-KNOWLEDGE-BRAIN.md")
    ap.add_argument("--since", default=None, help="keep entries dated on/after YYYY-MM-DD")
    ap.add_argument("--min-score", type=float, default=None, help="drop entries below this score")
    ap.add_argument("--max-per-source", type=int, default=None, help="cap kept entries per source")
    ap.add_argument("--dry-run", action="store_true", help="print scored JSON; do not write")
    ap.add_argument("--weekly", action="store_true", help="emit a cron-friendly log line and exit")
    ap.add_argument("-v", "--verbose", action="store_true", help="debug logging")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_argparser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    cfg = load_config(args.config)
    queries = cfg.get("queries") or DEFAULT_QUERIES
    configure_keywords(cfg.get("domain_keywords") or DEFAULT_KEYWORDS)

    if args.weekly:
        LOG.info("weekly tick at %s", _dt.date.today().isoformat())
        # Real scheduling is the operator's responsibility (cron / systemd timer).

    t0 = time.perf_counter()
    entries = asyncio.run(fetch_all(cfg, queries))
    LOG.info("fetched %d candidate entries in %.2fs", len(entries), time.perf_counter() - t0)

    if args.since:
        entries = filter_since(entries, args.since)
    min_score = args.min_score if args.min_score is not None else float(cfg.get("min_score", 0.0))
    max_per_source = args.max_per_source or int(cfg.get("max_per_source", 0)) or None

    if args.dry_run:
        scored = [e.to_json(score_entry(e)) for e in entries]
        print(json.dumps(scored, indent=2, ensure_ascii=False))
        return 0

    added, _ = append_entries(entries, args.out, min_score=min_score, max_per_source=max_per_source)
    print(f"[ok] appended {added} new entries to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
