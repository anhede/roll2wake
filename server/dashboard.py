from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from datetime import datetime
from db import StatisticsDB

class DashboardApp:
    def __init__(self, server, db_path: str = "stats.db", url_base_pathname: str = '/dashboard/'):
        self.db = StatisticsDB(db_path)
        self.app = Dash(
            __name__,
            server=server,
            url_base_pathname=url_base_pathname
        )
        # Use a dynamic layout to always fetch fresh data
        self.app.layout = self.serve_layout
        self._init_callbacks()

    def serve_layout(self):
        all_stats = self.db.query()
        unique_types = sorted({s.type for s in all_stats})

        return html.Div([
            html.H1("IoT Statistics Dashboard"),
            dcc.Dropdown(
                id='type-dropdown',
                options=[{'label': t, 'value': t} for t in unique_types],
                value=unique_types[0] if unique_types else None
            ),
            dcc.DatePickerRange(
                id='date-picker',
                start_date=datetime.utcnow().date(), # type: ignore
                end_date=datetime.utcnow().date() # type: ignore
            ),
            dcc.Graph(id='timeseries-graph'),
        ])

    def _init_callbacks(self):
        @self.app.callback(
            Output('timeseries-graph', 'figure'),
            Input('type-dropdown', 'value'),
            Input('date-picker', 'start_date'),
            Input('date-picker', 'end_date'),
        )
        def update_graph(selected_type, start_date, end_date):
            if not selected_type:
                return {}

            # Parse date inputs
            start = datetime.fromisoformat(start_date) if start_date else None
            end   = datetime.fromisoformat(end_date)   if end_date   else None

            # Query the database
            stats = self.db.query(stat_type=selected_type, start=start, end=end)
            if not stats:
                # No data for the chosen range
                return {}

            # Convert to pandas DataFrame
            df = pd.DataFrame([
                {
                    'timestamp': datetime.fromisoformat(s.timestamp) if isinstance(s.timestamp, str) else s.timestamp,
                    'value': s.value
                }
                for s in stats
            ])

            # Time-series figure
            fig = px.line(
                df,
                x='timestamp',
                y='value',
                title=f"{selected_type} over time"
            )
            return fig

    def run(self):
        # External run is handled by Flask
        pass