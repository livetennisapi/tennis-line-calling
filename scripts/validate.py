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
FIRST_SEASON, LAST_SEASON = 2017, 2026

# Which tour values each event may carry.
GRAND_SLAMS = {"Australian Open", "Roland Garros", "Wimbledon", "US Open"}
TEAM_EVENTS = {"ATP Cup", "United Cup", "Davis Cup Finals", "Billie Jean King Cup Finals"}
ATP_ONLY = {"ATP Finals", "Next Gen ATP Finals"}
WTA_ONLY = {"WTA Finals", "Wuhan Open", "Guadalajara Open"}

# Event editions that were not played. A row for one of these is an error.
NOT_HELD = {
    ("Wimbledon", "combined", 2020),
    ("Indian Wells Open", "ATP", 2020),
    ("Indian Wells Open", "WTA", 2020),
    ("Miami Open", "ATP", 2020),
    ("Miami Open", "WTA", 2020),
    ("Monte-Carlo Masters", "ATP", 2020),
    ("Madrid Open", "ATP", 2020),
    ("Madrid Open", "WTA", 2020),
    ("Canadian Open", "ATP", 2020),
    ("Canadian Open", "WTA", 2020),
    ("Next Gen ATP Finals", "ATP", 2020),
    ("WTA Finals", "WTA", 2020),
    ("Davis Cup Finals", "team", 2020),
    ("Billie Jean King Cup Finals", "team", 2020),
    ("Shanghai Masters", "ATP", 2020),
    ("Shanghai Masters", "ATP", 2021),
    ("Shanghai Masters", "ATP", 2022),
    ("China Open", "WTA", 2020),
    ("China Open", "WTA", 2021),
    ("China Open", "WTA", 2022),
    ("Wuhan Open", "WTA", 2020),
    ("Wuhan Open", "WTA", 2021),
    ("Wuhan Open", "WTA", 2022),
    ("Wuhan Open", "WTA", 2023),
}
# Team events that only ran in some seasons.
SEASON_SPAN = {
    "ATP Cup": (2020, 2022),
    "United Cup": (2023, LAST_SEASON),
    "Davis Cup Finals": (2019, LAST_SEASON),
    "Billie Jean King Cup Finals": (2021, LAST_SEASON),
}


def allowed_tours(event: str) -> set[str]:
    if event in GRAND_SLAMS:
        return {"combined"}
    if event in TEAM_EVENTS:
        return {"team"}
    if event in ATP_ONLY:
        return {"ATP"}
    if event in WTA_ONLY:
        return {"WTA"}
    return {"ATP", "WTA"}


def check_row(row: dict, where: str, today: datetime.date) -> list[str]:
    errors: list[str] = []
    for col in COLUMNS:
        if row[col] != row[col].strip() or "\n" in row[col] or "\r" in row[col]:
            errors.append(f"{where}: {col} has stray whitespace or a line break")
    for col in ("event", "tour", "season", "surface", "line_calling", "challenge_review", "notes", "confidence"):
        if not row[col].strip():
            errors.append(f"{where}: {col} is empty")

    event, tour = row["event"], row["tour"]
    if tour not in allowed_tours(event):
        errors.append(f"{where}: tour {tour!r} not allowed for {event}")
    season = int(row["season"]) if row["season"].isdigit() else None
    if season is None or not FIRST_SEASON <= season <= LAST_SEASON:
        errors.append(f"{where}: season {row['season']!r} outside {FIRST_SEASON}-{LAST_SEASON}")
    elif (event, tour, season) in NOT_HELD:
        errors.append(f"{where}: this edition was not played")
    elif event in SEASON_SPAN and not SEASON_SPAN[event][0] <= season <= SEASON_SPAN[event][1]:
        errors.append(f"{where}: {event} was not played in {season}")

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

    if row["source_date"]:
        try:
            d = datetime.date.fromisoformat(row["source_date"])
        except ValueError:
            errors.append(f"{where}: source_date {row['source_date']!r} is not YYYY-MM-DD")
        else:
            if len(row["source_date"]) != 10 or d > today:
                errors.append(f"{where}: source_date {row['source_date']!r} invalid or in the future")
            # A source dated before the season cannot report what happened in it.
            if conf == "confirmed" and season is not None and d.year < season:
                errors.append(f"{where}: confirmed row cites a source dated before the season")
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
    seen: set[tuple[str, str, str]] = set()
    for n, row in enumerate(rows, start=2):
        where = f"line {n} ({row.get('event')} {row.get('tour')} {row.get('season')})"
        if None in row or any(v is None for v in row.values()):
            errors.append(f"{where}: wrong number of fields")
            continue
        errors.extend(check_row(row, where, today))
        key = (row["event"], row["season"], row["tour"])
        if key in seen:
            errors.append(f"{where}: duplicate event, season and tour")
        seen.add(key)
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
