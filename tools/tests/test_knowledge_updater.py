# -*- coding: utf-8 -*-
"""Unit tests for tools/knowledge_updater.py — no network required.

Run:  python -m pytest tools/tests/test_knowledge_updater.py -q
or:   python tools/tests/run.py
"""
import os
import sys
import datetime as _dt

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import knowledge_updater as ku
from xml.etree import ElementTree as ET


def _entry(**kw):
    base = dict(title="t", authors="a", year=2024, venue="v", url="u",
                doi=None, abstract="abs", source="crossref")
    base.update(kw)
    return ku.Entry(**base)


def test_hash_is_stable_and_lowercase_agnostic():
    e = _entry(doi="10.1000/ABC")
    assert e.hash() == _entry(doi="10.1000/abc").hash()
    assert e.hash() == _entry(doi=" 10.1000/ABC ").hash()
    assert len(e.hash()) == 16


def test_hash_falls_back_to_url_then_title():
    assert _entry(url="https://example.org/x", doi=None).hash()
    assert _entry(url="", doi=None, title="X").hash() == _entry(url=None, doi=None, title="x").hash()


def test_score_recency_decays_over_time():
    now = _dt.date.today().year
    recent = ku.score_entry(_entry(year=now, abstract="evacuation drill OSHA NFPA"))
    old = ku.score_entry(_entry(year=now - 9, abstract="evacuation drill OSHA NFPA"))
    assert recent > old
    assert 0.0 <= old <= recent <= 1.0


def test_score_relevance_increases_with_keywords():
    base_year = _dt.date.today().year
    low = ku.score_entry(_entry(year=base_year, abstract="unrelated topic"))
    high = ku.score_entry(_entry(year=base_year, abstract="evacuation drill OSHA NFPA ISO 45001 HAZWOPER RSET ASET"))
    assert high > low


def test_score_unknown_year_uses_floor():
    e = _entry(year=None, abstract="evacuation drill OSHA NFPA ISO 45001 HAZWOPER RSET ASET communication gap closure response time evacuation effectiveness regulatory compliance")
    assert ku.score_entry(e) == round(0.5 * 0.3 + 0.5 * 1.0, 3)


def test_load_existing_hashes_reads_existing_file(tmp_path):
    p = tmp_path / "brain.md"
    p.write_text("some line\n<!--hash:0123456789abcdef-->\nmore\n", encoding="utf-8")
    assert ku.load_existing_hashes(str(p)) == {"0123456789abcdef"}


def test_append_entries_dedups_existing(tmp_path):
    p = tmp_path / "brain.md"
    p.write_text("<!--hash:%s-->\n" % _entry(doi="10.1/known").hash(), encoding="utf-8")
    added, kept = ku.append_entries([_entry(doi="10.1/known"), _entry(doi="10.1/new", year=_dt.date.today().year)], str(p))
    assert added == 1 and len(kept) == 1


def test_append_entries_is_idempotent(tmp_path):
    p = tmp_path / "brain.md"
    e = _entry(doi="10.1/a", year=_dt.date.today().year)
    n1, _ = ku.append_entries([e], str(p))
    n2, _ = ku.append_entries([e], str(p))
    assert n1 == 1 and n2 == 0


def test_append_entries_respects_min_score(tmp_path):
    p = tmp_path / "brain.md"
    low = _entry(doi="10.1/low", year=None, abstract="nothing relevant", venue="v")
    assert ku.score_entry(low) < 0.4
    added, _ = ku.append_entries([low], str(p), min_score=0.4)
    assert added == 0


def test_append_entries_respects_max_per_source(tmp_path):
    p = tmp_path / "brain.md"
    items = [_entry(doi=f"10.1/{i}", year=_dt.date.today().year) for i in range(10)]
    added, _ = ku.append_entries(items, str(p), max_per_source=3)
    assert added == 3


def test_parse_crossref_basic():
    item = {
        "DOI": "10.1/abc", "title": ["Fire drill effectiveness"],
        "author": [{"given": "A", "family": "B"}, {"family": "C"}],
        "published-print": {"date-parts": [[2020, 6]]},
        "container-title": ["Safety Science"], "abstract": "<jats:p>hi</jats:p>",
        "URL": "https://doi.org/10.1/abc",
    }
    e = ku.parse_crossref(item)
    assert e is not None and e.doi == "10.1/abc" and e.year == 2020
    assert "A B" in e.authors and "C" in e.authors
    assert e.venue == "Safety Science" and "hi" in e.abstract


def test_parse_crossref_skips_empty_title():
    assert ku.parse_crossref({"DOI": "x", "title": []}) is None


def test_parse_arxiv_basic():
    xml = """<?xml version='1.0'?>
    <feed xmlns='http://www.w3.org/2005/Atom'>
      <entry>
        <title>Evacuation Modelling</title>
        <author><name>J Doe</name></author>
        <id>http://arxiv.org/abs/1234.5678v1</id>
        <published>2021-05-01T00:00:00Z</published>
        <summary>A study of RSET.</summary>
      </entry>
    </feed>"""
    el = ET.fromstring(xml).find("{http://www.w3.org/2005/Atom}entry")
    e = ku.parse_arxiv(el)
    assert e is not None
    assert e.title == "Evacuation Modelling" and e.year == 2021
    assert "1234.5678" in e.url and "J Doe" in e.authors


def test_parse_semantic_scholar_basic():
    item = {
        "title": "NFPA 101 study", "authors": [{"name": "X Y"}], "year": 2019,
        "venue": "Fire Safety Journal", "externalIds": {"DOI": "10.2/zz"},
        "abstract": "egress", "url": "https://www.semanticscholar.org/p/1",
    }
    e = ku.parse_semantic_scholar(item)
    assert e is not None and e.year == 2019 and e.doi == "10.2/zz" and "X Y" in e.authors


def test_filter_since_keeps_recent_and_unknown():
    yr = _dt.date.today().year
    e_old = _entry(doi="10.1/old", year=2000)
    e_new = _entry(doi="10.1/new", year=yr)
    e_unk = _entry(doi="10.1/unk", year=None)
    out = ku.filter_since([e_old, e_new, e_unk], "2010-01-01")
    assert e_old not in out and e_new in out and e_unk in out


def test_to_markdown_includes_hash_and_score():
    e = _entry(doi="10.1/mk", year=_dt.date.today().year)
    md = e.to_markdown("2026-07-06", 0.555)
    assert "<!--hash:" in md and "score=0.555" in md and "**" in md


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
