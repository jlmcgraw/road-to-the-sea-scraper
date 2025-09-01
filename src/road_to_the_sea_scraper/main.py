#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
# "beautifulsoup4",
# "requests",
# "tenacity"
# ]
# ///
"""Scrape the Road to the Sea blog into one page."""

import logging
from collections.abc import Sequence
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, ResultSet, Tag
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(requests.RequestException),
    reraise=True,
)
def fetch_page(
    page_num: int, base_url: str, headers: dict[str, str]
) -> BeautifulSoup | None:
    """Fetch a single page of the blog with retry logic using tenacity.
    Returns None if all retries fail.
    """
    url = base_url.format(page_num)
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except (requests.RequestException, RetryError) as e:
        logging.error(f"Failed to fetch {url}: {e}")

        return None


def _first_str(val: object) -> str | None:
    if isinstance(val, str):
        return val
    if isinstance(val, list) and val and isinstance(val[0], str):
        return val[0]
    return None


def fix_image_urls(stories: Sequence[Tag], root_url: str) -> None:
    """Normalize image URLs in each story to ensure they are valid absolute URLs.

    Modifies the Tag objects in place.

    Args:
        stories: Sequence of story <article> tags.
        root_url: Root URL to join with relative paths.
    """
    for story in stories:
        for img in story.select("img"):
            # Prefer data-src if present; coerce to str
            data_src = _first_str(img.get("data-src"))
            if data_src is not None:
                img["src"] = data_src

            # Remove unused attrs
            img.attrs.pop("data-src", None)
            img.attrs.pop("data-srcset", None)
            img.attrs.pop("data-sizes", None)

            # Ensure src is absolute; coerce to str before urljoin
            src = _first_str(img.get("src"))
            if src is not None:
                img["src"] = urljoin(root_url, src)


def extract_stories(soup: BeautifulSoup) -> ResultSet[Tag]:
    """Extract all story elements from the page.

    Args:
        soup: Parsed BeautifulSoup object for the page.

    Returns:
        A list-like ResultSet of <article> elements.
    """
    return soup.select("article")


def build_html(stories: Sequence[Tag]) -> str:
    """Build a complete HTML document containing all stories.

    Args:
        stories: Sequence of story <article> tags.

    Returns:
        A string containing the full HTML document.
    """
    return (
        "<html><head><meta charset='utf-8'><title>All Stories</title></head><body>"
        + "".join(map(str, stories))
        + "</body></html>"
    )


def main(
    base_url: str = "https://roadtothesea.com/blog/page/{}",
    root_url: str = "https://roadtothesea.com",
    headers: dict[str, str] | None = None,
    output_file: str = "all_stories.html",
) -> None:
    """Crawl through paginated blog pages, extract stories, normalize images,
    and save the results into a single HTML file.

    Args:
        base_url: Template for paginated blog URLs.
        root_url: Root domain to resolve relative image URLs.
        headers: Optional HTTP headers to use in requests.
        output_file: Path to write the combined HTML file.
    """
    if headers is None:
        headers = {"User-Agent": "Mozilla/5.0"}

    page_num: int = 1
    all_stories: list[Tag] = []

    # Loop through paginated blog until no more pages are found
    while soup := fetch_page(page_num, base_url, headers):
        logging.info("Loading page %s", page_num)

        # Stop if no stories on this page
        if not (stories := extract_stories(soup)):
            break

        # Fix images and add stories to collection
        fix_image_urls(stories, root_url)
        all_stories.extend(stories)
        page_num += 1

    # Write the final HTML document
    Path(output_file).write_text(build_html(all_stories), encoding="utf-8")


if __name__ == "__main__":
    main()
