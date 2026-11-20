import json
from pathlib import Path

import pytest

from manga_compliance import __main__ as cli
from manga_compliance.models import FlagsResult
from manga_compliance.settings import settings


def fake_result(status: str, flags: list[dict[str, object]] | None = None) -> FlagsResult:
    return FlagsResult.model_validate(
        {
            "status": status,
            "summary": "",
            "flags": flags or [],
            "size": [10, 10],
            "seconds": 1.0,
            "error": None if status == "ok" else "model declined",
        }
    )


def run_check(
    result: FlagsResult, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> dict[str, object]:
    async def fake_call_flags(image: Path) -> FlagsResult:
        return result

    monkeypatch.setattr(cli, "call_flags", fake_call_flags)
    monkeypatch.setattr(settings, "out_dir", tmp_path)
    cli.check(str(tmp_path / "page.png"), "DE,AU")
    report: dict[str, object] = json.loads((tmp_path / "page.report.json").read_text())
    return report


@pytest.mark.parametrize("status", ["refused", "unparsed", "error"])
def test_page_the_engine_did_not_analyse_is_unresolved_not_ok(
    status: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    report = run_check(fake_result(status), tmp_path, monkeypatch)
    printed = capsys.readouterr().out
    assert "UNRESOLVED" in printed
    assert "] ok" not in printed
    assert report["checked"] is False
    assert report["verdicts"] == []


def test_analysed_page_without_flags_is_ok(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    report = run_check(fake_result("ok"), tmp_path, monkeypatch)
    assert "[DE] ok" in capsys.readouterr().out
    assert report["checked"] is True
