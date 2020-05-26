from Thalia.dashboard import callbacks
import pytest
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import pandas as pd
from analyse_data import analyse_data as anda
from config import Config


def test_check_overfitting(mock_finda):
    # make sure overfitting threshold is something reasonable
    Config.OVERFITTING_THRESH = 0.7
    # create strategy
    start_date = pd.Timestamp(2000, 3, 13)
    end_date = pd.Timestamp(2000, 3, 15)
    # Will trigger for any positive threshold (T = -1.7)
    asset_data = callbacks.get_assets(["OVF"], [1.0], start_date, end_date)
    strategy = anda.Strategy(start_date, end_date, 1, asset_data, [], 0, [],)
    assert callbacks.check_overfitting(strategy)
    # Will not trigger for any reasonable threshold
    asset_data = callbacks.get_assets(["NOVF"], [1.0], start_date, end_date)
    strategy = anda.Strategy(start_date, end_date, 1, asset_data, [], 0, [],)
    assert not callbacks.check_overfitting(strategy)
    # All values, should never trigger since performance should be the same
    start_date = pd.Timestamp(2000, 3, 9)
    end_date = pd.Timestamp(2000, 3, 18)
    asset_data = callbacks.get_assets(["NOVF"], [1.0], start_date, end_date)
    strategy = anda.Strategy(start_date, end_date, 1, asset_data, [], 0, [],)
    assert not callbacks.check_overfitting(strategy)
