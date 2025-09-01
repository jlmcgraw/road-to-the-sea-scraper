# tests/test_main_integration.py
from pathlib import Path

from bs4 import BeautifulSoup
from road_to_the_sea_scraper import main as r


def test_main_writes_combined_html(tmp_path, monkeypatch):
    pages = [
        BeautifulSoup(
            "<html><body><article id='p1a'></article></body></html>", "html.parser"
        ),
        BeautifulSoup(
            "<html><body><article id='p2a'></article>"
            "<article id='p2b'></article></body></html>",
            "html.parser",
        ),
        None,  # stop
    ]
    calls = {"i": 0}

    def fake_fetch(_page_num: int, _base_url: str, _headers: dict[str, str]):
        i = calls["i"]
        calls["i"] += 1
        return pages[i]

    monkeypatch.setattr(r, "fetch_page", fake_fetch)

    out = Path(tmp_path) / "out.html"
    r.main(
        base_url="https://example.com/page/{}",
        root_url="https://example.com",
        headers={"UA": "x"},
        output_file=str(out),
    )

    txt = out.read_text(encoding="utf-8")
    assert '<article id="p1a"></article>' in txt
    assert '<article id="p2a"></article>' in txt
    assert '<article id="p2b"></article>' in txt
