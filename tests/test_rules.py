from pathlib import Path

import pytest

from manga_compliance.models import Flag, Rule
from manga_compliance.rules import judge, load_rules


def flag(category: str, severity: str, source: str = "image") -> Flag:
    return Flag.model_validate(
        {
            "bbox": [0, 0, 10, 10],
            "source": source,
            "category": category,
            "severity": severity,
            "confidence": 0.9,
            "evidence": "test",
        }
    )


def rule(rule_id: str, category: str, min_severity: str, outcome: str, **extra: object) -> Rule:
    return Rule.model_validate(
        {
            "id": rule_id,
            "country": "DE",
            "category": category,
            "min_severity": min_severity,
            "outcome": outcome,
            "label": rule_id,
            "doc": "DE/x.md",
            "query": "q",
            **extra,
        }
    )


RULES = [
    rule("SYMBOL-BAN", "prohibited_symbol", "moderate", "blocked"),
    rule("SYMBOL-LOOK", "prohibited_symbol", "mild", "review"),
    rule("VIOLENCE", "violence", "strong", "age_restricted", sources=["image"]),
]


def test_no_flags_is_ok() -> None:
    assert judge([], RULES, "DE").outcome == "ok"


def test_mild_symbol_only_needs_review() -> None:
    verdict = judge([flag("prohibited_symbol", "mild")], RULES, "DE")
    assert verdict.outcome == "review"
    assert verdict.findings[0].rule.id == "SYMBOL-LOOK"


def test_strongest_rule_wins_for_one_flag() -> None:
    verdict = judge([flag("prohibited_symbol", "strong")], RULES, "DE")
    assert verdict.findings[0].rule.id == "SYMBOL-BAN"
    assert verdict.outcome == "blocked"


def test_page_outcome_is_the_strictest_finding() -> None:
    flags = [flag("violence", "strong"), flag("prohibited_symbol", "mild")]
    assert judge(flags, RULES, "DE").outcome == "age_restricted"


def test_rule_ignores_other_sources_and_weaker_flags() -> None:
    flags = [flag("violence", "strong", source="text"), flag("violence", "moderate")]
    assert judge(flags, RULES, "DE").findings == []


def test_rules_for_other_countries_do_not_apply() -> None:
    assert judge([flag("prohibited_symbol", "strong")], RULES, "AU").outcome == "ok"


@pytest.mark.parametrize("name", ["de.yaml", "au.yaml"])
def test_shipped_rule_files_load(name: str) -> None:
    rules = load_rules(Path("rules"))
    assert any(r.country == name[:2].upper() for r in rules)
