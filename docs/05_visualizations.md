# 05 — Visualizations

## Purpose

Catalog of every chart the project ships. Each entry defines purpose, input shape, signature, Statcast columns it reads, what it renders, and which template/notebook contexts use it. A downstream agent should be able to implement each chart purely from its entry here.

Stack: **matplotlib + seaborn** (per `02_tech_stack.md`). No Plotly. PDF-friendly static output.

---

## Conventions

### Return Type
Every chart function returns a single `matplotlib.figure.Figure`.

- No `plt.show()` inside. Caller decides display vs save.
- No global state mutation. Use `fig, ax = plt.subplots(...)` per call.
- Multi-panel charts return one Figure with multiple Axes. Caller can reach panels via `fig.axes[i]`.

### Style
- `theme.apply()` called once at import of `mlb_stats_lab.viz` sets:
  - `seaborn.set_theme(style="white", context="notebook")`
  - rcParams: font (sans), title weight, grid alpha, default figsize.
- Each chart can override its figsize via a `figsize` kwarg (defaults documented per chart).
- Title pattern: short title (auto-generated from inputs where possible) + optional subtitle via `subtitle` kwarg.

### Color System (defined in `theme.py`)

| Palette                | Purpose                                          |
| ---------------------- | ------------------------------------------------ |
| `TEAM_COLORS[abbrev]`  | dict `{"primary": "#003831", "secondary": ...}`. Used for team-identified charts. |
| `PITCH_COLORS[code]`   | Semantic pitch-type colors (FF=red, SI=orange, FC=brown, SL=yellow, CU=blue, KC=indigo, CH=green, FS=teal, FO=grey). |
| `OUTCOME_COLORS`       | HR=#d62728, 3B=#ff7f0e, 2B=#bcbd22, 1B=#2ca02c, BB=#1f77b4, K=#7f7f7f, out=#cccccc. |
| `NEUTRAL`              | Project default (deep blue + grey) for non-team, non-pitch charts. |

Each chart's docstring says which palette it pulls from.

### Save Helpers (`viz/save.py`)

```python
def fig_to_png(fig: Figure, path: str | Path, dpi: int = 200) -> Path:
    """Save figure as PNG. Returns path. Closes the figure."""

def fig_to_svg(fig: Figure, path: str | Path) -> Path:
    """Save figure as SVG (vector). Returns path. Closes the figure."""

def fig_to_bytes(fig: Figure, fmt: Literal["png", "svg"] = "png", dpi: int = 200) -> bytes:
    """In-memory render. Used by report pipeline for embedding."""
```

PDF report pipeline (`07_pdf_reports.md`) uses `fig_to_png` (or `fig_to_bytes`) to embed charts into Jinja HTML.

### Default Figsize
| Chart family          | figsize (inches) |
| --------------------- | ---------------- |
| Spray chart           | (7, 7) square    |
| Zone heatmap / grid   | (5, 6)           |
| Pitch location scatter| (5, 6)           |
| Movement / arsenal    | (7, 6)           |
| Velocity dist         | (8, 4)           |
| Pitch usage bar       | (6, 4)           |
| Pitch usage pie       | (5, 5)           |
| Rolling line          | (10, 4)          |
| Splits bar            | (8, 5)           |
| EV vs LA scatter      | (7, 5)           |
| Box / dist            | (8, 5)           |

---

## Module Surface

```
src/mlb_stats_lab/viz/
├── __init__.py        # re-exports public chart fns; calls theme.apply()
├── theme.py           # palettes, rcParams, apply()
├── field.py           # _draw_field_overlay(ax) — private
├── zone.py            # _draw_zone_overlay(ax) — private
├── spray.py           # spray_chart
├── heatmap.py         # zone_heatmap (KDE), zone_grid (binned)
├── scatter.py         # pitch_location_scatter, ev_la_scatter
├── arsenal.py         # pitch_movement_chart, velocity_distribution
├── usage.py           # pitch_usage_bar, pitch_usage_pie
├── rolling.py         # rolling_metric_line
├── splits.py          # splits_bar_chart
├── distributions.py   # ev_distribution, la_distribution, velocity_box
└── save.py            # fig_to_png, fig_to_svg, fig_to_bytes
```

Public re-exports from `viz/__init__.py`: every chart function above + the three save helpers.

---

## Chart Catalog

For each chart: **Purpose**, **Input**, **Signature**, **Columns Read**, **What It Renders**, **Used By**.

