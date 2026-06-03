# 07 — PDF Reports

> **Update (look & feel overhaul).** Reports now share one color story:
> `mlb_stats_lab.viz.theme.report_theme(team)` returns design tokens (primary /
> secondary / text / soft / mid). `reports.engine.render_html` injects them into
> every template as CSS custom properties (`--accent`, `--accent-2`, …) on `:root`
> in `_base.html.j2`. `_styles.css` consumes those variables, so the team-colored
> cover band, grid stat cards, and themed tables all theme from one source.
> Chart figures are tinted to match via `report_chart_context(accent)` wrapped
> around figure generation in `reports/context.py` (titles/spines pick up the team
> color; data-series colors are untouched). See the WeasyPrint native-library note
> in the README for Apple Silicon setup.

## Purpose

Defines how a notebook's analytical output gets rendered to a polished PDF report. Stack: **Jinja2 HTML templates → WeasyPrint → PDF** (per `02_tech_stack.md`).

PDFs are the deliverable artifact for the user. Notebooks are the interactive workspace; reports are what gets exported.

---

## Approach (Why Not nbconvert)

We deliberately **do not** use `nbconvert --to pdf`. Reasons:
- Layout control: nbconvert dumps notebook output cells linearly; reports need controlled page breaks, headers, footers.
- Asset reuse: same chart helpers feed both notebook display and PDF, but PDFs deserve report-grade typography and structure.
- Polishing: HTML/CSS is the right tool for print layout. WeasyPrint renders HTML/CSS into PDF with full CSS Paged Media support.

The flow is **explicit, data-driven**: a notebook (or any caller) builds a context dict and calls `render_report(template, context, out_path)`. Charts are rendered to PNG bytes and embedded.

```
notebook code  →  context dict + chart bytes
                          ↓
              reports.render_report(...)
                          ↓
          Jinja2 renders HTML from .html.j2 template
                          ↓
              WeasyPrint renders HTML → PDF
                          ↓
            reports/output/<name>.pdf
```

---

## Module Surface (`src/mlb_stats_lab/reports/`)

```
src/mlb_stats_lab/reports/
├── __init__.py
├── engine.py          # Jinja env, render_report, render_html
├── pdf.py             # html_to_pdf via WeasyPrint
├── assets.py          # fig_to_data_uri, embed_image helpers
├── context.py         # ReportContext dataclass + builders per template
├── summary.py         # shared auto-bullet logic (referenced from doc 06)
└── filters.py         # custom Jinja filters (format_pct, format_avg, ...)
```

### Public API

```python
def render_report(
    template: str,
    context: dict | ReportContext,
    output_path: str | Path,
    *,
    open_after: bool = False,
) -> Path:
    """Render a Jinja template with context, run WeasyPrint, write PDF.

    Args:
        template: template name without extension. Looked up in
            reports/templates/pdf/. e.g. "batter-profile".
        context: dict (or ReportContext) consumed by the template.
        output_path: PDF destination. If relative, resolved under
            config.output_dir.
        open_after: if True, opens the PDF in the system viewer.

    Returns:
        Path to the rendered PDF.
    """

def render_html(template: str, context: dict | ReportContext) -> str:
    """Render the template to HTML only (no PDF). Useful for debugging styling."""

def list_pdf_templates() -> list[str]:
    """Names of available PDF templates under reports/templates/pdf/."""
```

### `assets.py` — Chart Embedding

```python
def fig_to_data_uri(fig: Figure, fmt: Literal["png", "svg"] = "png", dpi: int = 200) -> str:
    """Render a matplotlib Figure to a base64 data URI suitable for
    direct <img src="..."> embedding in HTML. Closes the figure."""

def figs_to_context(**figs: Figure) -> dict[str, str]:
    """Convenience: convert a dict of name → Figure into name → data URI."""
```

Data URIs avoid temp files and let the PDF be a single self-contained render.

### `filters.py` — Jinja Custom Filters

