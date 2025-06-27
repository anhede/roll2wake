from dash import Dash, dcc, html
import plotly.express as px

class DashboardApp:
    def __init__(self, server, url_base_pathname: str = '/dashboard/'):
        self.app = Dash(
            __name__,
            server=server,
            url_base_pathname=url_base_pathname
        )
        # Dash auto-loads assets/style.css
        self.app.layout = self._build_layout()

    def _build_layout(self):
        # Placeholder metric values for row 1
        today_values = [123, 45, 67]
        # Placeholder averages for rows 2 & 3
        avg_values = [50, 60]

        # Placeholder figures
        fig1 = px.line(x=[1,2,3,4], y=[10,20,15,25], title='Metric Trend 1')
        fig2 = px.line(x=[1,2,3,4], y=[5,15,10,20], title='Metric Trend 2')

        return html.Div([
            # Title header
            html.Div(
                children=[
                    html.H1("WakeUpBro Dashboard", className='dashboard-title'),
                    html.P("Overview of sleep trends for the last", className='dashboard-subtitle'),
                    html.Div([
                        dcc.Dropdown(
                            id='preset-date-range',
                            options=[
                                {'label': '1 week',   'value': '1w'},
                                {'label': '2 weeks', 'value': '2w'},
                                {'label': '1 month', 'value': '1m'},
                                {'label': '6 months','value': '6m'},
                                {'label': '12 months','value':'12m'}
                            ],
                            value='1w',
                            clearable=False,
                            style={'width': '200px', 'margin': '0 auto'}
                        )
                    ], className='flex-item')
                ],
                className='dashboard-header',
            ),
            # Row 1
            html.Div(
                children=[
                    html.Div([
                        html.H1(str(val), className='metric-value'),
                        html.P("Today's value", className='metric-label')
                    ], className='flex-item')
                    for val in today_values
                ],
                className='row'
            ),

            # Dropdown

            # Row 2
            html.Div([
                html.Div([
                    html.H1(str(avg_values[0]), className='metric-value'),
                    html.P("Average metric", className='metric-label')
                ], className='flex-item'),
                html.Div([
                    dcc.Graph(figure=fig1)
                ], className='flex-plot'),
            ], className='row'),

            # Row 3
            html.Div([
                html.Div([
                    html.H1(str(avg_values[1]), className='metric-value'),
                    html.P("Average metric", className='metric-label')
                ], className='flex-item'),
                html.Div([
                    dcc.Graph(figure=fig2)
                ], className='flex-plot'),
            ], className='row'),

        ], className='dashboard-container')