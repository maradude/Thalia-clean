from datetime import datetime
from decimal import Decimal

import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from analyse_data import analyse_data as anda

from ..config import MAX_PORTFOLIOS, NO_TABS, OFFICIAL_COLOURS
from ..strategy import get_strategy
from .drawdowns import get_drawdowns_tables
from .metrics import combine_cols, get_table_data
from .returns import portfolios_figure, update_table
from .summary import get_pie_charts, get_yearly_differences_graph


def register_dashboard(dashapp):
    # Register sending portfolio data
    register_update_dashboard(dashapp)

    # Register tab switch upon submit
    register_tab_switch(dashapp)

    # register error message for allocations
    register_allocation_warning_message(dashapp)
    register_date_warning_message(dashapp)
    register_overlap_timeframe(dashapp)


def register_update_dashboard(dashapp):
    """
    Main callback, all outputs depend on a single strategy object instantiated here.
    Returning values instead of html children objects makes the code testable.
    """
    # Backtest constraints
    states = [
        State("my-date-picker-range", "start_date"),
        State("my-date-picker-range", "end_date"),
        State("input-money", "value"),
    ]

    outputs = [
        # Portfolio Growth Graph
        Output(f"main-graph", "figure"),
        # Returns tab
        Output(f"return-table", "children"),
        Output(f"annual-returns-portfolios", "figure"),
        # Dradwons tab
        Output("drawdowns-graph", "figure"),
    ]
    for i in range(1, MAX_PORTFOLIOS + 1):

        # Portfolio specific data
        states += [
            State(f"portfolio-name-{i}", "value"),
            State(f"input-contribution-{i}", "value"),
            State(f"contribution-dropdown-{i}", "value"),
            State(f"rebalancing-dropdown-{i}", "value"),
            State(f"memory-table-{i}", "data"),
        ]

        # Portfolio specific out
        outputs += [
            # Box visibility
            Output(f"metrics-box-{i}", "style"),
            # Box data
            Output(f"box-Portfolio Name-{i}", "children"),
            Output(f"box-Start Date-{i}", "children"),
            Output(f"box-End Date-{i}", "children"),
            Output(f"box-Initial Investment-{i}", "children"),
            Output(f"box-Final Balance-{i}", "children"),
            Output(f"box-Difference in Best Year-{i}", "children"),
            Output(f"box-Difference in Worst Year-{i}", "children"),
            Output(f"box-Best Year-{i}", "children"),
            Output(f"box-Worst Year-{i}", "children"),
            # Annual returns graph
            Output(f"annual-returns-{i}", "figure"),
            # Pie Chart
            Output(f"pie-{i}", "figure"),
            Output(f"graph-box-pie-{i}", "style"),
            # Drawdowns Table
            Output(f"drawdowns-portfolio-name-{i}", "children"),
            Output(f"drawdowns-table-{i}", "data"),
            Output(f"drawdowns-table-col-{i}", "style"),
        ]

    outputs += [
        # Metrics Table
        Output("key_metrics_table", "columns"),
        Output("key_metrics_table", "data"),
        # Store data for overfitting tests
        Output("portfolio-results", "data"),
        # exception button click
        Output("exceptions-btn", "exception_clicks"),
    ]

    dashapp.callback(outputs, [Input("submit-btn", "n_clicks")], states)(
        update_dashboard
    )


def register_date_warning_message(dashapp):
    dashapp.callback(
        Output("confirm-date", "displayed"),
        [Input("submit-btn", "n_clicks")],
        [
            State("my-date-picker-range", "start_date"),
            State("my-date-picker-range", "end_date"),
        ],
    )(date_warning_message)


def register_overlap_timeframe(dashapp):
    dashapp.callback(
        Output("timeframe_bug", "displayed"),
        [Input("exceptions-btn", "exception_clicks")],
    )(timeframe_overlap_warning)


def register_allocation_warning_message(dashapp):
    for i in range(1, MAX_PORTFOLIOS + 1):
        dashapp.callback(
            Output(f"confirm-allocation-{i}", "displayed"),
            [Input("submit-btn", "n_clicks"), Input(f"save-portfolio-{i}", "n_clicks")],
            [State(f"memory-table-{i}", "data")],
        )(allocation_warning_message)


def register_tab_switch(dashapp):
    """
    On backtest submission: enable all tabs and switch the active tab to the summary page.
    """
    dashapp.callback(
        [
            Output("tabs", "value"),
            Output("summary", "disabled"),
            Output("metrics", "disabled"),
            Output("returns", "disabled"),
            Output("drawdowns", "disabled"),
            Output("assets", "disabled"),
            Output("overfitting", "disabled"),
        ],
        [Input("submit-btn", "n_clicks"), Input("exceptions-btn", "exception_clicks"),],
        [
            State("my-date-picker-range", "start_date"),
            State("my-date-picker-range", "end_date"),
            State("input-money", "value"),
        ]
        + [State(f"memory-table-{i}", "data") for i in range(1, MAX_PORTFOLIOS + 1)],
    )(tab_switch)


