# tests/test_extract_and_fix.py

from typing import TYPE_CHECKING

from bs4 import BeautifulSoup
from road_to_the_sea_scraper import main as r

if TYPE_CHECKING:
    from bs4.element import Tag


def _s(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def test_extract_stories_finds_articles():
    soup = _s(
        "<html><body><article id='a1'></article>"
        "<div></div>"
        "<article id='a2'></article></body></html>"
    )
    arts = r.extract_stories(soup)
    ids = [a.get("id") for a in arts]
    assert ids == ["a1", "a2"]


def test_fix_image_urls_normalizes_and_cleans() -> None:
    story_html = """
    <article>
      <h2>Title</h2>
      <img data-src="/img/pic.jpg" data-srcset="x 1x" data-sizes="auto" />
      <img src="/img/other.jpg" />
    </article>
    """
    story: Tag | None = _s(story_html).article
    assert story is not None
    r.fix_image_urls([story], root_url="https://site.test")
    imgs = story.select("img")
    assert imgs[0]["src"] == "https://site.test/img/pic.jpg"
    assert "data-src" not in imgs[0].attrs
    assert "data-srcset" not in imgs[0].attrs
    assert "data-sizes" not in imgs[0].attrs
    assert imgs[1]["src"] == "https://site.test/img/other.jpg"
