from dash import Dash, dcc, html
import plotly.express as px
from db import StatisticsDB
from stats import STAT_INTERACTION, STAT_WAKEUP
import re
import datetime as dt
from dash.dependencies import Input, Output


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
            Output("sleep-graph", "figure"),
            Input("preset-date-range", "value"),
        )
        def update_sleep_graph(preset_value):
            return self.plot_sleep(preset_value)

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
        # Placeholder metric values for row 1
        today_values = [123, 45, 67]
        # Placeholder averages for rows 2 & 3
        avg_values = [50, 60]

        fig1 = self.plot_example()
        fig2 = self.plot_example()

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
                        html.Div(
                            [
                                html.H2(str(val), className="metric-value"),
                                html.P("Today's value", className="metric-label"),
                            ],
                            className="flex-item",
                        )
                        for val in today_values
                    ],
                    className="row",
                ),
                # Dropdown
                # Row 2
                html.Div(
                    [
                        html.Div(
                            [
                                html.H2(str(avg_values[0]), className="metric-value"),
                                html.P("Average metric", className="metric-label"),
                            ],
                            className="flex-item",
                        ),
                        html.Div([dcc.Graph(id="sleep-graph")], className="flex-plot"),
                    ],
                    className="row",
                ),
                # Row 3
                html.Div(
                    [
                        html.Div(
                            [
                                html.H2(str(avg_values[1]), className="metric-value"),
                                html.P("Average metric", className="metric-label"),
                            ],
                            className="flex-item",
                        ),
                        html.Div([dcc.Graph(figure=fig2)], className="flex-plot"),
                    ],
                    className="row",
                ),
            ],
            className="dashboard-container",
        )

    def plot_sleep(self, preset: str):
        # Map your presets to days
        presets = {"1w": 7, "2w": 14, "1m": 30, "6m": 182, "12m": 365}
        days = presets.get(preset, 7)

        end_date = dt.datetime.now()
        start_date = end_date - dt.timedelta(days=days)

        interactions = self.db.query(STAT_INTERACTION, start=start_date, end=end_date)
        interaction_times = [
            dt.datetime.fromisoformat(interaction.timestamp)
            for interaction in interactions
        ]
        wakeups = self.db.query(STAT_WAKEUP, start=start_date, end=end_date)
        wakeup_times = [
            dt.datetime.fromisoformat(wakeup.timestamp) for wakeup in wakeups
        ]

        # Infer sleep times

        print(f"Interaction times: {interaction_times}")
        print(f"Wakeup times: {wakeup_times}")
        fig = px.line(
            x=[1, 2, 3, 4],  # replace with real data
            y=[10, 20, 15, 25],
            title=f"Sleep trend ({preset})",
            color_discrete_sequence=[self.colors["pop"]],
        )
        fig = self.format_fig(fig)
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

    def format_fig(self, fig):
        fig.update_layout(
            paper_bgcolor=self.colors["bg"],  # outer background
            plot_bgcolor=self.colors["bg"],  # inner plotting area
            font_color=self.colors["primary"],  # axis & title text
            xaxis=dict(
                showgrid=True,
                gridcolor=self.colors["mg"],  # e.g. "#444444" or "lightgrey"
                gridwidth=1,
                zeroline=True,
                zerolinecolor=self.colors["mg"],  # <-- Color of x=0 line
                zerolinewidth=2                        # <-- Optional: thickness
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=self.colors["mg"],  # same or different color
                gridwidth=1,
                zeroline=True,
                zerolinecolor=self.colors["mg"],  # <-- Color of x=0 line
                zerolinewidth=2                        # <-- Optional: thickness
            ),
        )
        return fig
