# Templates

Source templates used by `statslab new-notebook` and `statslab new-report`.

## Notebook templates (`notebooks/`)

Each is a runnable `.ipynb` with a `parameters`-tagged cell that the CLI
rewrites before saving the scaffolded notebook into `reports/`.

| Template | CLI |
| --- | --- |
| `batter-profile.ipynb` | `statslab new-notebook batter-profile --player "Aaron Judge"` |
| `pitcher-profile.ipynb` | `statslab new-notebook pitcher-profile --player "Logan Gilbert"` |
| `team-season-snapshot.ipynb` | `statslab new-notebook team-season-snapshot --team SEA` |
| `series-matchup.ipynb` | `statslab new-notebook series-matchup --team-a SEA --team-b LAD` |

If you edit a template by hand in JupyterLab, make sure the parameters cell
still has the `parameters` tag (Property Inspector → Common Tools → Add Tag).
Or regenerate everything from the canonical script:

```sh
uv run python scripts/generate_notebook_templates.py
```

## PDF templates (`pdf/`)

Jinja2 HTML with a shared `_base.html.j2`, `_macros.html.j2`, and `_styles.css`.
Templates are looked up by name; the CLI's `new-report <name>` resolves to
`pdf/<name>.html.j2`.

Stat-formatting filters (`avg`, `pct`, `int`, `mph`, `team_color`) are
registered in `mlb_stats_lab.reports.engine`.
