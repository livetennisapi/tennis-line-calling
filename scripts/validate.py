#!/usr/bin/env python3
"""Validate data/line_calling.csv and print coverage counts.

Exits with status 1 if any check fails.
"""

import csv
import datetime
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "line_calling.csv"

COLUMNS = [
    "event",
    "tour",
    "season",
    "surface",
    "line_calling",
    "elc_system",
    "challenge_review",
    "notes",
    "source_url",
    "source_title",
    "source_date",
    "confidence",
]
LINE_CALLING = [
    "line_judges",
    "challenge_system",
    "elc_some_courts",
    "elc_all_courts",
    "unknown",
]
CHALLENGE = {"yes", "no", "unknown"}
CONFIDENCE = ["confirmed", "inferred", "unknown"]
SURFACES = {"Hard", "Hard (indoor)", "Clay", "Grass"}
ELC_SYSTEMS = {"", "Hawk-Eye", "Hawk-Eye Live", "FoxTenn", "Bolt6"}
SEASONS = range(2017, 2027)

# The editions in scope. Each entry is (event, tour): (seasons, earliest start).
# The earliest start is a month and day no edition (qualifying included) began
# before. A confirmed row needs a source dated on or after it.
ALL = set(SEASONS)
MASTERS_SEASONS = ALL - {2020}
SCOPE = {
    ("Australian Open", "combined"): (ALL, (1, 5)),
    ("Roland Garros", "combined"): (ALL, (5, 15)),
    ("Wimbledon", "combined"): (ALL - {2020}, (6, 15)),
    ("US Open", "combined"): (ALL, (8, 10)),
    ("ATP Finals", "ATP"): (ALL - {2026}, (11, 1)),
    ("Next Gen ATP Finals", "ATP"): (ALL - {2020, 2026}, (11, 1)),
    ("Indian Wells Open", "ATP"): (MASTERS_SEASONS, (2, 28)),
    ("Miami Open", "ATP"): (MASTERS_SEASONS, (3, 10)),
    ("Monte-Carlo Masters", "ATP"): (MASTERS_SEASONS, (3, 30)),
    ("Madrid Open", "ATP"): (MASTERS_SEASONS, (4, 15)),
    ("Italian Open", "ATP"): (ALL, (5, 1)),
    ("Canadian Open", "ATP"): (MASTERS_SEASONS, (7, 20)),
    ("Cincinnati Open", "ATP"): (ALL, (7, 30)),
    ("Shanghai Masters", "ATP"): (ALL - {2020, 2021, 2022}, (9, 25)),
    ("Paris Masters", "ATP"): (ALL - {2026}, (10, 20)),
    ("Indian Wells Open", "WTA"): (MASTERS_SEASONS, (2, 28)),
    ("Miami Open", "WTA"): (MASTERS_SEASONS, (3, 10)),
    ("Madrid Open", "WTA"): (MASTERS_SEASONS, (4, 15)),
    ("Italian Open", "WTA"): (ALL, (5, 1)),
    ("Canadian Open", "WTA"): (MASTERS_SEASONS, (7, 20)),
    ("Cincinnati Open", "WTA"): (ALL, (7, 30)),
    ("China Open", "WTA"): (ALL - {2020, 2021, 2022}, (9, 15)),
    ("Wuhan Open", "WTA"): ({2017, 2018, 2019, 2024, 2025, 2026}, (9, 15)),
    # Dubai and Doha only in the seasons they were Premier 5 or WTA 1000.
    ("Dubai Tennis Championships", "WTA"): ({2017, 2019, 2021, 2023, 2024, 2025, 2026}, (2, 5)),
    ("Qatar Open", "WTA"): ({2018, 2020, 2022, 2024, 2025, 2026}, (2, 1)),
    ("Guadalajara Open", "WTA"): ({2022, 2023}, (9, 10)),
    ("WTA Finals", "WTA"): (ALL - {2020, 2026}, (10, 15)),
    ("ATP Cup", "team"): ({2020, 2021, 2022}, (1, 1)),
    ("United Cup", "team"): ({2023, 2024, 2025, 2026}, None),  # starts late in December the year before
    ("Davis Cup Finals", "team"): ({2019, 2021, 2022, 2023, 2024, 2025}, (9, 1)),
    ("Billie Jean King Cup Finals", "team"): ({2021, 2022, 2023, 2024, 2025, 2026}, (9, 1)),
}
# ATP 500 events, 2025 and 2026 only. Basel and Vienna 2026 were still to come at release.
ATP_500 = {
    "Rotterdam Open": (1, 25), "Dallas Open": (1, 25), "Qatar Open": (2, 1), "Rio Open": (2, 1),
    "Dubai Tennis Championships": (2, 5), "Mexican Open": (2, 15), "Barcelona Open": (4, 5),
    "BMW Open": (4, 5), "Hamburg Open": (5, 10), "Halle Open": (6, 5), "Queen's Club Championships": (6, 5),
    "Washington Open": (7, 15), "China Open": (9, 15), "Japan Open": (9, 15),
    "Swiss Indoors": (10, 10), "Vienna Open": (10, 10),
}
for _event, _start in ATP_500.items():
    _seasons = {2025} if _event in ("Swiss Indoors", "Vienna Open") else {2025, 2026}
    SCOPE[(_event, "ATP")] = (_seasons, _start)
# Editions that moved to a later date than usual.
START_OVERRIDES = {
    ("Indian Wells Open", 2021): (10, 1),
    ("Roland Garros", 2020): (9, 20),
    ("Italian Open", 2020): (9, 10),
    ("Cincinnati Open", 2020): (8, 15),
}


