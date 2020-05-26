from Thalia.dashboard.callbacks import allocations
from dash.exceptions import PreventUpdate
import pytest
from Thalia.dashboard.config import MAX_PORTFOLIOS


def test_add_portfolio():
    with pytest.raises(PreventUpdate):
        allocations.add_portfolio(None)
        pytest.fail("No Update before button press")

    with pytest.raises(PreventUpdate):
        allocations.add_portfolio(MAX_PORTFOLIOS)
        pytest.fail("No Update if number of portfolios have reached maximum")

    returned = allocations.add_portfolio(
        1,
        {"display": "block"},
        {"display": "none"},
        {"display": "none"},
        {"display": "none"},
        {"display": "none"},
    )

    expected = [{"display": "block"}] * 2 + [{"display": "none"}] * (MAX_PORTFOLIOS - 2)
    expected.append(False)
    assert returned == expected

    returned = allocations.add_portfolio(
        MAX_PORTFOLIOS - 1,
        {"display": "block"},
        {"display": "block"},
        {"display": "block"},
        {"display": "block"},
        {"display": "none"},
    )

    expected = [{"display": "block"}] * MAX_PORTFOLIOS
    expected.append(True)
    assert returned == expected
