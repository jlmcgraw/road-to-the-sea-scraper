# tests/test_build_html.py

from bs4 import BeautifulSoup
from road_to_the_sea_scraper import main as r


def test_build_html_wraps_articles():
    doc = r.build_html([BeautifulSoup("<article>one</article>", "html.parser").article])
    assert doc.startswith("<html>")
    assert "</html>" in doc
    assert "<article>one</article>" in doc
