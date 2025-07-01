from dash import Dash, dcc, html
import plotly.express as px
from db import StatisticsDB
from stats import STAT_INTERACTION, STAT_WAKEUP
import re
import datetime as dt
from dash.dependencies import Input, Output
from sleep_inference import infer_sleep_periods, SleepRecord
SLEEP, BEDTIME, WAKEUP = range(3)


class DashboardApp:
    def __init__(
        self, server, db: StatisticsDB, url_base_pathname: str = "/dashboard/"
    ):
        self.colors = self._extract_colors()
        self.app = Dash(__name__, server=server, url_base_pathname=url_base_pathname)
        self.app.layout = self._build_layout()
        self._register_callbacks()
        self.db = db

    def _register_callbacks(self):
        @self.app.callback(
            # Row 1 - Averages
            Output("today-sleep", "children"),
            Output("today-gotobed", "children"),
            Output("today-wakeup", "children"),

            # Row 2 - Sleep Graph
            Output("sleep-graph", "figure"),
            Output("avg-sleep", "children"),

            # Row 3 - Bedtime Graph
            Output("bedtime-graph", "figure"),
            Output("avg-bedtime", "children"),

            # Row 4 - Wakeup Graph
            Output("wakeup-graph", "figure"),
            Output("avg-wakeup", "children"),

            # Inputs
            Input("preset-date-range", "value"),
        )
        def update_sleep_graph(preset):
            # Map your presets to days
            presets = {"1w": 7, "2w": 14, "1m": 30, "6m": 182, "12m": 365}
            days = presets.get(preset, 7)
            interaction_times, wakeup_times = self.get_times_from_db(days)
            sleep_records = infer_sleep_periods(interaction_times, wakeup_times)
            if not sleep_records:
                return "-", "-", "-", self.plot_sleep([])

            # Averages and today's values
            today = dt.date.today()
            today_record = next(
                (record for record in sleep_records if record.date == today),
                None
            )
            if today_record:
                today_sleep = f"{today_record.duration.total_seconds() / 3600 :.1f}h"
                today_gotobed = today_record.bedtime.strftime("%H:%M")
                today_wakeup = today_record.wakeup.strftime("%H:%M")
            else:
                today_sleep = "-"
                today_gotobed = "-"
                today_wakeup = "-"

            # Calculate averages
            total_sleep = sum(
                record.duration.total_seconds() for record in sleep_records
            )
            avg_sleep = total_sleep / len(sleep_records) / 3600 if sleep_records else 0
            avg_sleep_str = f"{avg_sleep:.1f}h"

            avg_bedtime = (
                sum(record.bedtime.hour * 60 + record.bedtime.minute for record in sleep_records) /
                len(sleep_records)
            ) if sleep_records else 0
            avg_bedtime_str = f"{int(avg_bedtime // 60):02}:{int(avg_bedtime % 60):02}"

            avg_wakeup = (
                sum(record.wakeup.hour * 60 + record.wakeup.minute for record in sleep_records) /
                len(sleep_records)
            ) if sleep_records else 0
            avg_wakeup_str = f"{int(avg_wakeup // 60):02}:{int(avg_wakeup % 60):02}"

            # Plots
            if days <= 7:
                show_date = False
            else:
                show_date = True
            sleep_fig = self.plot_line_trend(sleep_records, SLEEP, show_date)
            bedtime_fig = self.plot_line_trend(
                sleep_records, BEDTIME, show_date
            )
            wakeup_fig = self.plot_line_trend(
                sleep_records, WAKEUP, show_date
            )

            return (
                today_sleep,
                today_gotobed,
                today_wakeup,
                sleep_fig,
                avg_sleep_str,
                bedtime_fig,
                avg_bedtime_str,
                wakeup_fig,
                avg_wakeup_str,
            )

    def get_times_from_db(self, days):
        

        end_date = dt.datetime.now()
        start_date = end_date - dt.timedelta(days=days + 1)

        interactions = self.db.query(STAT_INTERACTION, start=start_date, end=end_date)
        interaction_times = [
            dt.datetime.fromisoformat(interaction.timestamp)
            for interaction in interactions
        ]
        wakeups = self.db.query(STAT_WAKEUP, start=start_date, end=end_date)
        wakeup_times = [
            dt.datetime.fromisoformat(wakeup.timestamp) for wakeup in wakeups
        ]

        return interaction_times, wakeup_times

    def _extract_colors(self):
        with open("assets/style.css") as f:
            css = f.read()
        pattern = re.compile(r"--(?P<name>[\w-]+)\s*:\s*(?P<value>#[0-9A-Fa-f]{6});")
        matches = pattern.finditer(css)
        colors = {
            m.group("name").replace("-color", ""): m.group("value") for m in matches
        }
        print("Extracted colors:", colors)
        return colors

    def _build_layout(self):
        return html.Div(
            [
                # Title header
                html.Div(
                    children=[
                        html.H1("WakeUpBro Dashboard", className="dashboard-title"),
                        html.P(
                            "Overview of sleep trends for the last",
                            className="dashboard-subtitle",
                        ),
                        html.Div(
                            [
                                dcc.Dropdown(
                                    id="preset-date-range",
                                    options=[
                                        {"label": "1 week", "value": "1w"},
                                        {"label": "2 weeks", "value": "2w"},
                                        {"label": "1 month", "value": "1m"},
                                        {"label": "6 months", "value": "6m"},
                                        {"label": "12 months", "value": "12m"},
                                    ],
                                    value="1w",
                                    clearable=False,
                                )
                            ],
                            className="flex-item",
                        ),
                    ],
                    className="dashboard-header",
                ),
                # Row 1
                html.Div(
                    children=[
                        html.H2("Today's stats", id="today-stats-title", className="dashboard-section-title"),
                        html.Div(
                            children=[
                                html.Div(
                                    [
                                        html.H2(
                                            "-",
                                            id=f"today-{stat_type}",
                                            className="metric-value",
                                        ),
                                        html.P(metric_name, className="metric-label"),
                                    ],
                                    className="flex-item",
                                )
                                for stat_type, metric_name in zip(["sleep", "gotobed", "wakeup"], 
                                                                   ["Sleep", "Bedtime", "Wakeup"])
                            ],
                            className="row",
                        )
                    ],
                    className="row column"   # <-- notice the extra “column” here
                ),
                # Dropdown
                # Row 2 – Sleep overview
                html.Div(
                    className="dashboard-section",
                    children=[
                        html.H2("Sleep", className="dashboard-section-title"),
                        html.Div(
                            [
                                html.Div([dcc.Graph(id="sleep-graph")], className="flex-plot"),
                                html.Div(
                                    [
                                        html.H2("-", id='avg-sleep', className="metric-value"),
                                        html.P("Average sleep", className="metric-label"),
                                    ],
                                    className="flex-item",
                                ),
                            ],
                            className="row",
                        ),
                    ],
                ),

                # Row 3 – Bedtime
                html.Div(
                    className="dashboard-section",
                    children=[
                        html.H2("Bedtime", className="dashboard-section-title"),
                        html.Div(
                            [
                                html.Div([dcc.Graph(id='bedtime-graph')], className="flex-plot"),
                                html.Div(
                                    [
                                        html.H2("-", id='avg-bedtime', className="metric-value"),
                                        html.P("Average bedtime", className="metric-label"),
                                    ],
                                    className="flex-item",
                                ),
                            ],
                            className="row",
                        ),
                    ],
                ),

                # Row 4 – Wakeup
                html.Div(
                    className="dashboard-section",
                    children=[
                        html.H2("Wakeup", className="dashboard-section-title"),
                        html.Div(
                            [
                                html.Div([dcc.Graph(id='wakeup-graph')], className="flex-plot"),
                                html.Div(
                                    [
                                        html.H2("-", id='avg-wakeup', className="metric-value"),
                                        html.P("Average wakeup", className="metric-label"),
                                    ],
                                    className="flex-item",
                                ),
                            ],
                            className="row",
                        ),
                    ],
                ),

            ],
            className="dashboard-container",
        )

    def plot_sleep(self, sleep_records: list[SleepRecord], show_date: bool):
        """Create a sleep trend plot. Tracks time from latest interaction to wakeup."""
        import plotly.graph_objects as go

        days = [sleep_record.date for sleep_record in sleep_records]
        hours_slept = [
            sleep_record.duration.total_seconds() / 3600
            for sleep_record in sleep_records
        ]

        # create a parallel list of timedelta strings
        td_strs = [
            f"{int(sleep_record.duration.total_seconds() // 3600)}h {int((sleep_record.duration.total_seconds() % 3600) // 60)}m"
            for sleep_record in sleep_records
        ]

        bar = go.Bar(
            x=days,
            y=hours_slept,
            # attach the formatted timedeltas
            customdata=td_strs,
            # you can show date & sleep:
            hovertemplate="%{customdata}" + "<extra></extra>",
            marker=dict(
                color=self.colors["pop"],
                line=dict(width=0),
                cornerradius=8,
            ),
        )

        fig = go.Figure(data=[bar])
        fig.update_layout(
            xaxis=dict(type="date"),
        )

        fig = self.format_fig(fig, show_date)

        return fig
    
    def plot_line_trend(self, sleep_records: list[SleepRecord], stat: int, show_date: bool):
        """
        Create a line trend plot for wakeup or bedtime.
        """
        import plotly.graph_objects as go

        if stat == SLEEP:
            times = [
                f"{rec.bedtime.time().strftime('%H:%M')} - {rec.wakeup.time().strftime('%H:%M')}"
                for rec in sleep_records
            ]
            minutes = [
                (rec.wakeup.hour * 60 + rec.wakeup.minute) - (rec.bedtime.hour * 60 + rec.bedtime.minute)
                for rec in sleep_records
            ]
        elif stat == BEDTIME:
            times = [rec.bedtime.time().strftime("%H:%M") for rec in sleep_records]
            minutes = [
                rec.bedtime.hour * 60 + rec.bedtime.minute for rec in sleep_records
            ]
        elif stat == WAKEUP:
            times = [rec.wakeup.time().strftime("%H:%M") for rec in sleep_records]
            minutes = [
                rec.wakeup.hour * 60 + rec.wakeup.minute for rec in sleep_records
            ]

        days = [record.date for record in sleep_records]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=days,
                y=minutes,
                mode="lines+markers",
                line=dict(color=self.colors["pop"]),
                marker=dict(size=8),
                text=times,
                hovertemplate="%{x}<br>%{text}<extra></extra>",
            )
        )

        if stat == SLEEP:
            # Set y-axis to show sleep duration in hours
            fig.update_yaxes(
                tickvals=list(range(0, max(minutes) + 1, 30)),
                ticktext=[f"{i // 60}h {i % 60}m" for i in range(0, max(minutes) + 1, 30)],
            )
        else:
            # Set y-axis ticks to the times
            min_minute = min(minutes)
            max_minute = max(minutes)
            # Choose a reasonable step (e.g., every 30 minutes)
            step = 30
            yticks = list(range((min_minute // step) * step, ((max_minute // step) + 1) * step + 1, step))
            yticklabels = [f"{h:02}:{m:02}" for h, m in [(m // 60, m % 60) for m in yticks]]
            fig.update_yaxes(
                tickvals=yticks,
                ticktext=yticklabels,
            )

        fig = self.format_fig(fig, show_date)
        return fig


    def plot_example(self):
        """Create a sleep trend plot. Tracks time from latest interaction to wakeup."""
        import plotly.graph_objects as go
        import pandas as pd

        df = pd.DataFrame(
            {
                "day": pd.to_datetime(
                    [
                        "2025-06-23",
                        "2025-06-24",
                        "2025-06-25",
                        "2025-06-26",
                        "2025-06-27",
                    ]
                ),
                "value": [10, 15, 13, 17, 12],
            }
        )

        bar = go.Bar(
            x=df["day"],
            y=df["value"],
            marker=dict(
                color=self.colors["pop"],
                line=dict(width=0),
                cornerradius=8,
            ),
        )

        fig = go.Figure(data=[bar])
        fig.update_layout(
            xaxis=dict(title="Day", type="date"),
            yaxis=dict(title="Sleep Time (hours)"),
            hovermode="x",
        )

        fig = self.format_fig(fig)

        return fig

    def format_fig(self, fig, show_date: bool = True):
        fig.update_layout(
            paper_bgcolor=self.colors["bg"],  # outer background
            plot_bgcolor=self.colors["bg"],  # inner plotting area
            font_color=self.colors["primary"],  # axis & title text
            font_family="Fira Code, monospace",
            title=dict(
                x=0.5,  # Center the title
                font=dict(size=24),
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor=self.colors["mg"],  # e.g. "#444444" or "lightgrey"
                gridwidth=1,
                zeroline=True,
                zerolinecolor=self.colors["mg"],  # <-- Color of x=0 line
                zerolinewidth=2,  # <-- Optional: thickness
                title=dict(font=dict(size=22)),
                tickformat="%a %d %b" if show_date else "%A",  # e.g. "Mon 01 Jan"
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=self.colors["mg"],  # same or different color
                gridwidth=1,
                zeroline=True,
                zerolinecolor=self.colors["mg"],  # <-- Color of x=0 line
                zerolinewidth=2,  # <-- Optional: thickness
                title=dict(font=dict(size=22)),
            ),
            margin=dict(l=0, r=00, t=40, b=40),
            #height=200,
            #width=400,
        )
        return fig
