import dash_html_components as html
import dash_core_components as dcc


def dates_container():
    return html.Div(
        html.Div(id="output-date", className="subtitle",),
        className="column is-12 has-text-right",
        style={"padding-bottom": "0px"},
    )


def returns_table(id):

    return html.Div(
        [
            html.P("Annual Returns", className="panel-heading"),
            html.Hr(),
            dcc.Loading(html.Div([html.Div(id=f"return-table")]),),
        ],
        className="box",
    )


def returns_graph(id):

    return html.Div(
        [
            html.P("Annual Returns", className="panel-heading"),
            dcc.Loading(
                html.Div(
                    dcc.Graph(
                        id=f"annual-returns-portfolios",
                        style={"width": "100%", "height": "500px"},
                    ),
                    className="panel-block",
                ),
            ),
        ],
        className="box",
    )


def returns_dashboard():
    return html.Div([dates_container(), returns_graph(id=1), returns_table(id=1)])
