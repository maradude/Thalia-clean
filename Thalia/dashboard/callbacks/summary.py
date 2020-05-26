from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

from ..config import OFFICIAL_COLOURS


def register_summary_tab(dashapp):
    register_print_dates(dashapp)


def register_print_dates(dashapp):
    """ Callback for showing dates on summary tab """
    dashapp.callback(
        Output("output-dates", "children"),
        [Input("submit-btn", "n_clicks")],
        [
            State("my-date-picker-range", "start_date"),
            State("my-date-picker-range", "end_date"),
        ],
    )(print_dates)


def print_dates(n_clicks, start_date, end_date):
    if n_clicks is None:
        raise PreventUpdate
    start = f"{start_date.split('-')[2]}/{start_date.split('-')[1]}/{start_date.split('-')[0]}"
    end = f"{end_date.split('-')[2]}/{end_date.split('-')[1]}/{end_date.split('-')[0]}"
    return f"Selected interval: {start} - {end}"


def get_yearly_differences_graph(name, diffs, start_date, end_date):
    years = list(range(start_date.year, end_date.year + 1))
    annual_figure = go.Figure(
        data=[go.Bar(name=name, y=diffs, x=years, marker_color=OFFICIAL_COLOURS[3])]
    )
    annual_figure.update_layout(
        xaxis_title="Year",
        yaxis_title="Difference (%)",
        font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"),
    )
    # If only 6 years of data show every year on the x axis
    if len(years) <= 6:
        annual_figure.update_xaxes(dtick=1)
    # Else let Dash figure it out
    return annual_figure


def get_pie_charts(tickers, proportions):
    """
    Returns Pie charts, and visibility for their divs
    Input: List of Ticker Names and List of corresponding Proportions
    Output: Go.Figure object
    """
    fig = go.Figure(data=[go.Pie(labels=tickers, values=proportions)])
    fig.update_traces(hoverinfo="label", marker=dict(colors=OFFICIAL_COLOURS))

    return [fig, {"display": "block"}]