def timeframe_overlap_warning(n_clicks):
    if n_clicks:
        return True


def allocation_warning_message(submit_btn, save_btn, table_data):
    if (submit_btn or save_btn) is None or not table_data:
        raise PreventUpdate
    for tkr in table_data:
        return any(tkr["Allocation"] == 0 for tkr in table_data)


def check_date(start_date, end_date):
    """
    Returns True if the dates are far enough apart for anda to make use of them properly,
    False if not.
    """
    real_end_date = datetime.strptime(end_date, "%Y-%m-%d")
    real_start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if (real_end_date - real_start_date).days < 365:
        return True

    date_range_jans = pd.date_range(real_start_date, real_end_date, freq="D")
    return len(anda._jan_firsts(date_range_jans)) < 2


def date_warning_message(n_clicks, start_date, end_date):
    if n_clicks is None or start_date is None or end_date is None:
        raise PreventUpdate

    if n_clicks:
        return check_date(start_date, end_date)


def tab_switch(n_clicks, exception_clicks, *args):
    if exception_clicks is not None:
        return ["allocations"] + [True] * (NO_TABS - 1)

    if n_clicks is None or not all(args[:4]):
        raise PreventUpdate

    if len(args) > 1:
        if check_date(args[0], args[1]):
            raise PreventUpdate

        tkrs = args[3:]
        for tkr in tkrs:
            if tkr:
                if any(Decimal(tkr[i]["Allocation"]) == 0 for i in range(len(tkr))):
                    raise PreventUpdate

    # Current tab + diasbled = False for all other
    return ["summary"] + [False] * (NO_TABS - 1)


def retrieve_args(args):
    def get_args(args, offset):
        """
        Returns offset-th element of arguments
        Needed to work around dynamic Dash elements
        """
        return [list(args)[i * 5 + offset] for i in range(MAX_PORTFOLIOS)]

    """
    For Regression Testing Parameter changes to Update_dashboard,
    Returns a Dictionary of parameters
    """
    args_dict = {}
    args_dict["Portfolio Names"] = get_args(args, offset=0)
    args_dict["Contribution Amounts"] = get_args(args, offset=1)
    args_dict["Contribution Frequencies"] = get_args(args, offset=2)
    args_dict["Rebalancing Frequencies"] = get_args(args, offset=3)
    args_dict["Ticker Tables"] = get_args(args, offset=4)
    return args_dict


def get_no_portfolios(args):
    """
    Return how many protfolios the user has sent on input,
    based on the first empty argument
    """
    if not args:
        return 0
    elif None in args:
        return args.index(None)
    else:
        return MAX_PORTFOLIOS


def validate_dates(start_date, end_date, frequency):
    """
    Validate the dates selected, return an empty set otherwise
    """
    if str(frequency) != "None":
        return pd.date_range(start_date, end_date, freq=frequency)
    else:
        return set()


def format_date(date):
    format_string = "%Y-%m-%d"
    return datetime.strptime(date, format_string)


def get_box_of_metrics(portfolio_name, strategy_object, key_metrics):
    """
    Returns:
    - Portfolio Name
    - Initial Balance
    - Final Balance
    - Best Year %
    - Worst Year %
    - Best Year
    - Worst Year
    """
    start_date = strategy_object.dates[0].strftime("%d/%m/%Y")
    end_date = strategy_object.dates[-1].strftime("%d/%m/%Y")
    box_metrics = [portfolio_name, start_date, end_date]
    box_metrics += [round(key_metrics[j][portfolio_name], 1) for j in range(4)]
    box_metrics += [
        anda.best_year_no(strategy_object),
        anda.worst_year_no(strategy_object),
    ]
    return box_metrics


def hidden_divs_data(no_portfolios):
    """
    As Dash does not allow dynamically registered callbacks,
    we need to return values for the hidden divs,
    ie for the number of portfolios left empty

    Corresponds to:
        - Box Visibility
        - Portfolio Name
        - Start Date
        - End Date
        - Initial Balance
        - End Balance
        - Best Year %
        - Worst Year %
        - Best Year
        - Worst Year
        - Annual Differences Graph
        - Pie Chart
        - Pie Chart Visibility
        - Drawdowns Table Name: None required
        - Drawdowns Table Data: None required
        - Drawdowns Table Visibility
    """
    empty_divs = [{"display": "none"}] * 13
    empty_divs += [
        None,
        None,
        {"display": "none"},
    ]
    return empty_divs * (MAX_PORTFOLIOS - no_portfolios)


def get_figure(xaxis_title, yaxis_title):
    fig = go.Figure()
    fig.update_layout(
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"),
    )
    return fig


def get_trace(x, y, name, color):
    return go.Scattergl(x=x, y=y, mode="lines", name=name, marker_color=color)


