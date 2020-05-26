import dash_html_components as html
import dash_core_components as dcc

from .elements import graph_box


def dates_container():
    return html.Div(
        html.Div(id="output-dates", className="subtitle",),
        className="column is-12 has-text-right",
        style={"padding-bottom": "0px"},
    )


def annual_returns(id):
    return html.Div(
        [
            html.P("Annual Returns", className="panel-heading"),
            dcc.Loading(
                html.Div(
                    dcc.Graph(
                        id=f"annual-returns-{id}",
                        style={"width": "100%", "height": "400px"},
                    ),
                    className="panel-block",
                )
            ),
        ],
        className="box",
    )


def portfolio_name(id):
    return html.Div(
        html.Div(id=f"box-Portfolio Name-{id}", className="level-item title"),
        className="level",
    )


def level_items(id, name1, name2, units=""):
    return html.Div(
        [box_item(name1, id, unit=units), box_item(name2, id, unit=units)],
        className="level",
    )


def metrics_box(id, visibility, size):
    return html.Div(
        [
            html.Div(
                dcc.Loading(
                    [
                        portfolio_name(id),
                        html.Hr(),
                        level_items(id, "Start Date", "End Date"),
                        level_items(
                            id, "Initial Investment", "Final Balance", units="$"
                        ),
                        level_items(id, "Best Year", "Worst Year"),
                        level_items(
                            id,
                            "Difference in Best Year",
                            "Difference in Worst Year",
                            units="%",
                        ),
                    ]
                ),
                className="box",
                style={"background-color": "#efeae2 "},
            ),
            annual_returns(id),
        ],
        className=f"column is-{size} has-text-vcentered",
        style={"display": str(visibility)},
        id=f"metrics-box-{id}",
    )


def box_item(metric_name, id, unit=""):
    return html.Div(
        [
            html.Div(
                f"{metric_name}: ",
                className="title is-5",
                style={"padding-right": "1cm"},
            ),
            html.Div(id=f"box-{metric_name}-{id}", className="title is-5",),
            html.Div(unit),
        ],
        className="level-item",
    )


def portfolio_summary(id, reverse_layout=False):
    elements = [
        metrics_box(id, visibility="none", size=7),
        graph_box(
            "Asset Allocations",
            id=f"pie-{id}",
            size=5,
            visibility="none",
            height="650px",
        ),
    ]
    if reverse_layout:
        elements.reverse()

    return html.Div([html.Div(elements, className="columns")], className="column is-12")


def summary_dashboard():
    return html.Div(
        [
            dates_container(),
            graph_box(
                "Total Returns over Time",
                id="main-graph",
                size=12,
                visibility="block",
                height="600px",
            ),
            portfolio_summary(id=1),
            portfolio_summary(id=2, reverse_layout=True),
            portfolio_summary(id=3),
            portfolio_summary(id=4, reverse_layout=True),
            portfolio_summary(id=5),
        ],
        className="columns is-multiline",
    )
