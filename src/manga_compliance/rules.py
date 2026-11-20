from pathlib import Path

import yaml

from manga_compliance.models import (
    OUTCOME_RANK,
    SEVERITY_RANK,
    CountryVerdict,
    Finding,
    Flag,
    Outcome,
    Rule,
)


def load_rules(rules_dir: Path) -> list[Rule]:
    rules: list[Rule] = []
    for path in sorted(rules_dir.glob("*.yaml")):
        for raw in yaml.safe_load(path.read_text(encoding="utf-8")) or []:
            rules.append(Rule.model_validate(raw))
    return rules


def matches(rule: Rule, flag: Flag) -> bool:
    return (
        rule.category == flag.category
        and flag.source in rule.sources
        and SEVERITY_RANK[flag.severity] >= SEVERITY_RANK[rule.min_severity]
    )


def strictest(rules: list[Rule], flag: Flag) -> Rule | None:
    hits = [r for r in rules if matches(r, flag)]
    return max(hits, key=lambda r: OUTCOME_RANK[r.outcome]) if hits else None


def judge(flags: list[Flag], rules: list[Rule], country: str) -> CountryVerdict:
    local = [r for r in rules if r.country == country]
    findings = [Finding(flag=flag, rule=rule) for flag in flags if (rule := strictest(local, flag))]
    outcomes: list[Outcome] = [f.rule.outcome for f in findings]
    outcome: Outcome = max(outcomes, key=OUTCOME_RANK.__getitem__, default="ok")
    return CountryVerdict(country=country, outcome=outcome, findings=findings)
