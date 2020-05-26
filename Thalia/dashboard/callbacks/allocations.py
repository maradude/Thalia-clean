import json
from datetime import datetime

import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from .. import user_csv
from ..config import MAX_PORTFOLIOS
from ..portfolio_manager import (
    get_portfolios_list,
    get_own_portfolio,
    store_portfolio,
    load_public_portfolio,
)
from ..strategy import normalise


def register_allocations_tab(dashapp):
    register_update_portfolio(dashapp)
    register_add_portfolio(dashapp)
    register_warning_csv(dashapp)
    register_warning_message(dashapp)
    register_warning_date_csv(dashapp)

    register_save_portfolio(dashapp)
    register_list_portfolios(dashapp)


def load_shared_portfolio(path):

    arg = path.rsplit("/", 1)[1]

    try:
        if len(arg) == 64:
            portfolio, strategy = load_public_portfolio(arg)
        else:
            porto_id = int(arg)
            portfolio, strategy = get_own_portfolio(porto_id)

    except ValueError:
        raise PreventUpdate

    return parse_stored_portfolio(portfolio, strategy)


def register_update_portfolio(dashapp):
    """ Callback tying the ticker dropdown to table """
    states = []
    for i in range(1, MAX_PORTFOLIOS + 1):
        states.append(
            (
                [
                    Output(f"memory-table-{i}", "data"),
                    Output(f"portfolio-name-{i}", "value"),
                ],
                [
                    Input(f"memory-ticker-{i}", "value"),
                    Input(f"lazy-portfolios-{i}", "value"),
                    Input(f"stored-portfolios-{i}", "value"),
                    Input(f"upload-data-{i}", "contents"),
                ],
                [
                    State(f"upload-data-{i}", "filename"),
                    State(f"memory-table-{i}", "data"),
                ],
            )
        )

    first_portfolio = states[0]
    first_portfolio[1].append(Input("page-location-url", "pathname"))
    dashapp.callback(*first_portfolio)(update_first_portfolio)

    for state in states[1:]:
        dashapp.callback(*state)(update_portfolio)


def update_first_portfolio(
    ticker_selected,
    lazy_portfolio,
    saved_portfolio,
    user_csv,
    url_path,
    filename,
    table_data,
):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    else:
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger == "page-location-url" and url_path is not None:
        results = load_shared_portfolio(url_path)
    else:
        results = update_portfolio(
            ticker_selected,
            lazy_portfolio,
            saved_portfolio,
            user_csv,
            filename,
            table_data
        )
    return results


def register_save_portfolio(dashapp):
    for i in range(1, MAX_PORTFOLIOS + 1):
        dashapp.callback(
            [
                Output(f"save-portfolio-success-{i}", "children"),
                Output(f"save-portfolio-success-{i}", "className"),
            ],
            [Input(f"save-portfolio-{i}", "n_clicks")],
            [
                State("my-date-picker-range", "start_date"),
                State("my-date-picker-range", "end_date"),
                State("input-money", "value"),
                State(f"portfolio-name-{i}", "value"),
                State(f"memory-table-{i}", "data"),
            ],
        )(save_portfolio)


def register_list_portfolios(dashapp):
    dashapp.callback(
        [
            Output(f"stored-portfolios-{i}", "options")
            for i in range(1, MAX_PORTFOLIOS + 1)
        ],
        [
            Input(f"save-portfolio-success-{i}", "children")
            for i in range(1, MAX_PORTFOLIOS + 1)
        ]
        + [Input("page-location-url", "href")],
    )(list_stored_portfolios)


def list_stored_portfolios(*_):
    portfolios = get_portfolios_list()
    options = [{"label": name, "value": pid} for pid, name in portfolios]
    return [options] * MAX_PORTFOLIOS


def parse_stored_portfolio(porto, strat):
    assets = []
    for tkr in strat.assets:
        ticker, name = tkr.ticker.split("|")
        assets.append({"AssetTicker": ticker, "Name": name, "Allocation": tkr.weight})
    return assets, porto.name


def save_portfolio(n_clicks, start_date, end_date, input_money, name, table_data):
    if n_clicks is None:
        raise PreventUpdate

    if not table_data or any(tkr["Allocation"] == 0 for tkr in table_data):
        raise PreventUpdate

    if any(tkr.get("Handle") for tkr in table_data):
        message = (
            f"You can not save portfolios with your own uploaded assets,"
            " please remove the asset before saving"
        )
        notification_type = "notification is-warning"
        return message, notification_type

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    allocations = [tkr["Allocation"] for tkr in table_data]
    normalise(allocations)
    tickers = (f"{tkr['AssetTicker']}|{tkr['Name']}" for tkr in table_data)

    success = store_portfolio(
        start_date, end_date, input_money, name, zip(tickers, allocations)
    )
    if success:
        message = f"Portfolio {name} saved"
        notification_type = "notification is-success"
    else:
        message = (
            f"You already have a portfolio called {name},"
            " please rename the portfolio and try again"
        )
        notification_type = "notification is-warning"

    return message, notification_type