def update_dashboard(n_clicks, start_date, end_date, input_money, *args):
    """
    Based on selected tickers and assets update the whole dashapp.
    *args is for all the specific portfolio data, which involves:
    - Portfolio Name
    - Contribution Amount
    - Contribution Frequency
    - Rebalancing Frequency
    - Table of Tickers
    The function updates:
    - The Main Portfolio Graph
    - Yearly Returns Table
    - Yearly Returns Graph
    - Dradwons Graph
    - Visibility for Portfolio Data
    - Box of Key Metrics per Portfolio
    - Yearly Differences Graph per Portfolio
    - Pie Charts of Asset Allocations per Portfolio
    - Table of Key Metrics
    - Overfitting Data
    """

    if n_clicks is None:
        raise PreventUpdate

    # Retrieve arguments, as they are combined for Dash
    args = retrieve_args(args)

    no_portfolios = get_no_portfolios(args["Ticker Tables"])

    # Prevent update if no portfolios were given
    values = (start_date, end_date, input_money)
    if not all(values) or no_portfolios == 0:
        raise PreventUpdate

    # Init
    to_return = []
    main_graph = get_figure(xaxis_title="Time", yaxis_title="Total Returns")
    drawdowns_graph = get_figure(xaxis_title="Time", yaxis_title="Drawdown (%)")
    # Yearly Returns parameters
    returns_tab_data = []
    # Metrics parameters
    table_data = []
    table_cols = [{"name": "Metric", "id": "Metric"}]
    # Overfitting parameters
    portfolio_params = []

    if check_date(start_date, end_date):
        raise PreventUpdate

    start_date = format_date(start_date)
    end_date = format_date(end_date)

    for i in range(no_portfolios):
        portfolio_name = args["Portfolio Names"][i]
        contribution_dates = validate_dates(
            start_date, end_date, args["Contribution Frequencies"][i]
        )
        contribution_amount = args["Contribution Amounts"][i] or 0
        rebalancing_dates = validate_dates(
            start_date, end_date, args["Rebalancing Frequencies"][i]
        )
        if args["Ticker Tables"][i] == []:
            raise PreventUpdate

        tickers, proportions, handles = zip(
            *(
                (tkr["AssetTicker"], Decimal(tkr["Allocation"]), tkr.get("Handle"))
                for tkr in args["Ticker Tables"][i]
            )
        )

        if any(tkr["Allocation"] == 0 for tkr in args["Ticker Tables"][i]):
            raise PreventUpdate

        strategy = get_strategy(
            tickers,
            proportions,
            handles,
            start_date,
            end_date,
            Decimal(input_money),
            contribution_amount,
            contribution_dates,
            rebalancing_dates,
        )

        if strategy is None:
            to_return = [None] * 4
            to_return += hidden_divs_data(0)
            to_return += [None] * 3

            # press exceptions
            to_return += [1]
            return to_return

        total_returns = anda.total_return(strategy)
        metrics = get_table_data(strategy, total_returns, portfolio_name)
        table_data = combine_cols(table_data, metrics)
        table_cols.append({"name": portfolio_name, "id": portfolio_name})


        # Store portfolio paramaters for overfitting test
        portfolio_params.append(
            {
                "name": portfolio_name,
                "tickers": tickers,
                "proportions": proportions,
                "input_money": input_money,
                "contribution_amount": contribution_amount,
                "contribution_dates": args["Contribution Frequencies"][i],
                "rebalancing_dates": args["Rebalancing Frequencies"][i],
                "sharpe": metrics[-1],
                "sortino": metrics[-2],
                "has_user_uploaded":any(tkr.get("Handle") for tkr in args["Ticker Tables"][i]),
            }
        )

        # Add Portfolio Trace to Main Graph
        main_graph.add_trace(
            get_trace(
                total_returns.index,
                total_returns,
                name=str(portfolio_name),
                color=OFFICIAL_COLOURS[i],
            )
        )

        # Visibility
        to_return.append({"display": "block"})

        # Box of Metrics
        to_return += get_box_of_metrics(portfolio_name, strategy, table_data)

        # Yearly Differences Graph
        annual_figure = get_yearly_differences_graph(
            portfolio_name,
            anda.relative_yearly_returns(strategy),
            strategy.dates[0],
            strategy.dates[-1],
        )

        to_return.append(annual_figure)

        returns_tab_data.append(
            [anda.relative_yearly_returns(strategy), portfolio_name, total_returns],
        )

        # Pie Charts
        to_return += get_pie_charts(tickers, proportions)

        # Drawdowns Table
        drawdowns = anda.drawdowns(total_returns)
        to_return += get_drawdowns_tables(portfolio_name, drawdowns)

        # Add trace to Drawdowns Graph
        drawdowns_graph.add_trace(
            get_trace(
                drawdowns.index,
                drawdowns,
                name=str(portfolio_name),
                color=OFFICIAL_COLOURS[i],
            )
        )

    # Data for the hidden divs
    to_return += hidden_divs_data(no_portfolios)
    # Returns tab
    returns_table = update_table(returns_tab_data, no_portfolios)
    annual_returns = portfolios_figure(returns_tab_data, no_portfolios)

    to_return = [main_graph, returns_table, annual_returns, drawdowns_graph] + to_return
    to_return += [table_cols, table_data, portfolio_params]

    # no exception
    to_return += [None]
    return to_return
