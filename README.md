# Electronic line calling in professional tennis, by tournament and season

This dataset records how lines were called at the top professional tennis events from 2017 to 2026.
Each row is one event, in one season, for one tour.
It says whether line judges, a player challenge system or electronic line calling was used.
Every row that is not marked unknown links to the page that supports it.

It is published by [Live Tennis API](https://livetennisapi.com).

The data is in `data/line_calling.csv`.

## What it covers

- The four Grand Slams, one combined row per event.
- The ATP Finals and the Next Gen ATP Finals.
- The nine ATP Masters 1000 events.
- WTA 1000 events, and the Premier Mandatory and Premier 5 events that came before them.
- The WTA Finals.
- The ATP Cup, United Cup, Davis Cup Finals and Billie Jean King Cup Finals.
- ATP 500 events in 2025 and 2026 only. The ATP's own tour-wide statements cover those two seasons.

Events that were not held have no row. Wimbledon 2020 and the 2020 events cancelled during the pandemic are left out.
Events still to be played after 22 October 2026 are also left out.

## Columns

The file is UTF-8 CSV with a header row.

| Column | Meaning |
|---|---|
| `event` | Tournament name. |
| `tour` | `ATP`, `WTA`, `combined` for the Grand Slams, or `team` for team events. |
| `season` | Year the event was played. |
| `surface` | `Hard`, `Hard (indoor)`, `Clay` or `Grass`. |
| `line_calling` | One of the five values described below. |
| `elc_system` | The electronic system the source names. Blank when the source names none. |
| `challenge_review` | `yes`, `no` or `unknown`. Did players have a challenge or review of calls? |
| `notes` | A short plain note on the row. |
| `source_url` | The page that supports the row. |
| `source_title` | The title of that page. |
| `source_date` | The publication date shown on that page, as YYYY-MM-DD. Blank when the page shows no date. |
| `confidence` | `confirmed`, `inferred` or `unknown`. |

### line_calling values

- `line_judges`: human line judges and no electronic challenge. Clay events used this before electronic calling arrived.
- `challenge_system`: human line judges, with an electronic review players could request on some or all courts.
- `elc_some_courts`: live electronic calling on some courts and line judges on others.
- `elc_all_courts`: live electronic calling on every court, with no line judges.
- `unknown`: we found no source we trust for that row.

### confidence values

- `confirmed`: the source says it for that event and that season.
- `inferred`: the source is a tour-wide rule, or a statement about an adjacent season or a range of seasons. The note says which.
- `unknown`: no supporting source. These rows always have `line_calling` set to `unknown`.

### challenge_review

For rows with full electronic calling, we only say `no` when the source says players could not challenge.
Otherwise we leave it `unknown`.
Several events now offer video review for things like double bounces. That is not counted as a line-call challenge unless the source says players could request it.

## Coverage

These counts come from running `scripts/validate.py` on the current file.

Total rows: 278.

| line_calling | Rows |
|---|---|
| line_judges | 28 |
| challenge_system | 64 |
| elc_some_courts | 3 |
| elc_all_courts | 105 |
| unknown | 78 |

| confidence | Rows |
|---|---|
| confirmed | 50 |
| inferred | 150 |
| unknown | 78 |

The rows cite 67 distinct source pages.

## Method

We searched tour press releases, tour rulebooks, tournament websites and major news outlets.
We preferred primary sources from the tours, the tournaments and the ITF.
News reports were used where no primary source was found.
Each source page was opened and read before it was cited. The CSV does not store quotations, but each row's claim was checked against the page text.
A sample of about twenty sources was opened a second time before release to confirm the quotes and dates.

Some rules we followed:

- A wrong row is worse than a blank one. When in doubt, the row is `unknown`.
- A tour-wide rule counts as a source for every event it covers. Those rows are marked `inferred` and cite the rule.
- For a combined ATP and WTA event, a source about the whole tournament can support both rows.
- Where sources disagree, the note says so, or the row is left `unknown`.

## Known gaps

The rows below are `unknown`. Corrections with a source are very welcome.

- ATP Cup 2020 to 2022.
- ATP Finals 2021 to 2024 in Turin.
- Billie Jean King Cup Finals 2021 to 2026.
- Davis Cup Finals 2019 and 2021 to 2025.
- United Cup 2023 to 2025.
- WTA Finals 2021 to 2025.
- Italian Open: ATP 2020 to 2023, WTA 2017 and 2019 to 2024.
- Madrid Open 2022 and 2023, both tours.
- Miami Open: ATP 2022 and 2023, WTA 2021 to 2023 and 2025.
- Cincinnati Open 2022 and 2023, both tours.
- Canadian Open: ATP 2022 and 2023, WTA 2023 to 2025.
- Paris Masters 2020 and 2022 to 2024.
- Shanghai Masters 2023 and 2024.
- Indian Wells Open, WTA 2025.
- WTA events in Doha, Dubai, Beijing, Wuhan and Guadalajara in several seasons.

Other limits worth knowing:

- Many rows are `inferred` from tour-wide rules. A rule says what events had to do. It does not prove what happened at each one.
- The 2026 WTA rows cite the July 2026 edition of the WTA rulebook. We have not checked whether earlier 2026 editions said the same.
- Court-by-court detail is rarely published. `elc_all_courts` rows that rest on a tour rule have not been checked court by court.
- ATP 500 and WTA 500 events before 2025 are not included. WTA 500 events in 2026 are not included either.
- Source pages can move or disappear. We do not archive copies.

## Checking the file

Run the validator with Python 3.10 or later. It needs no extra packages.

```
python3 scripts/validate.py
```

It checks the header, the allowed values, the dates and the source rules.
It prints the coverage counts above and exits with an error if any check fails.

## Licence

The dataset is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
You can share and adapt it, including for commercial use, as long as you give credit.
See `LICENSE` for details.

## How to cite

Please cite the publisher named above, the dataset title, version 1.0.0, the release date and this URL:
https://github.com/livetennisapi/tennis-line-calling

`CITATION.cff` holds these details in a machine-readable form. GitHub can turn it into APA or BibTeX for you.

## Updates and corrections

Corrections are welcome via issues.
Please include the event, the season and a link to a source that supports the change.
We plan to add new seasons as events are played, and to fill gaps as sources turn up.
Each change to the data gets a new version number.