def register_add_portfolio(dashapp):
    """ Callback for adding new portfolios and disabling button at 5 """
    dashapp.callback(
        [Output(f"portfolio-{i}", "style") for i in range(1, MAX_PORTFOLIOS + 1)]
        + [Output("add-portfolio-btn", "disabled")],
        [Input("add-portfolio-btn", "n_clicks")],
        [State(f"portfolio-{i}", "style") for i in range(1, MAX_PORTFOLIOS + 1)],
    )(add_portfolio)


def register_warning_message(dashapp):
    for i in range(1, MAX_PORTFOLIOS + 1):
        dashapp.callback(
            Output(f"confirm-{i}", "displayed"),
            [Input("submit-btn", "n_clicks")],
            [
                State("my-date-picker-range", "start_date"),
                State("my-date-picker-range", "end_date"),
                State("input-money", "value"),
                State(f"memory-table-{i}", "data"),
            ],
        )(warning_message)


def register_warning_csv(dashapp):
    for i in range(1, MAX_PORTFOLIOS + 1):
        dashapp.callback(
            Output(f"confirm-csv-{i}", "displayed"),
            [Input(f"upload-data-{i}", "contents")],
        )(user_csv_warning)


def register_warning_date_csv(dashapp):
    for i in range(1, MAX_PORTFOLIOS + 1):
        dashapp.callback(
            Output(f"confirm-csv-date-{i}", "displayed"),
            [Input(f"upload-data-{i}", "contents")],
        )(user_csv_date_warning)


def warning_message(n_clicks, start_date, end_date, input_money, table):
    values = (start_date, end_date, input_money, table)
    if n_clicks:
        return not all(values)


def update_portfolio(
    ticker_selected, lazy_portfolio, saved_portfolio, user_csv, filename, table_data
):
    """
    Filters the selected tickers from the dropdown menu.
    """
    if (ticker_selected or lazy_portfolio or user_csv or saved_portfolio) is None:
        raise PreventUpdate

    if table_data is None:
        table_data = []
    portfolio_name = dash.no_update  # only update the name when loading a portfolio

    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    else:
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]

    # load complete portfolio
    if trigger.startswith("stored-portfolios"):
        portfolio, strategy = get_own_portfolio(saved_portfolio)
        table_data, portfolio_name = parse_stored_portfolio(portfolio, strategy)
    elif trigger.startswith("lazy-portfolios"):
        table_data = list(json.loads(lazy_portfolio).values())

    # load single asset
    else:
        if trigger.startswith("upload-data"):
            user_supplied_csv = update_output(user_csv, filename)
            filename = user_supplied_csv[0]
            handle = user_supplied_csv[1]
            asset = {
                "AssetTicker": filename,
                "Handle": handle,
                "Allocation": 0,
            }

        else:
            ticker, name = ticker_selected.split(" – ")
            asset = {"AssetTicker": ticker, "Name": name, "Allocation": 0}

        if all(
            asset["AssetTicker"] != existing["AssetTicker"] for existing in table_data
        ):
            table_data.append(asset)

    return table_data, portfolio_name


def user_csv_warning(contents):
    if contents is not None:
        content_type, content_string = contents.split(",")
        try:
            user_csv.store(content_string)
        except user_csv.FormattingError:
            return True


def user_csv_date_warning(contents):
    if contents is not None:
        content_type, content_string = contents.split(",")
        try:
            user_csv.store_checked(content_string)
        except user_csv.anda.InsufficientTimeframe:
            return True


def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        children = [user_data(list_of_contents, list_of_names)]
        return children[0]


def user_data(contents, filename):
    content_type, content_string = contents.split(",")
    try:
        handle = user_csv.store(content_string)
    except user_csv.FormattingError:
        raise PreventUpdate
    try:
        handle = user_csv.store_checked(content_string)
    except user_csv.anda.InsufficientTimeframe:
        raise PreventUpdate
    return [filename, handle]


def add_portfolio(n_clicks, *args):
    """
    Makes input fields for another portfolio visible.
    If the number of portfolios has reached MAX_PORTFOLIOS, no update.
    """
    if n_clicks is None or n_clicks >= MAX_PORTFOLIOS:
        raise PreventUpdate

    no_portfolios = n_clicks

    ret = list(args)
    ret[no_portfolios] = {"display": "block"}
    if no_portfolios < MAX_PORTFOLIOS - 1:
        return ret + [False]
    else:
        return ret + [True]