| Filter         | Example use                            | Effect                                |
| -------------- | -------------------------------------- | ------------------------------------- |
| `avg`          | `{{ line.AVG \| avg }}`                | `.288` (3 decimals, no leading zero)  |
| `pct`          | `{{ line.K_pct \| pct }}`              | `22.4%`                               |
| `signed_pct`   | `{{ diff \| signed_pct }}`             | `+3.2%` / `-1.4%`                     |
| `int`          | `{{ line.PA \| int }}`                 | `231`                                 |
| `mph`          | `{{ velo \| mph }}`                    | `94.7 mph`                            |
| `team_color`   | `{{ team \| team_color("primary") }}`  | `#0C2C56`                             |

Registered in `engine.py`'s Jinja Environment.

---

## Template Directory Layout

```
reports/templates/pdf/
├── _base.html.j2           # shared layout: <html>, page CSS, header/footer
├── _macros.html.j2         # reusable Jinja macros (stat_card, chart_block)
├── _styles.css             # base print stylesheet
├── batter-profile.html.j2
├── pitcher-profile.html.j2
├── series-matchup.html.j2
└── team-season-snapshot.html.j2
```

One `.html.j2` per template. Inheritance via `{% extends "_base.html.j2" %}`. Shared CSS at `_styles.css`, referenced from `_base.html.j2`.

Each PDF template name **matches** the notebook template name (kebab-case). The CLI's `new-report <name>` looks up both.

---

