import dash_core_components as dcc
import dash_html_components as html

from . import tabs


layout = html.Div(
    html.Main(
        [
            dcc.Location(id="page-location-url", refresh=False),
            html.Div(
                [
                    dcc.Tabs(
                        [
                            tabs.allocations(),
                            tabs.summary(),
                            tabs.metrics(),
                            tabs.returns(),
                            tabs.drawdowns(),
                            tabs.assets(),
                            tabs.overfitting(),
                        ],
                        id="tabs",
                        value="allocations",
                    ),
                ],
                className="column",
            ),
        ],
        className="columns",
    ),
    className="section",
)
