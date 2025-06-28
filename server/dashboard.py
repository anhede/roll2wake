from dash import Dash, dcc, html
import plotly.express as px
from db import StatisticsDB
from stats import STAT_INTERACTION, STAT_WAKEUP

class DashboardApp:
    def __init__(self, server, db: StatisticsDB, url_base_pathname: str = "/dashboard/"):
        self.app = Dash(__name__, server=server, url_base_pathname=url_base_pathname)
        # Dash auto-loads assets/style.css
        self.app.layout = self._build_layout()
        self.db = db

    def _build_layout(self):
        # Placeholder metric values for row 1
        today_values = [123, 45, 67]
        # Placeholder averages for rows 2 & 3
        avg_values = [50, 60]

        # define your CSS vars in Python
        import re

        with open("assets/style.css") as f:
            css = f.read()
        pattern = re.compile(r"--(?P<name>[\w-]+)\s*:\s*(?P<value>#[0-9A-Fa-f]{6});")
        matches = pattern.finditer(css)
        colors = {
            m.group("name").replace("-color", ""): m.group("value") for m in matches
        }
        print("Extracted colors:", colors)

        # when you build your figures:
        # fig1 = px.line(x=[1, 2, 3, 4], y=[10, 20, 15, 25], title="Metric Trend 1")
        # fig2 = px.line(x=[1, 2, 3, 4], y=[5, 15, 10, 20], title="Metric Trend 2")
        fig1 = self.plot_sleep(colors)
        fig2 = px.line(
            x=[1, 2, 3, 4],
            y=[5, 15, 10, 20],
            title="Metric Trend 2",
            color_discrete_sequence=[colors["pop"]],  # use your pop color for the line
        )

        # then override the background + font colors to match
        for fig in [fig1, fig2]:
            fig.update_layout(
                paper_bgcolor=colors["bg"],  # outer background
                plot_bgcolor=colors["bg"],  # inner plotting area
                font_color=colors["primary"],  # axis & title text
                xaxis = dict(
                    showgrid=True,
                    gridcolor=colors["mg"],     # e.g. "#444444" or "lightgrey"
                    gridwidth=1
                ),
                yaxis = dict(
                    showgrid=True,
                    gridcolor=colors["mg"],     # same or different color
                    gridwidth=1
                )
            )

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
                        html.Div([dcc.Graph(figure=fig1)], className="flex-plot"),
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

    def plot_sleep(self, colors):
        """Create a sleep trend plot. Tracks time from latest interaction to wakeup."""
        #end_date = # Today as datetime
        #start_date = # Check dropdown value, subtract from end_date, datetime
        #interaction_times = self.db.query(STAT_INTERACTION, start=, end=)
        return px.line(
            x=[1, 2, 3, 4],
            y=[10, 20, 15, 25],
            title="Metric Trend 1",
            color_discrete_sequence=[colors["pop"]],  # use your pop color for the line
        )
