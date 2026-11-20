import asyncio
import json
from pathlib import Path

import fire

from manga_compliance.client import FukidashiClient
from manga_compliance.models import CountryVerdict, FlagsResult
from manga_compliance.rules import judge, load_rules
from manga_compliance.settings import settings


async def call_health() -> bool:
    async with FukidashiClient() as client:
        return await client.health()


async def call_flags(image: Path) -> FlagsResult:
    async with FukidashiClient() as client:
        return await client.flags(image)


def print_verdict(verdict: CountryVerdict) -> None:
    print(f"\n[{verdict.country}] {verdict.outcome}")
    for finding in verdict.findings:
        flag, rule = finding.flag, finding.rule
        print(f"  {rule.id:<16} {flag.category}/{flag.severity}  {rule.label}")
        print(f"      evidence: {flag.evidence}")


def health() -> None:
    print("ok" if asyncio.run(call_health()) else "not reachable")


def flags(image: str) -> None:
    result = asyncio.run(call_flags(Path(image)))
    print(result.model_dump_json(indent=2))


def check(image: str, countries: str | tuple[str, ...] = "DE,AU") -> None:
    codes = countries.split(",") if isinstance(countries, str) else list(countries)
    result = asyncio.run(call_flags(Path(image)))
    checked = result.status == "ok"
    verdicts: list[CountryVerdict] = []
    if checked:
        rules = load_rules(settings.rules_dir)
        verdicts = [judge(result.flags, rules, code) for code in codes]
        print(f"summary: {result.summary}")
        print(f"flags: {len(result.flags)}  ({result.seconds}s)")
        for verdict in verdicts:
            print_verdict(verdict)
    else:
        # No flags here means "not analysed", not "nothing found": never judge it as ok.
        print(f"UNRESOLVED: the engine returned status '{result.status}'", end="")
        print(f" ({result.error})" if result.error else "")
        print(f"Not checked for {', '.join(codes)}. Review this page by hand.")
    settings.out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "image": image,
        "checked": checked,
        "result": result.model_dump(),
        "verdicts": [v.model_dump() for v in verdicts],
    }
    out = settings.out_dir / f"{Path(image).stem}.report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nsaved {out}")


def main() -> None:
    fire.Fire({"health": health, "flags": flags, "check": check})


if __name__ == "__main__":
    main()
