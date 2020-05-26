from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_html_components as html
import dash
from decimal import Decimal

from analyse_data import analyse_data as anda
from .dashboard import validate_dates
from ..strategy import get_assets


def register_overfitting_tab(dashapp):
    disable_button_callback(dashapp)
    run_overfitting_test(dashapp)


def disable_button_callback(dashapp):
    dashapp.callback(
        Output("overfitting-btn", "disabled"),
        [Input("overfitting-btn", "n_clicks"), Input("submit-btn", "n_clicks")],
    )(disable_button)


def run_overfitting_test(dashapp):
    dashapp.callback(
        Output("overfitting-results", "children"),
        [Input("overfitting-btn", "n_clicks")],
        [State("portfolio-results", "data")],
    )(update_overfitting)


def disable_button(overfit_btn, submit_btn):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id == "overfitting-btn":
        return True
    else:
        return False


def update_overfitting(overfit_btn, portfolio_data):
    if overfit_btn is None:
        raise PreventUpdate

    overfitted_names = []
    udata_names = []
    for portfolio in portfolio_data:
        if portfolio["has_user_uploaded"]:
            udata_names.append(portfolio["name"])
        elif check_overfitting(portfolio):
            overfitted_names.append(portfolio["name"])

    udata_portfolios = html.Ul([html.Li(pname) for pname in udata_names])
    overfitted_portfolios = html.Ul([html.Li(pname) for pname in overfitted_names])

    if ((len(overfitted_names) == 0) and (len(udata_names) == 0)):
        return html.Div(
            children="We have not detected overfitting in any of your portfolios.",
            className="notification is-info",
        )
    elif(len(overfitted_names) == 0):
        return html.Div(
            children=[
                "Although no overfitting was detected, the following portfolio(s) contain \
                 user uploaded assets and therefore couldn't be checked: \n",
                udata_portfolios,
            ],
            className="notification is-warning"
        )
    elif(len(udata_names) == 0):
        return html.Div(
            children=[
                "WARNING: We have detected overfitting on the folowing simulations: \n",
                overfitted_portfolios,
            ],
            className="notification is-warning",
        )
    else:
        return html.Div(
            children=[
                "WARNING: We have detected overfitting on the folowing simulations: \n",
                overfitted_portfolios,
                "Additionally the following portfolio(s) contained user uploaded assets \
                and therefore couldn't be checked: \n",
                udata_portfolios,
            ],
            className="notification is-warning",
        )

def check_overfitting(portfolio, sharpe_threshold=0.5, sortino_threshold=0.5):
    """
    Checks and returns wether strategy is overfitted
    (By comparing to simulation results on rest of available date range)
    Threshold for performance difference considered indicative of overfitting
    """
    proportions = [Decimal(p) for p in portfolio["proportions"]]
    assets_data_all = get_assets(
        portfolio["tickers"], proportions, None, None
    )

    s_date = max([asset.values.index[0] for asset in assets_data_all])
    e_date = min(asset.values.index[-1] for asset in assets_data_all)

    new_strat = anda.Strategy(
        s_date,
        e_date,
        portfolio["input_money"],
        assets_data_all,
        validate_dates(s_date, e_date, portfolio["contribution_dates"]),
        portfolio["contribution_amount"],
        validate_dates(s_date, e_date, portfolio["rebalancing_dates"]),
    )

    old_sharpe = (portfolio["sharpe"])[portfolio["name"]]
    old_sortino = (portfolio["sortino"])[portfolio["name"]]

    new_sharpe = round(anda.sharpe_ratio(new_strat, None), 2)
    new_sortino = round(anda.sortino_ratio(new_strat, None), 2)

    return (old_sharpe > new_sharpe + Decimal(sharpe_threshold)) or (
        old_sortino > new_sortino + Decimal(sortino_threshold)
    )