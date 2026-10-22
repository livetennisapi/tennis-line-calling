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
TOURS = {"ATP", "WTA", "combined", "team"}
LINE_CALLING = [
    "line_judges",
    "challenge_system",
    "elc_some_courts",
    "elc_all_courts",
    "unknown",
]
CHALLENGE = {"yes", "no", "unknown"}
CONFIDENCE = ["confirmed", "inferred", "unknown"]
SURFACES = {"Hard", "Hard (indoor)", "Clay", "Grass", ""}
SEASONS = range(2017, 2027)


def check(path: Path) -> tuple[list[str], list[dict]]:
    errors: list[str] = []
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != COLUMNS:
            return [f"header is {reader.fieldnames}, expected {COLUMNS}"], []
        rows = list(reader)

    seen: set[tuple[str, str, str]] = set()
    for n, row in enumerate(rows, start=2):
        where = f"line {n} ({row.get('event')} {row.get('season')})"
        if None in row or any(v is None for v in row.values()):
            errors.append(f"{where}: wrong number of fields")
            continue
        for col in ("event", "tour", "season", "line_calling", "challenge_review", "confidence"):
            if not row[col].strip():
                errors.append(f"{where}: {col} is empty")
        if row["tour"] not in TOURS:
            errors.append(f"{where}: tour {row['tour']!r} not allowed")
        if not row["season"].isdigit() or int(row["season"]) not in SEASONS:
            errors.append(f"{where}: season {row['season']!r} outside 2017-2026")
        if row["surface"] not in SURFACES:
            errors.append(f"{where}: surface {row['surface']!r} not allowed")
        if row["line_calling"] not in LINE_CALLING:
            errors.append(f"{where}: line_calling {row['line_calling']!r} not allowed")
        if row["challenge_review"] not in CHALLENGE:
            errors.append(f"{where}: challenge_review {row['challenge_review']!r} not allowed")
        if row["confidence"] not in CONFIDENCE:
            errors.append(f"{where}: confidence {row['confidence']!r} not allowed")

        known = row["line_calling"] != "unknown" or row["confidence"] != "unknown"
        if known:
            url = urlparse(row["source_url"])
            if url.scheme != "https" or not url.netloc:
                errors.append(f"{where}: non-unknown row needs an https source_url")
            if not row["source_title"].strip():
                errors.append(f"{where}: non-unknown row needs a source_title")
        if row["line_calling"] == "unknown" and row["confidence"] != "unknown":
            errors.append(f"{where}: line_calling unknown must have confidence unknown")
        if row["confidence"] == "unknown" and row["line_calling"] != "unknown":
            errors.append(f"{where}: confidence unknown must have line_calling unknown")
        if row["line_calling"] == "line_judges" and row["elc_system"]:
            errors.append(f"{where}: elc_system set but line_calling has no ELC")

        if row["source_date"]:
            try:
                d = datetime.date.fromisoformat(row["source_date"])
            except ValueError:
                errors.append(f"{where}: source_date {row['source_date']!r} is not YYYY-MM-DD")
            else:
                if len(row["source_date"]) != 10 or d > datetime.date.today():
                    errors.append(f"{where}: source_date {row['source_date']!r} invalid or in the future")

        for col in COLUMNS:
            if row[col] != row[col].strip() or "\n" in row[col]:
                errors.append(f"{where}: {col} has stray whitespace or a line break")

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
    print("OK" if not errors else f"FAILED: {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
