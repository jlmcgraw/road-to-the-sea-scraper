from pytest import CaptureFixture
from road_to_the_sea_scraper.main import main


def test_raise(capsys: CaptureFixture[str]) -> None:
    main()
    assert "Ritchie Blackmore" in capsys.readouterr().out
