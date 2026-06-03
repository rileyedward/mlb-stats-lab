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
# # Team Season Snapshot
# *State of the union for a single team.*

# %% tags=["parameters"]
team = "SEA"
season = None
start_date = None
end_date = None
recent_window_games = 15

# %% tags=["setup"] jupyter={"source_hidden": true}
from IPython.display import Markdown, display

from mlb_stats_lab.batting import batting_line, contact_quality, plate_discipline
from mlb_stats_lab.batting.splits import splits as batting_splits
from mlb_stats_lab.data import (
    current_season,
    get_standings,
    get_statcast_for_team,
    season_range,
    team_schedule,
)
from mlb_stats_lab.pitching import arsenal_summary, pitching_line
from mlb_stats_lab.reports.summary import team_bullets
from mlb_stats_lab.viz import (
    ev_la_scatter,
    metric_row,
    pitch_usage_bar,
    report_header,
    section,
    splits_bar_chart,
    stat_table,
    velocity_distribution,
)

season = season or current_season()
if start_date is None or end_date is None:
    s, e = season_range(season)
    start_date = start_date or s
    end_date = end_date or e

display(report_header(f"{team} Snapshot", f"{season} season · {start_date} → {end_date}", team=team))

# %% tags=["load"] jupyter={"source_hidden": true}
bat_df = get_statcast_for_team(team, start=start_date, end=end_date, side="batting")
pit_df = get_statcast_for_team(team, start=start_date, end=end_date, side="pitching")
schedule = team_schedule(team, year=season)
print(f"Batting rows: {len(bat_df)}, Pitching rows: {len(pit_df)}, Schedule rows: {len(schedule)}")

# %%
display(section("Record & Standings"))
display(schedule.head() if not schedule.empty else Markdown("*No schedule data.*"))
display(get_standings(season).head(20))

# %%
display(section("Offense"))
bat_line = batting_line(bat_df)
display(
    metric_row(
        {
            "wOBA": bat_line.get("wOBA"),
            "OPS": bat_line.get("OPS"),
            "HR": bat_line.get("HR"),
            "BB%": bat_line.get("BB%"),
            "K%": bat_line.get("K%"),
        },
        team=team,
    )
)
display(stat_table(bat_line, "Batting Line"))
display(stat_table(contact_quality(bat_df), "Contact Quality"))
display(stat_table(plate_discipline(bat_df), "Plate Discipline"))
splits_bar_chart(batting_splits(bat_df, axis="vs_hand"), metric="wOBA", title="Offense vs Hand")
splits_bar_chart(batting_splits(bat_df, axis="month"), metric="wOBA", title="Offense by Month")
ev_la_scatter(bat_df, title="Team EV / LA")

# %%
display(section("Pitching"))
staff_line = pitching_line(pit_df)
display(stat_table(staff_line, "Staff Line"))
display(arsenal_summary(pit_df))
pitch_usage_bar(pit_df, title="Staff Usage")
velocity_distribution(pit_df, kind="box", title="Staff Velocity")

# %% tags=["summary"]
display(section("Takeaways"))
display(Markdown("\n".join(team_bullets(bat_line, staff_line))))