## Base Layout — `_base.html.j2`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{% block title %}{{ report_title }}{% endblock %}</title>
  <link rel="stylesheet" href="_styles.css">
  <style>
    @page {
      size: Letter;
      margin: 0.6in 0.6in 0.8in 0.6in;
      @bottom-left { content: "{{ report_title }}"; font-size: 8pt; color: #888; }
      @bottom-right { content: "Page " counter(page) " of " counter(pages); font-size: 8pt; color: #888; }
    }
    {% block extra_styles %}{% endblock %}
  </style>
</head>
<body>
  <header class="cover">
    <h1>{{ report_title }}</h1>
    <p class="subtitle">{{ report_subtitle }}</p>
    <p class="meta">{{ generated_at }}</p>
  </header>

  {% block body %}{% endblock %}

  <footer class="endnote">
    <p>Generated by MLB Stats Lab • Data via Statcast / pybaseball</p>
  </footer>
</body>
</html>
```

---

## Shared Macros — `_macros.html.j2`

```jinja
{% macro stat_card(label, value, accent="#003831") %}
<div class="stat-card" style="border-left: 4px solid {{ accent }};">
  <div class="stat-label">{{ label }}</div>
  <div class="stat-value">{{ value }}</div>
</div>
{% endmacro %}

{% macro chart_block(title, data_uri, caption=None) %}
<figure class="chart">
  <h3>{{ title }}</h3>
  <img src="{{ data_uri }}" alt="{{ title }}">
  {% if caption %}<figcaption>{{ caption }}</figcaption>{% endif %}
</figure>
{% endmacro %}

{% macro bullet_list(items) %}
<ul class="takeaways">
  {% for item in items %}<li>{{ item }}</li>{% endfor %}
</ul>
{% endmacro %}
```

---

## Base Stylesheet — `_styles.css`

Project styling baseline. Hand-curated; tweak per template via `extra_styles` block.

```css
/* Typography */
body {
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  color: #222;
  line-height: 1.4;
  font-size: 10.5pt;
}
h1 { font-size: 22pt; margin: 0 0 0.1in 0; }
h2 { font-size: 14pt; border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-top: 0.3in; }
h3 { font-size: 11pt; margin: 0.15in 0 0.05in 0; }

/* Cover */
.cover { text-align: left; margin-bottom: 0.4in; }
.cover .subtitle { color: #555; font-size: 12pt; margin: 0; }
.cover .meta { color: #888; font-size: 9pt; margin-top: 4px; }

/* Stat cards */
.stat-card {
  display: inline-block;
  padding: 8px 14px;
  margin: 4px;
  background: #f7f7f7;
  border-radius: 3px;
  min-width: 90px;
}
.stat-label { font-size: 8pt; text-transform: uppercase; color: #777; letter-spacing: 0.05em; }
.stat-value { font-size: 14pt; font-weight: 600; }

/* Charts */
.chart { margin: 0.15in 0; page-break-inside: avoid; }
.chart img { width: 100%; max-height: 4.5in; object-fit: contain; }
.chart figcaption { font-size: 8pt; color: #777; text-align: center; }

/* Tables */
table { width: 100%; border-collapse: collapse; margin: 0.1in 0; }
th, td { padding: 4px 8px; text-align: right; }
th { background: #f0f0f0; font-size: 9pt; text-transform: uppercase; }
td:first-child, th:first-child { text-align: left; }
tr:nth-child(even) { background: #fafafa; }

/* Takeaway list */
.takeaways { padding-left: 18px; }
.takeaways li { margin: 4px 0; }

/* Page breaks */
.page-break { page-break-after: always; }
```

---

## Example — `batter-profile.html.j2`

Skeleton showing structure; full template will mirror notebook sections from `06`.

```jinja
{% extends "_base.html.j2" %}
{% import "_macros.html.j2" as m %}

{% block extra_styles %}
  .stat-card { border-left-color: {{ team | team_color("primary") }}; }
{% endblock %}

{% block body %}

<section>
  <h2>Season Line</h2>
  {{ m.stat_card("PA",   line.PA | int) }}
  {{ m.stat_card("AVG",  line.AVG | avg) }}
  {{ m.stat_card("OBP",  line.OBP | avg) }}
  {{ m.stat_card("SLG",  line.SLG | avg) }}
  {{ m.stat_card("wOBA", line.wOBA | avg) }}
  {{ m.stat_card("xwOBA", line.xwOBA | avg) }}
  {{ m.stat_card("BB%",  line["BB%"] | pct) }}
  {{ m.stat_card("K%",   line["K%"] | pct) }}
</section>

<section>
  <h2>Spray</h2>
  {{ m.chart_block("Batted Balls", figs.spray) }}
</section>

<section class="page-break">
  <h2>Zone Profile</h2>
  <div class="row">
    {{ m.chart_block("Pitches Seen", figs.zone_density) }}
    {{ m.chart_block("Swing Rate", figs.zone_swing) }}
  </div>
  {{ m.chart_block("xwOBA by Zone", figs.zone_xwoba) }}
</section>

<section>
  <h2>Contact Profile</h2>
  {{ m.chart_block("EV vs LA", figs.ev_la) }}
</section>

<section class="page-break">
  <h2>Splits</h2>
  {{ m.chart_block("vs Handedness", figs.splits_hand) }}
  {{ m.chart_block("Home / Away",   figs.splits_home_away) }}
  {{ m.chart_block("By Month",      figs.splits_month) }}
</section>

<section>
  <h2>Performance by Pitch Type</h2>
  <table>
    <thead><tr>
      <th>Pitch</th><th>Pitches</th><th>Whiff%</th><th>AVG</th><th>SLG</th><th>xwOBA</th>
    </tr></thead>
    <tbody>
    {% for row in by_pitch %}
      <tr>
        <td>{{ row.pitch_name }}</td>
        <td>{{ row.pitches | int }}</td>
        <td>{{ row["Whiff%"] | pct }}</td>
        <td>{{ row.AVG | avg }}</td>
        <td>{{ row.SLG | avg }}</td>
        <td>{{ row.xwOBA | avg }}</td>
      </tr>
    {% endfor %}
    </tbody>
  </table>
</section>

<section>
  <h2>Recent Form</h2>
  {{ m.chart_block("Rolling wOBA", figs.rolling_woba) }}
</section>

<section>
  <h2>Takeaways</h2>
  {{ m.bullet_list(takeaways) }}
</section>

{% endblock %}
```

---

## Context Shape Per Template

Each template's expected `context` keys are formalized in `reports/context.py` as a TypedDict (or dataclass) so notebooks know what to pass.

### `BatterProfileContext`

```python
@dataclass
class BatterProfileContext:
    # Header
    report_title: str               # "Batter Profile — Aaron Judge"
    report_subtitle: str            # "2026 Season, through May 20"
    generated_at: str               # ISO datetime string
    team: str                       # 3-letter abbrev for theming

    # Numeric blocks
    line: dict                      # batting_line output (Series → dict)
    discipline: dict
    contact: dict
    by_pitch: list[dict]            # performance_by_pitch_type rows

    # Charts (data URIs)
    figs: dict[str, str]            # keys: spray, zone_density, zone_swing, zone_xwoba, ev_la, splits_hand, splits_home_away, splits_month, rolling_woba

    # Narrative
    takeaways: list[str]
```

Similar dataclasses for `PitcherProfileContext`, `SeriesMatchupContext`, `TeamSeasonSnapshotContext` — each defined in `reports/context.py`.

A notebook's final cell builds this context and calls `render_report`:

```python
from mlb_stats_lab.reports import render_report
from mlb_stats_lab.reports.assets import figs_to_context
from mlb_stats_lab.reports.context import BatterProfileContext

ctx = BatterProfileContext(
    report_title=f"Batter Profile — {player}",
    report_subtitle=f"{season} Season, through {end_date}",
    generated_at=datetime.now().isoformat(timespec="seconds"),
    team=team_abbrev,
    line=line.to_dict(),
    discipline=disc.to_dict(),
    contact=contact.to_dict(),
    by_pitch=by_pitch_df.reset_index().to_dict("records"),
    figs=figs_to_context(
        spray=spray_fig,
        zone_density=zone_density_fig,
        zone_swing=zone_swing_fig,
        zone_xwoba=zone_xwoba_fig,
        ev_la=ev_la_fig,
        splits_hand=splits_hand_fig,
        splits_home_away=splits_home_away_fig,
        splits_month=splits_month_fig,
        rolling_woba=rolling_woba_fig,
    ),
    takeaways=takeaways,
)

render_report("batter-profile", ctx, "judge_2026-05-20.pdf")
```

---

## WeasyPrint Config

`pdf.py`:

```python
from weasyprint import HTML, CSS

def html_to_pdf(html_str: str, output_path: Path, base_url: Path | None = None) -> Path:
    """Render HTML string to PDF using WeasyPrint.

    base_url: directory used to resolve relative URLs (CSS, images).
              Defaults to reports/templates/pdf/ so relative <link href>
              and <img src> work without absolute paths.
    """
    HTML(string=html_str, base_url=str(base_url)).write_pdf(target=str(output_path))
    return output_path
```

Notes:
- `base_url` lets the `<link rel="stylesheet" href="_styles.css">` resolve.
- We pass the HTML string (not file path) because Jinja already rendered it.
- Image embedding via data URIs bypasses fetching entirely.

---

## Output Location

Per `01_architecture.md`:
- Generated PDFs → `reports/output/` (configurable via `statslab.toml` `[paths] output_dir`).
- Naming: `<template>__<key-args>__<YYYY-MM-DD>.pdf`.

`render_report` resolves relative `output_path` under `output_dir` from config.

---

## Debugging Styles

For iterating on CSS without paying the full WeasyPrint round-trip:

```python
html = render_html("batter-profile", ctx)
Path("debug.html").write_text(html)
# Open debug.html in a browser
```

Browser rendering ≠ WeasyPrint exactly (browsers ignore `@page`, etc.), but is close enough for first-pass styling.

---

## Performance

- WeasyPrint render time scales with chart count and size. ~10 chart PDF: 2–4s.
- Largest cost is image decoding from base64. Acceptable for v1.
- If perf becomes an issue: switch from PNG data URIs to on-disk PNG references with `base_url=Path(tmp_dir)`.

---

## Decision Log

| Decision                                          | Rationale                                                       |
| ------------------------------------------------- | --------------------------------------------------------------- |
| Jinja2 + WeasyPrint over nbconvert                | Layout control, print-quality typography                        |
| One `.html.j2` per template, shared `_base`       | DRY layout, easy per-template tweaks                            |
| Chart embedding via PNG data URIs                 | Self-contained PDFs, no temp files                              |
| `reports/context.py` dataclasses per template     | Templates know their expected inputs; type safety               |
| Custom Jinja filters (avg, pct, team_color, ...)  | Single source of truth for number formatting                    |
| `render_html` debugging escape hatch              | Fast CSS iteration without PDF round-trip                       |
| Page size Letter w/ 0.6"–0.8" margins             | Standard for personal printing; tweakable in `_base.html.j2`    |
| WeasyPrint `base_url` set to templates/pdf/       | Resolves stylesheet `<link>` correctly                          |

---

## Open Items For Later Docs / Impl

- `summary.py` shared auto-bullet helpers — design alongside template authoring
- Team logo embedding (PNG assets per team) — out of v1
- Optional dark / light theme toggle for printed vs on-screen viewing — defer
- Multi-page TOC for long reports — likely not needed at v1 scale
