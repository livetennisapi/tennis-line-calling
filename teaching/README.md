# Teaching pack: electronic line calling, 2017 to 2026

Two charts and a set of questions for a statistics or data-literacy class. They use the dataset in this repository, so students can open the same CSV and check every answer.

The charts are 16:9, sized for a slide, in SVG and PNG:

- [`charts/line-calling-by-season.svg`](charts/line-calling-by-season.svg): how lines were called, by season, as stacked counts of rows.
- [`charts/grand-slams-timeline.svg`](charts/grand-slams-timeline.svg): the four Grand Slams, season by season.

Both are drawn from `data/line_calling.csv` by `scripts/teaching_charts.py`. Rerun it after any change to the data:

```
uvx --with matplotlib python scripts/teaching_charts.py
```

## Questions for the by-season chart

1. **What does one row count?** One event, in one season, for one tour. A combined Grand Slam is one row. An event with separate men's and women's draws can be two.
2. **Why is 2025 taller than 2024?** The file adds ATP 500 events from 2025, because the ATP's tour-wide statements cover those two seasons. The bars before and after 2025 count different sets of events.
3. **Can you compare the share of events with electronic calling across seasons?** Only with care. Ask students to drop the rows marked not known first. Among known rows, about 4% called every line electronically in 2019, about 62% in 2024 and about 97% in 2025. Then ask what changes if the not known rows all turned out one way or the other.
4. **Why is 2020 so short?** Many events were cancelled that season, and the file has no row for an event that was not held.

## Questions for the Grand Slam timeline

1. Which Grand Slam moved to electronic calling first, and in which season?
2. The US Open in 2020 is the only cell of its kind. What happened that season? (Read the row's note and source.)
3. Roland Garros never had a challenge system. On clay the ball leaves a mark the umpire can inspect. How might that change the case for electronic review? (The Madrid rows in the CSV show a dispute over a ball mark.)
4. Find the cell marked not held. Why is it blank, and why is that different from not known?

## For the teacher

- Every row with a known value links the page that supports it, so a student can check any single cell.
- The `confidence` column separates confirmed rows from inferred ones. A good extension exercise is to redraw the by-season chart with confirmed rows only.
- The data and the charts are CC BY 4.0. Credit "Live Tennis API" and link [livetennisapi.com](https://livetennisapi.com). The [README](../README.md#how-to-cite) gives the full citation.
- For a coding course, the [tennis API exercises](https://livetennisapi.com/teach) pair well with this pack.
