"""Draw the teaching chart pack from data/line_calling.csv.

Writes teaching/charts/*.svg and *.png at 16:9, sized for a slide. Run it after any change
to the data so the charts never disagree with the file:

    uvx --with matplotlib python scripts/teaching_charts.py
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "line_calling.csv"
OUT = ROOT / "teaching" / "charts"

# One hue, light to dark, for the ordered states from human calls to fully electronic.
# The ramp was checked as an ordinal palette: monotone lightness, visible gaps, and a light
# end that still clears the surface. Unknown is a neutral gray with a hatch, so it never
# depends on colour alone.
STATES = [
    ("line_judges", "Line judges only", "#86b6ef"),
    ("challenge_system", "Line judges with a challenge system", "#3987e5"),
    ("elc_some_courts", "Electronic calling on some courts", "#1c5cab"),
    ("elc_all_courts", "Electronic calling on every court", "#0d366b"),
]
UNKNOWN = ("unknown", "Not known", "#d6d4cf")
SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
SLAMS = ["Australian Open", "Roland Garros", "Wimbledon", "US Open"]


def rows() -> list[dict[str, str]]:
    with DATA.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def style(ax) -> None:
    ax.set_facecolor(SURFACE)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    ax.tick_params(colors=MUTED, labelsize=11, length=0)


def save(fig, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.svg", facecolor=SURFACE, metadata={"Date": None})
    fig.savefig(OUT / f"{name}.png", facecolor=SURFACE, dpi=150)
    plt.close(fig)


def by_season(data: list[dict[str, str]]) -> None:
    seasons = sorted({r["season"] for r in data})
    counts = {s: Counter(r["line_calling"] for r in data if r["season"] == s) for s in seasons}
    fig, ax = plt.subplots(figsize=(12.8, 7.2), facecolor=SURFACE)
    style(ax)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    bottoms = [0] * len(seasons)
    for key, label, colour in STATES + [UNKNOWN]:
        values = [counts[s].get(key, 0) for s in seasons]
        ax.bar(seasons, values, bottom=bottoms, color=colour, width=0.62, label=label,
               edgecolor=SURFACE, linewidth=2, hatch="///" if key == "unknown" else None)
        bottoms = [b + v for b, v in zip(bottoms, values)]
    for x, total in zip(seasons, bottoms):
        ax.text(x, total + 0.8, str(total), ha="center", va="bottom", color=INK2, fontsize=11)
    ax.set_ylabel("Rows (one event, season and tour each)", color=INK2, fontsize=11)
    ax.set_ylim(0, max(bottoms) * 1.15)
    fig.suptitle("How lines were called at top professional events, by season", x=0.06, ha="left",
                 color=INK, fontsize=17, fontweight="bold", y=0.96)
    fig.text(0.06, 0.885, "From 2025 the file also covers ATP 500 events, so the bars before and "
             "after 2025 count different sets of events.", color=INK2, fontsize=11.5)
    ax.legend(loc="upper left", frameon=False, fontsize=10.5, labelcolor=INK2, ncol=2)
    fig.text(0.06, 0.025, "Data: Electronic line calling in professional tennis, by tournament and "
             "season. Live Tennis API, CC BY 4.0.", color=MUTED, fontsize=9.5)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.84, bottom=0.1)
    save(fig, "line-calling-by-season")


def slam_timeline(data: list[dict[str, str]]) -> None:
    seasons = sorted({r["season"] for r in data})
    state = {(r["event"], r["season"]): r["line_calling"] for r in data if r["tour"] == "combined"}
    colours = {k: c for k, _, c in STATES + [UNKNOWN]}
    fig, ax = plt.subplots(figsize=(12.8, 7.2), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    ax.set_xlim(-0.5, len(seasons) - 0.5)
    ax.set_ylim(len(SLAMS) - 0.5, -0.5)
    for y, event in enumerate(SLAMS):
        for x, season in enumerate(seasons):
            key = state.get((event, season))
            if key is None:
                ax.text(x, y, "not held", ha="center", va="center", color=MUTED, fontsize=9.5)
                continue
            ax.add_patch(Rectangle((x - 0.47, y - 0.42), 0.94, 0.84, facecolor=colours[key],
                                   edgecolor=SURFACE, linewidth=2,
                                   hatch="///" if key == "unknown" else None))
    ax.set_xticks(range(len(seasons)), seasons)
    ax.set_yticks(range(len(SLAMS)), SLAMS)
    ax.tick_params(colors=INK2, labelsize=11.5, length=0)
    for side in ax.spines.values():
        side.set_visible(False)
    fig.suptitle("The four Grand Slams, 2017 to 2026", x=0.06, ha="left", color=INK, fontsize=17,
                 fontweight="bold", y=0.96)
    fig.text(0.06, 0.885, "Roland Garros is the one Grand Slam that still uses line judges.",
             color=INK2, fontsize=11.5)
    handles = [Patch(facecolor=c, edgecolor=SURFACE, label=l) for k, l, c in STATES if k != "elc_some_courts"]
    handles.insert(2, Patch(facecolor=colours["elc_some_courts"], edgecolor=SURFACE,
                            label="Electronic calling on some courts"))
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.08), frameon=False,
              fontsize=10.5, labelcolor=INK2, ncol=2)
    fig.text(0.06, 0.025, "Data: Electronic line calling in professional tennis, by tournament and "
             "season. Live Tennis API, CC BY 4.0.", color=MUTED, fontsize=9.5)
    fig.subplots_adjust(left=0.15, right=0.97, top=0.84, bottom=0.24)
    save(fig, "grand-slams-timeline")


if __name__ == "__main__":
    plt.rcParams["svg.hashsalt"] = "line-calling"
    plt.rcParams["font.family"] = "DejaVu Sans"
    data = rows()
    by_season(data)
    slam_timeline(data)
    print(f"wrote {sorted(p.name for p in OUT.iterdir())}")
