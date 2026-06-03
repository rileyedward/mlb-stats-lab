# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#   kernelspec:
#     display_name: MLB Stats Lab
#     language: python
#     name: mlb-stats-lab
# ---

# %% [markdown]
# # Series Matchup
# *Two-team in-depth comparison.*

# %% tags=["parameters"]
team_a = "SEA"
team_b = "LAD"
season = None
start_date = None
end_date = None
recent_form_games = 10

# %% tags=["setup"] jupyter={"source_hidden": true}
import pandas as pd
from IPython.display import Markdown, display

from mlb_stats_lab.batting import batting_line
from mlb_stats_lab.batting.splits import splits as batting_splits
from mlb_stats_lab.data import current_season, get_statcast_for_team, season_range
from mlb_stats_lab.pitching import pitching_line
from mlb_stats_lab.viz import (
    pitch_usage_bar,
    report_header,
    section,
    splits_bar_chart,
    velocity_distribution,
)

season = season or current_season()
if start_date is None or end_date is None:
    s, e = season_range(season)
    start_date = start_date or s
    end_date = end_date or e

display(report_header(f"{team_a} vs {team_b}", f"{season} · {start_date} → {end_date}", team=team_a))

# %% tags=["load"] jupyter={"source_hidden": true}
a_bat = get_statcast_for_team(team_a, start=start_date, end=end_date, side="batting")
a_pit = get_statcast_for_team(team_a, start=start_date, end=end_date, side="pitching")
b_bat = get_statcast_for_team(team_b, start=start_date, end=end_date, side="batting")
b_pit = get_statcast_for_team(team_b, start=start_date, end=end_date, side="pitching")
print(f"{team_a}: {len(a_bat)} bat / {len(a_pit)} pit;  {team_b}: {len(b_bat)} bat / {len(b_pit)} pit")

# %%
display(section("Offense Compare"))
display(pd.concat([batting_line(a_bat).rename(team_a), batting_line(b_bat).rename(team_b)], axis=1))
splits_bar_chart(batting_splits(a_bat, axis="vs_hand"), metric="wOBA", title=f"{team_a} vs Hand")
splits_bar_chart(batting_splits(b_bat, axis="vs_hand"), metric="wOBA", title=f"{team_b} vs Hand")

# %%
display(section("Pitching Compare"))
display(pd.concat([pitching_line(a_pit).rename(team_a), pitching_line(b_pit).rename(team_b)], axis=1))
pitch_usage_bar(a_pit, title=f"{team_a} Staff Usage")
pitch_usage_bar(b_pit, title=f"{team_b} Staff Usage")
velocity_distribution(a_pit, kind="kde", title=f"{team_a} Velo")
velocity_distribution(b_pit, kind="kde", title=f"{team_b} Velo")

# %% tags=["summary"]
display(section("Takeaways"))
_summary = [
    f'→ {team_a} wOBA {batting_line(a_bat).get("wOBA", 0):.3f} vs {team_b} wOBA {batting_line(b_bat).get("wOBA", 0):.3f}.',
    f'→ {team_a} staff K-BB% {pitching_line(a_pit).get("K-BB%", 0):.1%} vs {team_b} staff K-BB% {pitching_line(b_pit).get("K-BB%", 0):.1%}.',
]
display(Markdown("\n".join(_summary)))
