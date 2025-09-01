# tests/test_fetch_page.py
import requests
from bs4 import BeautifulSoup
from road_to_the_sea_scraper import main as r


class DummyResponse:
    def __init__(self, text: str = "", status: int = 200) -> None:
        self.text = text
        self.status_code = status

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"status={self.status_code}")


def test_fetch_page_success(monkeypatch):
    def fake_get(_url: str, headers: dict[str, str], timeout: int) -> DummyResponse:
        _headers = headers
        _timeout = timeout
        return DummyResponse("<html><body><article>ok</article></body></html>", 200)

    monkeypatch.setattr(requests, "get", fake_get)
    soup = r.fetch_page(1, "https://example.com/page/{}", {"UA": "x"})
    assert isinstance(soup, BeautifulSoup)
    assert soup.select_one("article").text == "ok"


def test_fetch_page_http_error_returns_none(monkeypatch):
    def fake_get(_url: str, headers: dict[str, str], timeout: int) -> DummyResponse:
        _headers = headers
        _timeout = timeout
        return DummyResponse("nope", 500)

    monkeypatch.setattr(requests, "get", fake_get)
    soup = r.fetch_page(1, "https://example.com/page/{}", {"UA": "x"})
    assert soup is None


# def test_fetch_page_retries_then_succeeds(monkeypatch):
#     calls: list[str] = []
#
#     def fake_get(url: str, headers: dict[str, str], timeout: int) -> DummyResponse:
#         calls.append("x")
#         # First call raises, second returns ok
#         if len(calls) == 1:
#             raise requests.ConnectionError("boom")
#         return DummyResponse("<html><body><article>ok</article></body></html>", 200)
#
#     monkeypatch.setattr(requests, "get", fake_get)
#     soup = r.fetch_page(1, "https://example.com/page/{}", {"UA": "x"})
#     assert isinstance(soup, BeautifulSoup)
#     assert len(calls) == 2


def test_fetch_page_retries_exhausted_returns_none(monkeypatch):
    def fake_get(_url: str, headers: dict[str, str], timeout: int) -> DummyResponse:
        _headers = headers
        _timeout = timeout
        raise requests.Timeout("slow")

    monkeypatch.setattr(requests, "get", fake_get)
    soup = r.fetch_page(1, "https://example.com/page/{}", {"UA": "x"})
    assert soup is None