def expected_keys() -> set[tuple[str, str, int]]:
    return {(event, tour, season) for (event, tour), (seasons, _) in SCOPE.items() for season in seasons}


def earliest_start(event: str, tour: str, season: int) -> datetime.date:
    if (event, season) in START_OVERRIDES:
        month, day = START_OVERRIDES[(event, season)]
        return datetime.date(season, month, day)
    start = SCOPE[(event, tour)][1]
    if start is None:
        return datetime.date(season - 1, 12, 20)
    return datetime.date(season, *start)


def check_row(row: dict, where: str, today: datetime.date) -> list[str]:
    errors: list[str] = []
    for col in COLUMNS:
        if row[col] != row[col].strip() or "\n" in row[col] or "\r" in row[col]:
            errors.append(f"{where}: {col} has stray whitespace or a line break")
    for col in ("event", "tour", "season", "surface", "line_calling", "challenge_review", "notes", "confidence"):
        if not row[col].strip():
            errors.append(f"{where}: {col} is empty")

    event, tour = row["event"], row["tour"]
    season = int(row["season"]) if row["season"].isdigit() else None
    in_scope = season is not None and (event, tour, season) in expected_keys()
    if not in_scope:
        errors.append(f"{where}: not an edition in scope (unknown event, wrong tour, not played or out of range)")

    lc, chal, conf = row["line_calling"], row["challenge_review"], row["confidence"]
    if row["surface"] not in SURFACES:
        errors.append(f"{where}: surface {row['surface']!r} not allowed")
    if lc not in LINE_CALLING:
        errors.append(f"{where}: line_calling {lc!r} not allowed")
    if chal not in CHALLENGE:
        errors.append(f"{where}: challenge_review {chal!r} not allowed")
    if conf not in CONFIDENCE:
        errors.append(f"{where}: confidence {conf!r} not allowed")
    if row["elc_system"] not in ELC_SYSTEMS:
        errors.append(f"{where}: elc_system {row['elc_system']!r} not allowed")

    # line_calling and confidence are unknown together or not at all.
    if (lc == "unknown") != (conf == "unknown"):
        errors.append(f"{where}: line_calling and confidence must both be unknown, or neither")
    # Values that follow from the definitions in the README.
    if lc == "line_judges" and (row["elc_system"] or chal != "no"):
        errors.append(f"{where}: line_judges needs a blank elc_system and challenge_review no")
    if lc == "challenge_system" and chal != "yes":
        errors.append(f"{where}: challenge_system needs challenge_review yes")
    if lc == "unknown" and chal != "unknown":
        errors.append(f"{where}: an unknown row needs challenge_review unknown")

    if conf != "unknown":
        url = urlparse(row["source_url"])
        if url.scheme != "https" or not url.netloc:
            errors.append(f"{where}: a sourced row needs an https source_url")
        if not row["source_title"].strip():
            errors.append(f"{where}: a sourced row needs a source_title")
    if row["source_url"] and not row["source_title"]:
        errors.append(f"{where}: source_url without source_title")
    if row["source_title"] and not row["source_url"]:
        errors.append(f"{where}: source_title without source_url")

    if row["source_date"]:
        try:
            d = datetime.date.fromisoformat(row["source_date"])
        except ValueError:
            errors.append(f"{where}: source_date {row['source_date']!r} is not YYYY-MM-DD")
        else:
            if len(row["source_date"]) != 10 or d > today:
                errors.append(f"{where}: source_date {row['source_date']!r} invalid or in the future")
            # A source dated before the event cannot report what happened at it.
            if conf == "confirmed" and in_scope and d < earliest_start(event, tour, season):
                errors.append(f"{where}: confirmed row cites a source dated before the event")
    elif conf == "confirmed":
        errors.append(f"{where}: confirmed row needs a dated source")
    return errors


def check(path: Path) -> tuple[list[str], list[dict]]:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        return ["file starts with a byte order mark"], []
    if b"\r" in raw:
        return ["file has CR line endings, expected LF"], []
    if not raw.endswith(b"\n"):
        return ["file does not end with a newline"], []

    errors: list[str] = []
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != COLUMNS:
            return [f"header is {reader.fieldnames}, expected {COLUMNS}"], []
        rows = list(reader)

    today = datetime.date.today()
    seen: set[tuple[str, str, int]] = set()
    for n, row in enumerate(rows, start=2):
        where = f"line {n} ({row.get('event')} {row.get('tour')} {row.get('season')})"
        if None in row or any(v is None for v in row.values()):
            errors.append(f"{where}: wrong number of fields")
            continue
        errors.extend(check_row(row, where, today))
        if row["season"].isdigit():
            key = (row["event"], row["tour"], int(row["season"]))
            if key in seen:
                errors.append(f"{where}: duplicate event, tour and season")
            seen.add(key)
    for event, tour, season in sorted(expected_keys() - seen):
        errors.append(f"missing row: {event} {tour} {season}")
    return errors, rows


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else CSV_PATH
    errors, rows = check(path)
    for e in errors:
        print(f"ERROR {e}")
    print(f"rows: {len(rows)}")
    by_lc = Counter(r["line_calling"] for r in rows)
    print("by line_calling:")
    for k in LINE_CALLING:
        print(f"  {k}: {by_lc.get(k, 0)}")
    by_conf = Counter(r["confidence"] for r in rows)
    print("by confidence:")
    for k in CONFIDENCE:
        print(f"  {k}: {by_conf.get(k, 0)}")
    sources = {r["source_url"] for r in rows if r["source_url"]}
    print(f"distinct source pages: {len(sources)}")
    print("OK" if not errors else f"FAILED: {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
