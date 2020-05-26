from Thalia.dashboard.callbacks import summary
import pytest
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import datetime


def test_print_dates():
    with pytest.raises(PreventUpdate):
        summary.print_dates(n_clicks=None, start_date=None, end_date=None)
        pytest.fail("Print Dates should fail on if button has not been pressed")

    assert "01/01/2010 - 01/01/2020" in summary.print_dates(
        1, "2010-01-01", "2020-01-01"
    )


def test_get_yearly_differences_graph():
    start_date = datetime.date(2000, 1, 1)
    end_date = datetime.date(2003, 1, 1)
    data = [1, 2, 3]
    returned = summary.get_yearly_differences_graph(
        "Portfolio Name", data, start_date, end_date
    )
    assert isinstance(returned, go.Figure)


def test_get_pie_charts():
    tickers = ["A", "B"]
    proportions = [50, 50]
    returned = summary.get_pie_charts(tickers, proportions)
    assert isinstance(returned[0], go.Figure)
    assert returned[1] == {"display": "block"}
