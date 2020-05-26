import dash_html_components as html
import dash_core_components as dcc
import dash_table
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta

from . import lazy_portfolio
from .. import util
from ..config import MAX_PORTFOLIOS, OFFICIAL_COLOURS


def ticker_dropdown(id):
    tickers = util.get_asset_names()

    options = []
    for tkr, name in tickers:
        tkr_name = f"{tkr} – {name}"
        options.append({"value": tkr_name, "label": tkr_name})

    return html.Div(
        [
            html.I("Select an asset"),
            html.Div(
                dcc.Dropdown(
                    id=f"memory-ticker-{id}",
                    options=options,
                    multi=False,
                    className="",
                ),
                className="control",
            ),
        ],
        className="field",
    )


def ticker_table(id):
    return html.Div(
        dash_table.DataTable(
            id=f"memory-table-{id}",
            columns=[
                {"name": "Ticker", "id": "AssetTicker", "type": "text"},
                {"name": "Name", "id": "Name", "type": "text"},
                {
                    "name": "Allocation",
                    "id": "Allocation",
                    "type": "numeric",
                    "editable": True,
                },
                {"name": "Handle", "id": "Handle", "type": "any", "visible": False,},
            ],
            hidden_columns=["Handle"],
            row_deletable=True,
            css=[{"selector": ".show-hide", "rule": "display: none"}],
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "rgb(248, 248, 248)",},
                {
                    "if": {
                        "column_id": "Allocation",
                        "filter_query": "{Allocation} > 100",
                    },
                    "backgroundColor": OFFICIAL_COLOURS[0],
                    "color": "white",
                },
            ],
            style_header={
                "backgroundColor": "rgb(230, 230, 230)",
                "fontWeight": "bold",
            },
            style_cell_conditional=[{"textAlign": "center"}],
        ),
        style={"padding-top": "25px"},
    )


def select_dates():
    today = dt.now().date()
    return html.Div(
        [
            dcc.DatePickerRange(
                id="my-date-picker-range",
                display_format="DD/MM/YYYY",
                max_date_allowed=today,
                start_date=today - relativedelta(years=5),
                end_date=today,
            ),
            html.Div(id="date-picker-range-container"),
        ],
        className="container has-text-centered",
    )


def initial_amount_of_money():
    return html.Div(
        [
            html.I("Initial Amount in $"),
            html.Br(),
            dcc.Input(
                id="input-money",
                min=1,
                placeholder="Insert Initial amount of $",
                type="number",
                className="input",
                value=1000,
            ),
            html.Div(id="output-money"),
        ]
    )


def contribution_amount(id):
    return html.Div(
        [
            html.I("Contribution Amount in $"),
            html.Br(),
            dcc.Input(
                id=f"input-contribution-{id}",
                placeholder="Insert contribution amount of $",
                type="number",
                className="input",
            ),
            html.Div(id=f"output-contribution-{id}"),
        ]
    )


def contribution_dates(id):
    return html.Div(
        [
            html.I("Contribution Frequency"),
            html.Br(),
            dcc.Dropdown(
                id=f"contribution-dropdown-{id}",
                options=[  # Business month END
                    {"label": "None", "value": "None"},
                    {"label": "Monthly", "value": "BM"},
                    {"label": "Quarterly", "value": "BQ"},
                    {"label": "Annually", "value": "BA"},
                    {"label": "Semi-Annually", "value": "6BM"},
                ],
            ),
            html.Div(id=f"output-contribution-dpp-{id}"),
        ]
    )


def rebalancing_dates(id):
    return html.Div(
        [
            html.I("Rebalancing Frequency"),
            html.Br(),
            dcc.Dropdown(
                id=f"rebalancing-dropdown-{id}",
                options=[  # Business month END
                    {"label": "None", "value": "None"},
                    {"label": "Monthly", "value": "BM"},
                    {"label": "Quarterly", "value": "BQ"},
                    {"label": "Annually", "value": "BA"},
                    {"label": "Semi-Annually", "value": "6BM"},
                ],
            ),
            html.Div(id=f"output-rebalancing-{id}"),
        ]
    )


def lazy_portfolios(id):
    return html.Div(
        [
            html.I("Feeling lazy?"),
            html.Div(
                dcc.Dropdown(
                    id=f"lazy-portfolios-{id}",
                    placeholder="Lazy Portfolio",
                    className="has-text-left",
                    options=lazy_portfolio.lazy_portfolio_options,
                ),
                className="control",
            ),
        ],
        className="field",
    )


def portfolio_name(id):
    return html.Div(
        [
            html.Label(
                html.Div(className="fas fa-pen fa-2x"),
                htmlFor=f"portfolio-name-{id}",
                style={"float": "right"},
            ),
            dcc.Input(
                placeholder=f"Portfolio {id}",
                type="text",
                value=f"Portfolio {id}",
                style={
                    "border-width": "0px",
                    "color": "#363636",
                    "font-size": "2rem",
                    "height": "2.5rem",
                    "font-weight": "600",
                    "line-height": "1.125",
                    # "padding-bottom": "0.5cm"
                },
                id=f"portfolio-name-{id}",
                # className="input"
            ),
        ],
        className="column is-5 has-text-left",
        style={"height": "4rem"},
    )


def save_portfolio_button(id):
    return html.Div(
        [
            html.Div(id=f"save-portfolio-success-{id}"),
            html.Button(
                "Save portfolio", id=f"save-portfolio-{id}", className="button"
            ),
        ],
        className="has-text-centered",
        style={"padding-top": "10px"},
    )


