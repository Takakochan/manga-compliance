from typing import Literal

from pydantic import BaseModel

Category = Literal[
    "violence",
    "bad_language",
    "fear",
    "sex",
    "drugs",
    "discrimination",
    "gambling",
    "prohibited_symbol",
]
Severity = Literal["mild", "moderate", "strong"]
Source = Literal["image", "text"]
Outcome = Literal["ok", "review", "age_restricted", "edit_required", "blocked"]

SEVERITY_RANK: dict[Severity, int] = {"mild": 1, "moderate": 2, "strong": 3}
OUTCOME_RANK: dict[Outcome, int] = {
    "ok": 0,
    "review": 1,
    "age_restricted": 2,
    "edit_required": 3,
    "blocked": 4,
}


class Flag(BaseModel):
    bbox: list[int]
    source: Source
    category: Category
    severity: Severity
    confidence: float
    evidence: str


class FlagsResult(BaseModel):
    status: str
    summary: str
    flags: list[Flag]
    size: list[int]
    seconds: float
    error: str | None = None


class Rule(BaseModel):
    id: str
    country: str
    category: Category
    min_severity: Severity = "mild"
    sources: list[Source] = ["image", "text"]
    outcome: Outcome
    label: str
    doc: str
    query: str


class Finding(BaseModel):
    flag: Flag
    rule: Rule


class CountryVerdict(BaseModel):
    country: str
    outcome: Outcome
    findings: list[Finding]
