from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from .summary import get_pie_charts
from ..tab_elements.elements import graph_box
from ..config import MAX_PORTFOLIOS
from ..tab_elements.assets import asset_contributions_table_element
from ..util import get_assets


def register_assets_tab(dashapp):
    register_asset_contributions(dashapp)


def register_asset_contributions(dashapp):
    states = []
    for i in range(1, MAX_PORTFOLIOS + 1):
        states += [
            State(f"memory-table-{i}", "data"),
            State(f"portfolio-name-{i}", "value"),
        ]
    dashapp.callback(
        Output(f"assets-container", "children"),
        [Input("submit-btn", "n_clicks")],
        states,
    )(asset_contributions)


def asset_contributions(n_clicks, *args):
    """
    Input:
    - Submit button clicks
    - Ticker Table data: even of args
    - Corresponding Portfolio Name: odd of args

    Output:
    - Div Children: Portfolio Name, Table of Assets, Pie Chart of Cactegories
    """
    if n_clicks is None:
        raise PreventUpdate

    table_data = args[0::2]
    portfolio_names = args[1::2]
    if None in table_data:
        no_portfolios = table_data.index(None)
    else:
        no_portfolios = MAX_PORTFOLIOS

    assets = get_assets()
    for i in range(len(table_data)):
        if table_data[i] is not None:
            for j in range(len(table_data[i])):
                ticker = table_data[i][j]["AssetTicker"]
                if "csv" in table_data[i][j]["AssetTicker"]:
                    category = "user supplied csv"
                else:
                    category = assets[assets.index == ticker]["AssetClassName"].values[
                        0
                    ]

                table_data[i][j]["Category"] = category.replace("_", " ").title()

    ret = []
    for i in range(no_portfolios):
        proportions = {}
        for row in table_data[i]:
            if row["Category"] in proportions:
                proportions[row["Category"]] += row["Allocation"]
            else:
                proportions[row["Category"]] = row["Allocation"]

        fig = get_pie_charts(list(proportions.keys()), list(proportions.values()))[0]
        ret += [
            asset_contributions_table_element(
                portfolio_names[i],
                i,
                table_data[i],
                graph_box(
                    graph_name=f"Proportions per Category for {portfolio_names[i]}",
                    visibility="block",
                    id=f"categories-pie-{i}",
                    height="650px",
                    size=5,
                    figure=fig,
                ),
                reverse_layout=(i % 2 == 0),
            )
        ]

    return ret