def stored_portfolios_dropdown(id):
    return html.Div(
        [
            html.I("Or want to select from your previous portfolios?"),
            html.Div(
                dcc.Dropdown(
                    id=f"stored-portfolios-{id}",
                    placeholder="Saved portfolios",
                    className="has-text-left",
                ),
                className="control",
            ),
        ],
        className="field",
    )


def options(id, visibility):
    return html.Div(
        [
            html.Div(
                [
                    portfolio_name(id),
                    html.Div(contribution_amount(id), className="column is-12"),
                    html.Div(contribution_dates(id), className="column is-12"),
                    html.Div(rebalancing_dates(id), className="column is-12"),
                    html.Div(html.Hr(), className="column is-12"),
                    html.Div(
                        html.Div(
                            [
                                html.Div(
                                    [
                                        ticker_dropdown(id),
                                        upload_data(id),
                                        html.Hr(style={"background-color": "grey"}),
                                        lazy_portfolios(id),
                                        stored_portfolios_dropdown(id),
                                        save_portfolio_button(id),
                                    ],
                                    className="column is-4",
                                ),
                                html.Div([ticker_table(id),], className="column is-8"),
                            ],
                            className="columns",
                        ),
                        className="column is-12",
                    ),
                ],
                className="columns is-multiline",
            )
        ],
        className="box",
        id=f"portfolio-{id}",
        style={"display": f"{visibility}"},
    )


def submit_button():
    return html.Div(
        html.Button(
            "Submit",
            "submit-btn",
            className="button is-large is-primary",
            style={"background-color": OFFICIAL_COLOURS[0]},
        ),
        className="container has-text-centered",
    )


def add_portfolio_button():
    return html.Div(
        html.Button(
            "Add Portfolio",
            "add-portfolio-btn",
            className="button is-medium",
            style={
                "border": "0px",
                "color": OFFICIAL_COLOURS[0],
                "background-color": "transparent",
            },
        )
    )


def upload_data(id):
    return html.Div(
        [
            html.Div(
                [
                    "Upload your own ticker: ",
                    html.Abbr(
                        title=(
                            "Please provide a CSV following the rules below:\n"
                            "- The top of the file includes the columns:\n"
                            "  Date, Open, High, Low, Close\n"
                            "- Dates should be in the format of DD/MM/YYYY\n"
                            "- The csv file should have at least 1 year of data\n\n"
                            "Example of the format below:\n"
                            "Date,Open,High,Low,Close\n"
                            "13/03/1986,100,105,99,103\n"
                            "14/03/1986,103,106,103,103\n"
                        ),
                        className="fa fa-question-circle",
                    ),
                ],
                className="has-text-centered",
                style={"margin": "10px"},
            ),
            dcc.Upload(
                id=f"upload-data-{id}",
                children=html.Div(
                    [
                        "Drag and Drop or ",
                        html.A("Select Files ", style={"color": OFFICIAL_COLOURS[0]}),
                    ]
                ),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                },
            ),
        ]
    )


def warning_message(id, message):
    return html.Div(
        [dcc.ConfirmDialog(id=id, message=message), html.Div(id=f"output-{id}")]
    )


def options_wrapper():
    missing_params_warning_msg = (
        "Please make sure you have selected a start date, an "
        "end date, initial amount and at least one ticker for "
        "the first portfolio!"
    )
    zero_allocation_msg = "Please make sure that allocation is not zero for any ticker!"
    short_timerange_msg = "You need at least one full calendar year (Jan. 1 to Jan. 1)."
    csv_format_msg = (
        "The format you input is not compatible, please enter a csv with columns: "
        "Date,Open,High,Low,Close\n in this format: 13/03/1986,100,105,99,103\n"
    )
    csv_date_msg = (
        "Please enter a csv with at least one full calendar year (Jan. 1 to Jan. 1)."
    )
    timeframe_overlap_msg = (
        "The dates for the selected ticker do not exist for the selected timeframe!"
    )

    allocation_messages = (
        warning_message(f"confirm-allocation-{i}", zero_allocation_msg)
        for i in range(1, MAX_PORTFOLIOS + 1)
    )
    csv_messages = (
        warning_message(f"confirm-csv-{i}", csv_format_msg)
        for i in range(1, MAX_PORTFOLIOS + 1)
    )
    csv_date_messages = (
        warning_message(f"confirm-csv-date-{i}", csv_date_msg)
        for i in range(1, MAX_PORTFOLIOS + 1)
    )

    return html.Div(
        [
            html.Div(
                [html.Div(select_dates()), html.Div(initial_amount_of_money())],
                className="box",
            ),
            html.Div(
                children=[
                    options(1, visibility="block"),
                    options(2, visibility="none"),
                    options(3, visibility="none"),
                    options(4, visibility="none"),
                    options(5, visibility="none"),
                ],
                id="portfolios-container",
            ),
            add_portfolio_button(),
            html.Br(),
            submit_button(),
            warning_message("confirm-1", missing_params_warning_msg),
            *allocation_messages,
            warning_message("confirm-date", short_timerange_msg),
            warning_message("timeframe_bug", timeframe_overlap_msg),
            *csv_messages,
            *csv_date_messages,
            html.Div(html.Button(id="exceptions-btn"), style={"display": "none"}),
        ],
        id="portfolios-main",
    )
