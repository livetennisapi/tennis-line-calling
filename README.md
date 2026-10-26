# Electronic line calling in tennis: which tournaments use it (2017 to 2026)

Every ATP Tour event has used live electronic line calling, with no line judges, since the start of 2025.
The Australian Open (2021), US Open (2021) and Wimbledon (2025) also call every line electronically.
Roland Garros is the one Grand Slam that still uses human line judges, and it kept them in 2026.
This dataset shows, event by event and season by season, how lines were called at the top of professional tennis from 2017 to 2026.
Each row is one event, in one season, for one tour. Every row with a known value links the page that supports it.

Published by [Live Tennis API](https://livetennisapi.com) under CC BY 4.0.
The data is in [`data/line_calling.csv`](data/line_calling.csv).

## What it covers

- The four Grand Slams, one combined row per event.
- The ATP Finals and the Next Gen ATP Finals.
- The nine ATP Masters 1000 events.
- WTA 1000 events, and the Premier Mandatory and Premier 5 events that came before them.
- The WTA Finals.
- The ATP Cup, United Cup, Davis Cup Finals and Billie Jean King Cup Finals.
- ATP 500 events in 2025 and 2026 only. The ATP's own tour-wide statements cover those two seasons.

Events that were not held have no row.
That covers Wimbledon 2020, the other events cancelled in 2020, the events in China from 2020 to 2022, and Wuhan in 2023.
Events still to be played after 22 October 2026 are also left out.

## Columns

The file is UTF-8 CSV with a header row and LF line endings.
`data/line_calling.csv-metadata.json` describes the same columns in the W3C CSV on the Web format.

| Column | Meaning |
|---|---|
| `event` | Tournament name. |
| `tour` | `ATP`, `WTA`, `combined` for the Grand Slams, or `team` for team events. |
| `season` | Year the event was played. |
| `surface` | `Hard`, `Hard (indoor)`, `Clay` or `Grass`. |
| `line_calling` | One of the five values described below. |
| `elc_system` | The electronic system the source names: `Hawk-Eye`, `Hawk-Eye Live`, `FoxTenn` or `Bolt6`. Blank when the source names none. |
| `challenge_review` | `yes`, `no` or `unknown`. Could players challenge a call or ask for a review? |
| `notes` | A short plain note on the row. |
| `source_url` | The page that supports the row. |
| `source_title` | The title of that page. Where the page carries a wire story, the agency follows in brackets, such as (Associated Press). |
| `source_date` | The publication date shown on that page, as YYYY-MM-DD. For a PDF that prints no date, the date in its file name or its creation date. Blank when no date can be trusted. |
| `confidence` | `confirmed`, `inferred` or `unknown`. |

### line_calling values

- `line_judges`: human line judges and no electronic challenge. Clay events used this before electronic calling arrived.
- `challenge_system`: human line judges, with an electronic review players could request on some or all courts.
- `elc_some_courts`: live electronic calling on some courts and line judges on others.
- `elc_all_courts`: live electronic calling on every court, with no line judges.
- `unknown`: we found no source we trust for that row.

### confidence values

- `confirmed`: a source published during or after the event says it for that event and that season.
- `inferred`: the source is a tour-wide rule or an announcement made before the event. Or it describes an adjacent season or a range of seasons. The note says which.
- `unknown`: no supporting source. These rows always have `line_calling` set to `unknown`. Some still link a page that gives context, such as the system a tournament named.

### challenge_review

For rows with full electronic calling, we only say `no` when the source says players could not challenge.
Otherwise we leave it `unknown`.
Several events now offer video review for things like double bounces and touches.
That counts as `yes` only when the source says players could ask for it.

## Coverage

These counts come from running `scripts/validate.py` on the current file.

Total rows: 278.

| line_calling | Rows |
|---|---|
| line_judges | 28 |
| challenge_system | 64 |
| elc_some_courts | 1 |
| elc_all_courts | 107 |
| unknown | 78 |

| confidence | Rows |
|---|---|
| confirmed | 41 |
| inferred | 159 |
| unknown | 78 |

The rows cite 75 distinct source pages.

## Method

We searched tour press releases, tour rulebooks, tournament websites and major news outlets.
We preferred primary sources from the tours, the tournaments and the ITF.
News reports were used where no primary source was found.
Every cited page was read before it was cited.
The CSV does not store quotations, but each row's claim was checked against the page text.

Before release, every source page was fetched again and checked against the quote we had recorded for it.
Every `confirmed` row on a Grand Slam or a season final was checked again by hand, along with a sample of `inferred` rows.
Rows the page did not support for that event and season were moved to `inferred` or `unknown`.

Some rules we followed:

- A wrong row is worse than a blank one. When in doubt, the row is `unknown`.
- A tour-wide rule counts as a source for every event it covers. Those rows are marked `inferred` and cite the rule.
- An announcement made before an event is `inferred`. Only a report from during or after the event makes a row `confirmed`.
- For a combined ATP and WTA event, a source about the whole tournament can support both rows. A source about one tour's matches makes the other tour's row `inferred`.
- Where sources disagree, the note says so, or the row is left `unknown`.

### US Open 2021

Sources disagree on the first US Open with no line judges.
An NPR report from September 2022 reads as if 2022 was the first fully electronic year.
We use 2021.
The USTA announced in May 2021 that Hawk-Eye Live would cover every court that year.
ESPN reported in September 2022 that the US Open extended the system to Ashe and Armstrong in 2021.
AP reported from the 2021 semi-finals that there were no line judges to argue with.
An AP report from October 2024 also says the US Open has had no line judges since 2021.

## Known gaps

The rows below are `unknown`. Corrections with a source are very welcome.

- ATP Cup 2020 to 2022.
- ATP Finals 2021 to 2024 in Turin.
- Billie Jean King Cup Finals 2021 to 2026.
- Davis Cup Finals 2019 and 2021 to 2025.
- United Cup 2023 to 2025.
- WTA Finals 2021 and 2023 to 2025.
- Italian Open: ATP 2020 to 2023, WTA 2017 and 2019 to 2024.
- Madrid Open 2022 and 2023, both tours.
- Miami Open: ATP 2022 and 2023, WTA 2022, 2023 and 2025.
- Cincinnati Open: ATP 2022 and 2023, WTA 2022, 2023 and 2025.
- Canadian Open: ATP 2022 and 2023, WTA 2023 to 2025.
- Paris Masters 2020 to 2024. Sources disagree on 2021.
- Shanghai Masters 2023 and 2024.
- Indian Wells Open, WTA 2025.
- WTA events in Doha, Dubai, Beijing, Wuhan and Guadalajara in several seasons.

The 2026 WTA rows cite the rulebook edition dated 22 December 2025, which was published before the season began.

Other limits worth knowing:

- Many rows are `inferred` from tour-wide rules. A rule says what events had to do. It does not prove what happened at each one.
- Court-by-court detail is rarely published. `elc_all_courts` rows that rest on a tour rule have not been checked court by court.
- ATP 500 and WTA 500 events before 2025 are not included. WTA 500 events in 2026 are not included either.
- Source pages can move or disappear. We do not archive copies.

## Checking the file

Run the validator with Python 3.10 or later. It needs no extra packages.

```
python3 scripts/validate.py
```

It checks the header, the allowed values and the dates.
It holds a list of every edition in scope. It reports a missing row and rejects a row for an edition that was not played.
It checks the rules that tie columns together.
A `confirmed` row must cite a source dated no earlier than the event's first possible day.
It prints the coverage counts above and exits with status 1 if any check fails.

## Licence

The dataset is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
You can share and adapt it, including for commercial use, as long as you give credit.
`LICENSE` holds the full legal code.

## How to cite

Live Tennis API (2026). *Electronic line calling in professional tennis, by tournament and season* (Version 1.0.0) [Data set]. https://github.com/livetennisapi/tennis-line-calling

```bibtex
@misc{livetennisapi_line_calling_2026,
  author       = {{Live Tennis API}},
  title        = {Electronic line calling in professional tennis, by tournament and season},
  year         = {2026},
  version      = {1.0.0},
  howpublished = {\url{https://github.com/livetennisapi/tennis-line-calling}},
  note         = {Data set, CC BY 4.0}
}
```

`CITATION.cff` holds the same details in the Citation File Format.

## Updates and corrections

Open an issue at https://github.com/livetennisapi/tennis-line-calling/issues.
Please include the event, the season and a link to a source that supports the change.
We plan to add new seasons as events are played, and to fill gaps as sources turn up.
Each change to the data gets a new version number.
