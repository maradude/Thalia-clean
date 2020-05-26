import dash_html_components as html
import dash_core_components as dcc


def graph_box(graph_name, visibility, id, height, size=6, figure={}):
    """
    Generic and resizable box that can take a go.Figure as input
    """
    return html.Div(
        html.Div(
            [
                html.P(graph_name, className="panel-heading"),
                dcc.Loading(
                    html.Div(
                        dcc.Graph(
                            figure=figure,
                            id=id,
                            style={"width": "100%", "height": "100%"},
                        ),
                        style={"width": "100%", "height": height},
                        className="panel-block",
                    )
                ),
            ],
            className="box",
            style={"width": "100%", "height": "100%"},
        ),
        className=f"column is-{size}",
        id=f"graph-box-{id}",
        style={"display": str(visibility)},
    )