---

### `spray_chart`

**Purpose**: Show where a hitter (or team) puts the ball in play on the field.

**Input**: Statcast DataFrame filtered to a batter (or team's hitters), with batted-ball events only. The helper internally calls `filters.only_in_play(df)` to be safe.

**Signature**:
```python
def spray_chart(
    df: pd.DataFrame,
    *,
    title: str | None = None,
    show_outs: bool = True,
    team_color: str | None = None,    # 3-letter abbrev for theme accent
    figsize: tuple[float, float] = (7, 7),
) -> Figure: ...
```

**Columns Read**: `hc_x`, `hc_y`, `events`, `bb_type`, `launch_speed`, `launch_angle`

**What It Renders**:
- Baseball field overlay (foul lines, bases, outfield arc) drawn by `_draw_field_overlay(ax)`.
- Scatter of batted-ball landing locations from `hc_x` / `hc_y` (coordinate transform: `x = hc_x − 125`, `y = 200 − hc_y` — standard Statcast spray transform).
- Marker color by outcome: `OUTCOME_COLORS` map. Outs in grey if `show_outs=True`, hidden otherwise.
- Marker size proportional to `launch_speed` (clamped 30–150).
- Legend with outcome counts.

**Used By**: Batter Profile template, Series Matchup template (team-aggregated).

---

### `zone_heatmap` (KDE)

**Purpose**: Smooth density heatmap of pitch locations, or batted-ball/swing locations, in/around the strike zone — batter's perspective by default.

**Input**: Statcast DataFrame with pitch-level rows containing `plate_x`, `plate_z`.

**Signature**:
```python
def zone_heatmap(
    df: pd.DataFrame,
    *,
    metric: Literal["density", "whiff_rate", "swing_rate", "xwoba"] = "density",
    perspective: Literal["batter", "pitcher"] = "batter",
    title: str | None = None,
    figsize: tuple[float, float] = (5, 6),
) -> Figure: ...
```

**Columns Read**: `plate_x`, `plate_z`, plus the columns needed for the chosen `metric`:
- `density` → none extra
- `whiff_rate` → `description`
- `swing_rate` → `description`
- `xwoba` → `estimated_woba_using_speedangle`

**What It Renders**:
- Strike zone outline rectangle (from `sz_top`/`sz_bot` averages, fixed `±0.83 ft` horizontal) drawn by `_draw_zone_overlay(ax)`.
- KDE contour fill (seaborn `kdeplot`) of pitch positions, or a heatmap of the chosen metric on a 2D grid.
- For `metric="density"`: viridis colormap.
- For metric-weighted variants: RdYlBu_r (diverging, red = hot).
- Horizontal limits ±2 ft, vertical 0.5–4.5 ft.

**Used By**: Batter Profile (locations seen), Pitcher Profile (locations thrown), Series Matchup (key matchup vs LHP/RHP).

---

### `zone_grid`

**Purpose**: Discrete-bin version of zone heatmap. Each cell labeled with the metric value (e.g. xwOBA in zone 5 = .412).

**Input**: Same as `zone_heatmap`.

**Signature**:
```python
def zone_grid(
    df: pd.DataFrame,
    *,
    metric: Literal["count", "whiff_rate", "swing_rate", "avg", "xwoba"] = "count",
    bins: Literal[3, 5] = 3,    # 3x3 (standard zone) or 5x5 (finer)
    perspective: Literal["batter", "pitcher"] = "batter",
    title: str | None = None,
    figsize: tuple[float, float] = (5, 6),
) -> Figure: ...
```

**Columns Read**: `plate_x`, `plate_z`, plus those required by `metric`.

**What It Renders**:
- 3×3 (or 5×5) grid cells covering the strike zone and one shell of "chase zones" outside.
- Cell fill color from metric value, cell label = formatted number ("0.412", "47%").
- Strike zone rectangle overlay on top.

**Used By**: Pitcher Profile (whiff% by zone), Batter Profile (xwOBA by zone).

---

### `pitch_location_scatter`

**Purpose**: Individual pitches plotted in the zone, colored by `pitch_type` or `description`.

**Input**: Pitch-level Statcast DataFrame.

**Signature**:
```python
def pitch_location_scatter(
    df: pd.DataFrame,
    *,
    color_by: Literal["pitch_type", "description", "result"] = "pitch_type",
    perspective: Literal["batter", "pitcher"] = "batter",
    title: str | None = None,
    figsize: tuple[float, float] = (5, 6),
) -> Figure: ...
```

**Columns Read**: `plate_x`, `plate_z`, plus the `color_by` column.

**What It Renders**:
- Strike zone overlay.
- Scatter of each pitch as a circle.
- Color: `PITCH_COLORS` for `pitch_type`, `OUTCOME_COLORS` for `result`, semantic palette for `description`.
- Legend with counts per category.

**Used By**: Pitcher Profile, Game Recap (deferred), Series Matchup spotlight ABs.

---

### `pitch_movement_chart`

**Purpose**: Pitcher's arsenal in horizontal vs vertical break space — one cluster per pitch type.

**Input**: Pitch-level Statcast DataFrame filtered to one pitcher (or aggregated across).

**Signature**:
```python
def pitch_movement_chart(
    df: pd.DataFrame,
    *,
    title: str | None = None,
    figsize: tuple[float, float] = (7, 6),
) -> Figure: ...
```

**Columns Read**: `pfx_x`, `pfx_z`, `pitch_type`, `release_speed`.

**What It Renders**:
- X axis: `pfx_x` (inches, with sign flipped per perspective convention)
- Y axis: `pfx_z` (inches)
- Scatter colored by `pitch_type` (PITCH_COLORS).
- Each cluster annotated with the pitch's mean velocity ("FF 96.2 mph").
- Zero-zero gridlines, equal aspect ratio.

**Used By**: Pitcher Profile.

---

### `velocity_distribution`

**Purpose**: Show velocity range per pitch type (consistency, top end).

**Input**: Pitch-level Statcast DataFrame.

**Signature**:
```python
def velocity_distribution(
    df: pd.DataFrame,
    *,
    kind: Literal["kde", "violin", "box"] = "kde",
    title: str | None = None,
    figsize: tuple[float, float] = (8, 4),
) -> Figure: ...
```

**Columns Read**: `release_speed`, `pitch_type`.

**What It Renders**:
- One distribution per pitch type, colored by `PITCH_COLORS`.
- KDE overlapped, violin side-by-side, or box plot — caller picks.
- X axis: mph. Legend with mean velocity per pitch type.

**Used By**: Pitcher Profile, Series Matchup (starter arsenal compare).

---

### `pitch_usage_bar`

**Purpose**: Pitcher's pitch mix as a horizontal bar.

**Input**: Pitch-level DataFrame.

**Signature**:
```python
def pitch_usage_bar(
    df: pd.DataFrame,
    *,
    by: Literal["overall", "vs_hand", "count_state"] = "overall",
    title: str | None = None,
    figsize: tuple[float, float] = (6, 4),
) -> Figure: ...
```

**Columns Read**: `pitch_type`, plus `stand` (vs_hand) or balls/strikes (count_state).

**What It Renders**:
- Horizontal bars, one per pitch type, length = usage %.
- Bars colored by `PITCH_COLORS`. Labels = "%" and raw counts.
- For `by="vs_hand"`: grouped bars (vs LHB and vs RHB side by side).
- For `by="count_state"`: grouped by ahead/even/behind.

**Used By**: Pitcher Profile, Series Matchup.

---

### `pitch_usage_pie`

**Purpose**: Same as `pitch_usage_bar` but pie. Use when overall mix is the only message.

**Input**: Pitch-level DataFrame.

**Signature**:
```python
def pitch_usage_pie(
    df: pd.DataFrame,
    *,
    title: str | None = None,
    figsize: tuple[float, float] = (5, 5),
) -> Figure: ...
```

**Columns Read**: `pitch_type`.

**What It Renders**: Donut chart (inner radius 0.5), wedges colored by `PITCH_COLORS`, % labels on slices.

**Used By**: Pitcher Profile (compact view).

---

### `ev_la_scatter`

**Purpose**: Launch-angle vs exit-velocity profile of batted balls.

**Input**: In-play DataFrame.

**Signature**:
```python
def ev_la_scatter(
    df: pd.DataFrame,
    *,
    overlay_barrel_zone: bool = True,
    color_by: Literal["outcome", "bb_type", "none"] = "outcome",
    title: str | None = None,
    figsize: tuple[float, float] = (7, 5),
) -> Figure: ...
```

**Columns Read**: `launch_speed`, `launch_angle`, `events`, `bb_type`.

**What It Renders**:
- Scatter: X = `launch_angle`, Y = `launch_speed`.
- Optional shaded "barrel zone" overlay (the Statcast barrel definition's LA × EV envelope).
- Color by outcome (HR red, hits orange/green, outs grey) or by `bb_type`.

**Used By**: Batter Profile, Series Matchup (team batted-ball quality).

---

### `rolling_metric_line`

**Purpose**: Rolling-window trend over time — e.g. rolling AVG over PAs, rolling K% over BFs.

**Input**: DataFrame output of `batting.rolling_batting_line` or `pitching.rolling_pitching_line`, OR raw Statcast df + metric spec.

**Signature**:
```python
def rolling_metric_line(
    series_or_df: pd.Series | pd.DataFrame,
    *,
    metric: str | None = None,        # column name when input is DataFrame
    title: str | None = None,
    league_average: float | None = None,  # horizontal reference line
    figsize: tuple[float, float] = (10, 4),
) -> Figure: ...
```

**Columns Read**: Whatever metric column the caller picks.

**What It Renders**:
- Line plot, X = window anchor (PA #, game #, date), Y = metric.
- Optional dashed horizontal `league_average` line.
- Shaded ±1 SD band if input includes a `std` column.

**Used By**: Batter Profile (rolling AVG/wOBA), Pitcher Profile (rolling K%, ERA proxy), Team Season Snapshot (team rolling run differential).

---

### `splits_bar_chart`

**Purpose**: Compare a metric across split buckets (e.g. AVG vs LHP vs RHP, home vs away, by month).

**Input**: DataFrame from `batting.splits(df, axis=...)` or `pitching.splits(df, axis=...)`.

**Signature**:
```python
def splits_bar_chart(
    splits_df: pd.DataFrame,
    metric: str,                       # column to plot from splits_df
    *,
    title: str | None = None,
    sort: Literal["index", "value"] = "index",
    figsize: tuple[float, float] = (8, 5),
) -> Figure: ...
```

**Columns Read**: The chosen `metric` column from a `splits()` output.

**What It Renders**:
- Vertical bars, one per split bucket.
- Bar height = metric.
- Sample-size label above each bar (PA or BF from the splits row).
- Horizontal reference line at the player's overall metric.

**Used By**: Batter Profile (splits panel), Pitcher Profile (splits panel), Series Matchup.

---

### `ev_distribution`, `la_distribution`, `velocity_box`

**Purpose**: Single-metric distributions — exit velocity, launch angle, velocity by pitch type. Smaller utility charts for filling out template space.

**Signatures**:
```python
def ev_distribution(df, *, by: str | None = None, ...) -> Figure: ...
def la_distribution(df, *, by: str | None = None, ...) -> Figure: ...
def velocity_box(df, *, by: str = "pitch_type", ...) -> Figure: ...
```

**Columns Read**: `launch_speed`, `launch_angle`, `release_speed`, plus the `by` column.

**Used By**: optional panels in any template.

---

## Style Reference

### Team Colors

`viz/theme.py` ships a `TEAM_COLORS` dict keyed by 3-letter abbreviation. Each value:

```python
{
    "primary":   "#003831",   # main team color
    "secondary": "#EFB21E",   # secondary
    "text_on_primary": "#FFFFFF",  # readable foreground
}
```

All 30 teams pre-populated using each franchise's official colors. Updated manually when a team rebrands.

Sample (for reference):

| Abbrev | Primary   | Secondary |
| ------ | --------- | --------- |
| SEA    | #0C2C56   | #005C5C   |
| LAD    | #005A9C   | #EF3E42   |
| NYY    | #003087   | #E4002C   |
| ATH    | #003831   | #EFB21E   |
| BOS    | #BD3039   | #0C2340   |

Full table embedded in `theme.py` as a constant.

### Pitch Colors

```python
PITCH_COLORS = {
    "FF": "#d62728",  # 4-seam fastball — red
    "SI": "#ff7f0e",  # sinker — orange
    "FC": "#8c564b",  # cutter — brown
    "SL": "#f7c948",  # slider — yellow
    "ST": "#bcbd22",  # sweeper — olive
    "CU": "#1f77b4",  # curveball — blue
    "KC": "#5e2ca5",  # knuckle curve — indigo
    "CH": "#2ca02c",  # changeup — green
    "FS": "#17becf",  # splitter — teal
    "FO": "#7f7f7f",  # forkball — grey
    "KN": "#e377c2",  # knuckleball — pink
}
```

Unknown pitch types fall back to `#cccccc`.

### Outcome Colors

```python
OUTCOME_COLORS = {
    "home_run":      "#d62728",
    "triple":        "#ff7f0e",
    "double":        "#bcbd22",
    "single":        "#2ca02c",
    "walk":          "#1f77b4",
    "hit_by_pitch":  "#9467bd",
    "strikeout":     "#7f7f7f",
    "field_out":     "#cccccc",
    "grounded_into_double_play": "#999999",
}
```

Defaults to grey for any other outcome.

---

## What Each Template Pulls (Preview)

Full mapping in `06_notebook_templates.md`. Quick preview:

| Template              | Charts                                                                  |
| --------------------- | ----------------------------------------------------------------------- |
| Batter Profile        | spray_chart, zone_heatmap, ev_la_scatter, splits_bar_chart, rolling_metric_line |
| Pitcher Profile       | pitch_movement_chart, velocity_distribution, pitch_usage_bar, zone_grid, splits_bar_chart |
| Series Matchup        | spray_chart (team), pitch_usage_bar (starters), splits_bar_chart, rolling_metric_line (form) |
| Team Season Snapshot  | rolling_metric_line (run diff), pitch_usage_bar (staff aggregate), splits_bar_chart |

---

## Implementation Notes

### Spray Coordinate Transform

Statcast `hc_x` / `hc_y` are in a 250×250 pixel-style coordinate space where home plate is at roughly (125, 200) and the outfield extends upward (decreasing `y`). Standard transform for drawing:

```python
x = df["hc_x"] - 125.0       # center on home plate
y = 200.0 - df["hc_y"]       # flip so outfield is +y
```

Applied inside `spray_chart` only — every other function uses native coords.

### Strike Zone Coordinates

- Horizontal: `plate_x` in feet, zero = center of plate. Plate is ±0.708 ft. Use ±0.83 ft for "edges" tolerance.
- Vertical: `plate_z` in feet from ground. Zone top/bottom vary per batter — use `sz_top` and `sz_bot` means for the player when available, else fixed (1.5, 3.5) ft.
- `_draw_zone_overlay(ax)` draws the rectangle. Outer "chase zone" optionally drawn as dashed rectangle ±0.5 ft beyond zone.

### Perspective Flip

For pitcher view, plate appears from the catcher's POV (right-handed batter on the left side, `plate_x > 0` = arm side for RHP). For batter view, mirror: `plate_x` is flipped so the batter's "inside" pitches appear on the inside of the plot regardless of handedness. Handled by an internal helper `_flip_for_perspective(df, perspective, stand_or_throws)`.

### Theme Application

`viz/__init__.py` calls `theme.apply()` at import time (idempotent). Apply does:

```python
import matplotlib as mpl
import seaborn as sns

def apply() -> None:
    sns.set_theme(style="white", context="notebook")
    mpl.rcParams.update({
        "figure.dpi": 100,
        "savefig.dpi": 200,
        "font.family": "sans-serif",
        "axes.titleweight": "bold",
        "axes.titlesize": 13,
        "axes.labelsize": 11,
        "axes.grid": True,
        "grid.alpha": 0.2,
        "legend.frameon": False,
    })
```

---

## Decision Log

| Decision                                          | Rationale                                                |
| ------------------------------------------------- | -------------------------------------------------------- |
| matplotlib + seaborn only                         | PDF-friendly, per `02_tech_stack.md`                     |
| Return `Figure` (not `(Figure, Axes)`)            | Consistent signatures, customization still possible      |
| All-batted-balls spray (color by outcome)         | More information per chart, outs visible in grey         |
| Split heatmap: KDE + grid as separate fns         | Different use cases, clearer call site                   |
| Team colors registry                              | Identity in reports, worth the maintenance               |
| Pitch-type semantic palette                       | Reader recognizes pitch by color across multiple charts  |
| `theme.apply()` on import                         | Consistent look without per-call setup                   |
| Save helpers in same module                       | viz module owns its own rendering-to-disk                |

---

## Open Items For Later Docs

- Exact `_draw_field_overlay` proportions (foul line angle, outfield arc radius) → implementation detail
- Game Recap template + pitch-by-pitch sequence chart → deferred per `06_notebook_templates.md`
- League-average values for `rolling_metric_line` reference lines — sourced from `data.season` or hardcoded constants? → resolve in implementation
- Whether to add team logos (PNG) to template cover pages → out of v1 (extra asset pipeline)
